from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

class Client(Base):
    """
    The Central Anchor for the entire ecosystem.
    Manages identity, billing, and platform access for each tenant.
    """
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    
    # Global Identity
    global_tenant_id = Column(String, unique=True, index=True) # Unique ID shared across all platforms
    
    # Mercado Pago Credentials (The Billing Layer)
    access_token = Column(String, nullable=False)
    public_key = Column(String)
    client_id = Column(String)
    client_secret = Column(String)
    webhook_secret = Column(String)
    
    # Platform Activation Flags
    has_whatsapp_hub = Column(Integer, default=0) # 0: Disabled, 1: Enabled
    has_stock_pro = Column(Integer, default=0)    # 0: Disabled, 1: Enabled
    account_status = Column(String, default="active") # active, suspended, pending
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    payments = relationship("Payment", back_populates="client")
    subscriptions = relationship("Subscription", back_populates="client")

class Payment(Base):
    """
    Records payment attempts and statuses for a specific client.
    """
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    
    # Mercado Pago Reference
    preference_id = Column(String, index=True, unique=True)
    init_point = Column(String)
    payment_id = Column(String, index=True)
    
    amount = Column(Float, nullable=False)
    currency = Column(String, default="ARS")
    status = Column(String, default="pending") # pending, approved, rejected

    
    description = Column(String)
    payer_email = Column(String)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    client = relationship("Client", back_populates="payments")

class Subscription(Base):
    """
    Represents a recurring payment plan (Subscription) created for a client.
    """
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    
    # Mercado Pago Reference
    subscription_id = Column(String, index=True, unique=True)
    plan_id = Column(String)
    
    amount = Column(Float, nullable=False)
    frequency = Column(String, default="monthly") # monthly, yearly
    status = Column(String, default="active") # active, paused, cancelled
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    client = relationship("Client", back_populates="subscriptions")

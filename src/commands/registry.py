from typing import Dict, Type
from src.commands.base import BaseCommand
from src.commands.client_cmds.create_client import CreateClientCommand
from src.commands.client_cmds.list_clients import ListClientsCommand
from src.commands.client_cmds.provision_client import ProvisionClientCommand
from src.commands.client_cmds.update_client_status import UpdateClientStatusCommand
from src.commands.client_cmds.update_client import UpdateClientCommand
from src.commands.payment_cmds.create_payment import CreatePaymentCommand
from src.commands.payment_cmds.list_payments import ListPaymentsCommand
from src.commands.payment_cmds.list_all_payments import ListAllPaymentsCommand
from src.commands.payment_cmds.update_payment_status import UpdatePaymentStatusCommand
from src.commands.payment_cmds.list_subscriptions import ListSubscriptionsCommand
from src.commands.payment_cmds.create_subscription import CreateSubscriptionCommand

class CommandRegistry:
    """
    A registry to map command names to their respective classes.
    This allows the interfaces (API, CLI) to call commands dynamically.
    """
    _commands: Dict[str, Type[BaseCommand]] = {}

    @classmethod
    def register(cls, name: str, command_class: Type[BaseCommand]):
        """
        Registers a command class with a specific name.
        """
        cls._commands[name] = command_class

    @classmethod
    def get_command(cls, name: str) -> BaseCommand:
        """
        Retrieves and instantiates a command by its name.
        """
        command_class = cls._commands.get(name)
        if not command_class:
            raise ValueError(f"Command '{name}' not found in registry.")
        return command_class()

    @classmethod
    def list_commands(cls) -> list[str]:
        """
        Returns a list of all registered command names.
        """
        return list(cls._commands.keys())

# Registration of all commands
CommandRegistry.register("client:create", CreateClientCommand)
CommandRegistry.register("client:list", ListClientsCommand)
CommandRegistry.register("client:provision", ProvisionClientCommand)
CommandRegistry.register("client:update_status", UpdateClientStatusCommand)
CommandRegistry.register("client:update", UpdateClientCommand)
CommandRegistry.register("payment:create", CreatePaymentCommand)
CommandRegistry.register("payment:list", ListPaymentsCommand)
CommandRegistry.register("payment:all", ListAllPaymentsCommand)
CommandRegistry.register("payment:update_status", UpdatePaymentStatusCommand)
CommandRegistry.register("subscription:list", ListSubscriptionsCommand)
CommandRegistry.register("subscription:create", CreateSubscriptionCommand)

# License Management Commands (Master Control Plane)
from src.commands.license_cmds.license_cmds import GrantLicenseCommand, RevokeLicenseCommand, AuditLicenseCommand
CommandRegistry.register("license:grant", GrantLicenseCommand)
CommandRegistry.register("license:revoke", RevokeLicenseCommand)
CommandRegistry.register("license:audit", AuditLicenseCommand)


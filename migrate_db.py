import sqlite3

def migrate():
    try:
        conn = sqlite3.connect('payment_gateway.db')
        cursor = conn.cursor()
        cursor.execute('ALTER TABLE payments ADD COLUMN init_point TEXT')
        conn.commit()
        conn.close()
        print("Columna init_point añadida con éxito.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("La columna init_point ya existe.")
        else:
            print(f"Error de migración: {e}")

if __name__ == '__main__':
    migrate()

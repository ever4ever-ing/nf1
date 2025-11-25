import mysql.connector
import sys

# Conexión a MySQL
try:
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password=input('Ingresa la contraseña de MySQL: '),
        database='nf1'
    )
    cursor = conn.cursor()
    
    # Leer el archivo SQL
    with open('create_competitiva_tables.sql', 'r', encoding='utf-8') as f:
        sql_script = f.read()
    
    # Dividir por CREATE TABLE y ejecutar cada uno
    statements = sql_script.split('CREATE TABLE')
    
    for statement in statements[1:]:  # Saltar el primero que está vacío
        sql = 'CREATE TABLE' + statement.strip()
        if sql.endswith(';'):
            sql = sql[:-1]
        try:
            cursor.execute(sql)
            table_name = sql.split('`')[1]
            print(f'✓ Tabla {table_name} creada exitosamente')
        except mysql.connector.Error as err:
            if err.errno == 1050:  # Table already exists
                table_name = sql.split('`')[1]
                print(f'ℹ Tabla {table_name} ya existe')
            else:
                print(f'✗ Error: {err}')
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print('\n✅ Todas las tablas han sido procesadas exitosamente!')
    
except mysql.connector.Error as err:
    print(f'Error de conexión: {err}')
    sys.exit(1)
except FileNotFoundError:
    print('Error: No se encontró el archivo create_competitiva_tables.sql')
    sys.exit(1)

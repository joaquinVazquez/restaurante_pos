# database/init_db.py
from database.connection import get_connection


def inicializar_bd():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS categorias (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre    TEXT NOT NULL UNIQUE,
            icono     TEXT,
            activo    INTEGER DEFAULT 1,
            creado_en TEXT DEFAULT (DATETIME('now'))
        );

        CREATE TABLE IF NOT EXISTS usuarios (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre        TEXT NOT NULL,
            username      TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            rol           TEXT NOT NULL DEFAULT 'cajero',
            activo        INTEGER DEFAULT 1,
            creado_en     TEXT DEFAULT (DATETIME('now'))
        );

        CREATE TABLE IF NOT EXISTS productos (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre       TEXT NOT NULL,
            descripcion  TEXT,
            precio       REAL NOT NULL,
            stock        INTEGER DEFAULT 0,
            categoria_id INTEGER REFERENCES categorias(id),
            activo       INTEGER DEFAULT 1,
            imagen       TEXT,
            creado_en    TEXT DEFAULT (DATETIME('now'))
        );

        CREATE TABLE IF NOT EXISTS clientes (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre    TEXT NOT NULL,
            telefono  TEXT,
            email     TEXT,
            direccion TEXT,
            notas     TEXT,
            activo    INTEGER DEFAULT 1,
            creado_en TEXT DEFAULT (DATETIME('now'))
        );

        CREATE TABLE IF NOT EXISTS ventas (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id     INTEGER REFERENCES usuarios(id),
            cliente_id     INTEGER REFERENCES clientes(id),
            total          REAL NOT NULL,
            metodo_pago    TEXT,
            monto_recibido REAL,
            cambio         REAL,
            estado         TEXT DEFAULT 'completada',
            creado_en      TEXT DEFAULT (DATETIME('now'))
        );

        CREATE TABLE IF NOT EXISTS detalle_ventas (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            venta_id        INTEGER REFERENCES ventas(id),
            producto_id     INTEGER REFERENCES productos(id),
            cantidad        INTEGER NOT NULL,
            precio_unitario REAL NOT NULL,
            subtotal        REAL
        );

        CREATE TABLE IF NOT EXISTS cortes_caja (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha          TEXT NOT NULL,
            total_ventas   INTEGER DEFAULT 0,
            total_ingresos REAL DEFAULT 0,
            efectivo       REAL DEFAULT 0,
            tarjeta        REAL DEFAULT 0,
            observaciones  TEXT,
            creado_en      TEXT DEFAULT (DATETIME('now'))
        );

        CREATE TABLE IF NOT EXISTS configuracion (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            clave       TEXT NOT NULL UNIQUE,
            valor       TEXT,
            descripcion TEXT
        );
    """)
    conn.commit()

    # Datos iniciales solo si la BD está vacía
    cursor.execute("SELECT COUNT(*) FROM categorias")
    if cursor.fetchone()[0] == 0:
        cursor.executescript("""
            INSERT INTO categorias (nombre, icono) VALUES
                ('Bebidas',        '🥤'),
                ('Antojitos',      '🌮'),
                ('Platos Fuertes', '🍽️'),
                ('Postres',        '🍰'),
                ('Desayunos',      '🍳');

            INSERT INTO usuarios
                (nombre, username, password_hash, rol)
            VALUES
                ('Administrador', 'admin',   'admin123',  'admin'),
                ('Cajero',        'cajero1', 'cajero123', 'cajero');

            INSERT INTO productos
                (nombre, descripcion, precio, stock, categoria_id)
            VALUES
                ('Agua Natural 500ml', 'Agua purificada', 15.00, 100, 1),
                ('Refresco 600ml',     'Coca/Pepsi',      22.00,  80, 1),
                ('Café Americano',     'Café de olla',    25.00,  50, 1),
                ('Taco de Pastor',     'Con piña',        18.00,  60, 2),
                ('Taco de Bistec',     'Con guacamole',   20.00,  60, 2),
                ('Quesadilla',         'Queso Oaxaca',    35.00,  40, 2),
                ('Carne Asada',        'Con arroz',      120.00,  20, 3),
                ('Pollo en Mole',      'Receta casera',   95.00,  15, 3),
                ('Flan Napolitano',    'Con cajeta',      40.00,  25, 4),
                ('Chilaquiles Rojos',  'Con crema',       75.00,  30, 5);

            INSERT INTO configuracion (clave, valor, descripcion) VALUES
                ('restaurante_nombre',    'Mi Restaurante',
                 'Nombre del restaurante'),
                ('restaurante_direccion', 'Dirección aquí',
                 'Dirección'),
                ('restaurante_telefono',  '000-000-0000',
                 'Teléfono'),
                ('ticket_mensaje',
                 '¡Gracias por su compra!',
                 'Mensaje en tickets');
        """)
        conn.commit()

    conn.close()
    print("✅ Base de datos SQLite lista")


if __name__ == "__main__":
    inicializar_bd()

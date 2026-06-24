from database.db_manager import crear_categoria, crear_producto, get_categorias

def poblar_base_de_datos():
    print("Iniciando inyección de datos de prueba...")

    # 1. Crear Categorías base
    print("Creando categorías...")
    crear_categoria({"nombre": "Platos Fuertes", "icono": "restaurant"})
    crear_categoria({"nombre": "Bebidas", "icono": "local_drink"})
    crear_categoria({"nombre": "Postres", "icono": "cake"})

    # 2. Recuperar las categorías generadas para obtener sus IDs generados por Convex
    categorias = get_categorias()
    
    id_platos = next((c["id"] for c in categorias if c["nombre"] == "Platos Fuertes"), None)
    id_bebidas = next((c["id"] for c in categorias if c["nombre"] == "Bebidas"), None)
    id_postres = next((c["id"] for c in categorias if c["nombre"] == "Postres"), None)

    # 3. Crear Productos de prueba usando la estructura de tu db_manager
    print("Creando productos...")
    productos = [
        {
            "nombre": "Hamburguesa Doble", "descripcion": "Con queso y tocino",
            "precio": 120.0, "stock": 50, "categoria_id": id_platos
        },
        {
            "nombre": "Tacos al Pastor (Orden)", "descripcion": "5 piezas con piña",
            "precio": 80.0, "stock": 100, "categoria_id": id_platos
        },
        {
            "nombre": "Refresco de Cola", "descripcion": "600ml lata",
            "precio": 25.0, "stock": 200, "categoria_id": id_bebidas
        },
        {
            "nombre": "Agua de Horchata", "descripcion": "1 Litro",
            "precio": 35.0, "stock": 40, "categoria_id": id_bebidas
        },
        {
            "nombre": "Rebanada Pastel Chocolate", "descripcion": "Receta de la casa",
            "precio": 65.0, "stock": 20, "categoria_id": id_postres
        }
    ]

    for prod in productos:
        crear_producto(prod)
        print(f"Producto inyectado: {prod['nombre']}")

    print("¡Población de datos completada exitosamente!")

if __name__ == "__main__":
    poblar_base_de_datos()
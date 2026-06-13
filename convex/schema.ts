// convex/schema.ts
import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  categorias: defineTable({
    nombre:    v.string(),
    icono:     v.optional(v.string()),
    activo:    v.boolean(),
  }),

  usuarios: defineTable({
    nombre:        v.string(),
    username:      v.string(),
    password_hash: v.string(),
    rol:           v.string(),
    activo:        v.boolean(),
  }),

  productos: defineTable({
    nombre:       v.string(),
    descripcion:  v.optional(v.string()),
    precio:       v.number(),
    stock:        v.number(),
    categoria_id: v.optional(v.string()),
    activo:       v.boolean(),
    imagen:       v.optional(v.string()),
  }),

  clientes: defineTable({
    nombre:    v.string(),
    telefono:  v.optional(v.string()),
    email:     v.optional(v.string()),
    direccion: v.optional(v.string()),
    notas:     v.optional(v.string()),
    activo:    v.boolean(),
  }),

  ventas: defineTable({
    usuario_id:     v.optional(v.string()),
    cliente_id:     v.optional(v.string()),
    total:          v.number(),
    metodo_pago:    v.string(),
    monto_recibido: v.optional(v.number()),
    cambio:         v.optional(v.number()),
    estado:         v.string(),
  }),

  detalle_ventas: defineTable({
    venta_id:       v.string(),
    producto_id:    v.string(),
    cantidad:       v.number(),
    precio_unitario: v.number(),
    subtotal:       v.number(),
  }),

  cortes_caja: defineTable({
    fecha:          v.string(),
    total_ventas:   v.number(),
    total_ingresos: v.number(),
    efectivo:       v.number(),
    tarjeta:        v.number(),
    observaciones:  v.optional(v.string()),
  }),

  configuracion: defineTable({
    clave:       v.string(),
    valor:       v.optional(v.string()),
    descripcion: v.optional(v.string()),
  }),
});
import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  // ── ENTIDAD PRINCIPAL (TENANT) ──
  negocios: defineTable({
    nombre: v.string(),
    rfc: v.optional(v.string()),
    activo: v.boolean(),
  }),

  // ── ADMINISTRACIÓN Y CONFIGURACIÓN ──
  usuarios: defineTable({
    negocio_id: v.id("negocios"),
    nombre: v.string(),
    username: v.string(),
    password: v.string(),
    rol: v.string(),
    activo: v.boolean(),
  }) 
  .index("by_negocio", ["negocio_id"])
  .index("by_username", ["username"]),

  configuracion: defineTable({
    negocio_id: v.id("negocios"),
    nombre_restaurante: v.string(),
    direccion: v.optional(v.string()),
    telefono: v.optional(v.string()),
    email: v.optional(v.string()),
    rfc: v.optional(v.string()),
    mensaje_ticket: v.optional(v.string()),
    logo: v.optional(v.string()),
}).index("by_negocio", ["negocio_id"]),

  config_impresora: defineTable({
    negocio_id: v.id("negocios"),
    nombre_impresora: v.optional(v.string()),
    ancho_papel: v.string(),
    mensaje_ticket: v.optional(v.string()),
  }).index("by_negocio", ["negocio_id"]),

  // ── CATÁLOGO E INVENTARIO ──
  categorias: defineTable({
    negocio_id: v.id("negocios"),
    nombre: v.string(),
    icono: v.optional(v.string()),
    activo: v.boolean(),
  }).index("by_negocio", ["negocio_id"]),

  productos: defineTable({
    negocio_id: v.id("negocios"),
    nombre: v.string(),
    descripcion: v.optional(v.string()),
    precio: v.number(),
    costo: v.optional(v.number()),
    stock: v.number(),
    categoria_id: v.optional(v.id("categorias")),
    imagen: v.optional(v.string()),
    activo: v.boolean(),
  }).index("by_negocio", ["negocio_id"])
    .index("by_categoria", ["categoria_id"]),

  // ── OPERACIÓN COMERCIAL ──
  clientes: defineTable({
    negocio_id: v.id("negocios"),
    nombre: v.string(),
    telefono: v.optional(v.string()),
    email: v.optional(v.string()),
  }).index("by_negocio", ["negocio_id"]),

  ventas: defineTable({
    negocio_id: v.id("negocios"),
    total: v.number(),
    metodo_pago: v.string(),
    monto_recibido: v.optional(v.number()),
    cambio: v.optional(v.number()),
    cliente_id: v.optional(v.id("clientes")),
  }).index("by_negocio", ["negocio_id"]),

  detalle_ventas: defineTable({
    negocio_id: v.id("negocios"),
    venta_id: v.id("ventas"),
    producto_id: v.id("productos"),
    producto_nombre: v.string(),
    cantidad: v.number(),
    precio_unitario: v.number(),
    costo_unitario: v.number(),
    subtotal: v.number(),
    costo_total: v.number(),
    margen_total: v.number(),
  }).index("by_negocio", ["negocio_id"])
    .index("by_venta", ["venta_id"]),

  // ── FLUJO DE CAJA Y CONTROL ──
  cortes_caja: defineTable({
    negocio_id: v.id("negocios"),
    fecha: v.string(),
    fondo_inicial: v.number(),
    total_ventas: v.number(),
    total_ingresos: v.number(),
    diferencia: v.number(),
    observaciones: v.optional(v.string()),
  }).index("by_negocio", ["negocio_id"]),

  gastos: defineTable({
    negocio_id: v.id("negocios"),
    categoria: v.string(),
    descripcion: v.string(),
    monto: v.number(),
    fecha: v.string(),
  }).index("by_negocio", ["negocio_id"]),

  mermas: defineTable({
    negocio_id: v.id("negocios"),
    producto_id: v.id("productos"),
    cantidad: v.number(),
    costo_unitario: v.number(),
    costo_total: v.number(),
    motivo: v.string(),
    fecha: v.string(),
  }).index("by_negocio", ["negocio_id"]),

  entradas_inventario: defineTable({
    negocio_id: v.id("negocios"),
    producto_id: v.id("productos"),
    cantidad: v.number(),
    costo_unitario: v.number(),
    costo_total: v.number(),
    proveedor: v.optional(v.string()),
    fecha: v.string(),
    gasto_id: v.optional(v.id("gastos")),
  }).index("by_negocio", ["negocio_id"])
    .index("by_producto", ["producto_id"]),
})


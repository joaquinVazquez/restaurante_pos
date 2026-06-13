// convex/productos.ts
import { query, mutation } from "./_generated/server";
import { v } from "convex/values";

export const listar = query({
  args: {
    busqueda:     v.optional(v.string()),
    categoria_id: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    let productos = await ctx.db
      .query("productos")
      .filter((q) => q.eq(q.field("activo"), true))
      .collect();

    if (args.categoria_id) {
      productos = productos.filter(
        (p) => p.categoria_id === args.categoria_id
      );
    }

    if (args.busqueda) {
      const b = args.busqueda.toLowerCase();
      productos = productos.filter((p) =>
        p.nombre.toLowerCase().includes(b)
      );
    }

    return productos;
  },
});

export const crear = mutation({
  args: {
    nombre:       v.string(),
    descripcion:  v.optional(v.string()),
    precio:       v.number(),
    stock:        v.number(),
    categoria_id: v.optional(v.string()),
    imagen:       v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("productos", {
      ...args,
      activo: true,
    });
  },
});

export const actualizar = mutation({
  args: {
    id:           v.id("productos"),
    nombre:       v.optional(v.string()),
    descripcion:  v.optional(v.string()),
    precio:       v.optional(v.number()),
    stock:        v.optional(v.number()),
    categoria_id: v.optional(v.string()),
    imagen:       v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    const { id, ...campos } = args;
    return await ctx.db.patch(id, campos);
  },
});

export const desactivar = mutation({
  args: { id: v.id("productos") },
  handler: async (ctx, args) => {
    return await ctx.db.patch(args.id, { activo: false });
  },
});

export const actualizar_stock = mutation({
  args: {
    id:       v.id("productos"),
    cantidad: v.number(),
  },
  handler: async (ctx, args) => {
    const producto = await ctx.db.get(args.id);
    if (!producto) throw new Error("Producto no encontrado");
    return await ctx.db.patch(args.id, {
      stock: producto.stock - args.cantidad,
    });
  },
});
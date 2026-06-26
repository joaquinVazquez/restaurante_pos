import { query, mutation } from "./_generated/server";
import { v } from "convex/values";

export const listar = query({
  args: { 
    negocio_id: v.id("negocios"),
    categoria_id: v.optional(v.id("categorias")),
    busqueda: v.optional(v.string())
  },
  handler: async (ctx, args) => {
    // 1. Filtrar siempre por el tenant (negocio) activo
    let q = ctx.db
      .query("productos")
      .withIndex("by_negocio", (q) => q.eq("negocio_id", args.negocio_id));
      
    let productos = await q.collect();

    // 2. Filtros secundarios en memoria
    if (args.categoria_id) {
      productos = productos.filter(p => p.categoria_id === args.categoria_id);
    }
    if (args.busqueda) {
      const b = args.busqueda.toLowerCase();
      productos = productos.filter(p => p.nombre.toLowerCase().includes(b));
    }
    
    return productos.filter(p => p.activo === true);
  },
});

export const crear = mutation({
  args: {
    negocio_id: v.id("negocios"),
    nombre: v.string(),
    descripcion: v.string(),
    precio: v.number(),
    stock: v.number(),
    categoria_id: v.optional(v.id("categorias")),
    imagen: v.optional(v.string())
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("productos", { ...args, activo: true });
  }
});

export const actualizar = mutation({
  args: {
    negocio_id: v.id("negocios"),
    id: v.id("productos"),
    nombre: v.optional(v.string()),
    descripcion: v.optional(v.string()),
    precio: v.optional(v.number()),
    stock: v.optional(v.number()),
    categoria_id: v.optional(v.id("categorias")),
    imagen: v.optional(v.string())
  },
  handler: async (ctx, args) => {
    const { id, negocio_id, ...updates } = args;
    // Capa de seguridad: verificar que el producto pertenece al negocio
    const producto = await ctx.db.get(id);
    if (!producto || producto.negocio_id !== negocio_id) throw new Error("Acceso denegado");
    
    return await ctx.db.patch(id, updates);
  }
});
import { query, mutation } from "./_generated/server";
import { v } from "convex/values";

export const listar = query({
  args: { 
    negocio_id: v.id("negocios"),
    busqueda: v.optional(v.string())
  },
  handler: async (ctx, args) => {
    let clientes = await ctx.db
      .query("clientes")
      .withIndex("by_negocio", (q) => q.eq("negocio_id", args.negocio_id))
      .collect();

    // Filtro de búsqueda en memoria
    if (args.busqueda) {
      const b = args.busqueda.toLowerCase();
      clientes = clientes.filter(c => c.nombre.toLowerCase().includes(b));
    }
    
    return clientes;
  },
});

export const crear = mutation({
  args: {
    negocio_id: v.id("negocios"),
    nombre: v.string(),
    telefono: v.optional(v.string()),
    email: v.optional(v.string())
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("clientes", args);
  }
});

export const actualizar = mutation({
  args: {
    negocio_id: v.id("negocios"),
    id: v.id("clientes"),
    nombre: v.optional(v.string()),
    telefono: v.optional(v.string()),
    email: v.optional(v.string())
  },
  handler: async (ctx, args) => {
    const { id, negocio_id, ...updates } = args;
    
    // Capa de seguridad: verificar que el cliente pertenece al negocio activo
    const cliente = await ctx.db.get(id);
    if (!cliente || cliente.negocio_id !== negocio_id) {
        throw new Error("Acceso denegado");
    }
    
    return await ctx.db.patch(id, updates);
  }
});

export const eliminar = mutation({
  args: {
    negocio_id: v.id("negocios"),
    id: v.id("clientes")
  },
  handler: async (ctx, args) => {
    // Capa de seguridad: verificar propiedad antes de eliminar
    const cliente = await ctx.db.get(args.id);
    if (!cliente || cliente.negocio_id !== args.negocio_id) {
        throw new Error("Acceso denegado: El cliente no pertenece a este negocio.");
    }
    
    // Eliminación física
    await ctx.db.delete(args.id);
  }
});
import { query, mutation } from "./_generated/server";
import { v } from "convex/values";

export const listar = query({
  args: { negocio_id: v.id("negocios") },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("categorias")
      .withIndex("by_negocio", (q) => q.eq("negocio_id", args.negocio_id))
      .filter((q) => q.eq(q.field("activo"), true))
      .collect();
  },
});

export const crear = mutation({
  args: {
    negocio_id: v.id("negocios"),
    nombre: v.string(),
    icono: v.optional(v.string())
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("categorias", {
      negocio_id: args.negocio_id,
      nombre: args.nombre,
      icono: args.icono,
      activo: true
    });
  }
});
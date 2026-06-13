// convex/categorias.ts
import { query, mutation } from "./_generated/server";
import { v } from "convex/values";

export const listar = query({
  args: {},
  handler: async (ctx) => {
    return await ctx.db
      .query("categorias")
      .filter((q) => q.eq(q.field("activo"), true))
      .collect();
  },
});

export const crear = mutation({
  args: {
    nombre: v.string(),
    icono:  v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("categorias", {
      nombre: args.nombre,
      icono:  args.icono,
      activo: true,
    });
  },
});
import { query, mutation } from "./_generated/server";
import { v } from "convex/values";

export const listar = query({
  args: { 
    negocio_id: v.id("negocios"),
    desde: v.optional(v.string()),
    hasta: v.optional(v.string())
  },
  handler: async (ctx, args) => {
    let cortes = await ctx.db
      .query("cortes_caja")
      .withIndex("by_negocio", (q) => q.eq("negocio_id", args.negocio_id))
      .collect();

    // Filtro por fechas en memoria (Opcional, si envías fechas desde Python)
    if (args.desde && args.hasta) {
      cortes = cortes.filter(c => c.fecha >= args.desde! && c.fecha <= args.hasta!);
    }
    
    return cortes;
  },
});

export const crear = mutation({
  args: {
    negocio_id: v.id("negocios"),
    fecha: v.string(),
    fondo_inicial: v.number(),
    total_ventas: v.number(),
    total_ingresos: v.number(),
    diferencia: v.number(),
    observaciones: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("cortes_caja", args);
  }
});
// convex/cortes_caja.ts
import { query, mutation } from "./_generated/server";
import { v } from "convex/values";

export const listar = query({
  args: {
    desde: v.optional(v.string()),
    hasta: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    let cortes = await ctx.db.query("cortes_caja").order("desc").collect();
    if (args.desde && args.hasta) {
      cortes = cortes.filter(
        (c) => c.fecha >= args.desde! && c.fecha <= args.hasta!
      );
    }
    return cortes.map((c) => ({ id: c._id, ...c }));
  },
});

export const crear = mutation({
  args: {
    fecha: v.string(),
    total_ventas: v.number(),
    total_ingresos: v.number(),
    efectivo: v.number(),
    tarjeta: v.number(),
    observaciones: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("cortes_caja", args);
  },
});

// convex/gastos.ts
import { query, mutation } from "./_generated/server";
import { v } from "convex/values";

export const listar = query({
  args: {
    desde: v.optional(v.string()),
    hasta: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    let gastos = await ctx.db.query("gastos").order("desc").collect();
    if (args.desde && args.hasta) {
      gastos = gastos.filter(
        (g) => g.fecha >= args.desde! && g.fecha <= args.hasta!
      );
    }
    return gastos;
  },
});

export const crear = mutation({
  args: {
    categoria:   v.string(),
    descripcion: v.string(),
    monto:       v.number(),
    fecha:       v.string(),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("gastos", args);
  },
});
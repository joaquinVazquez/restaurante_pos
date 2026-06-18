// convex/mermas.ts
import { query, mutation } from "./_generated/server";
import { v } from "convex/values";

export const listar = query({
  args: {
    desde: v.optional(v.string()),
    hasta: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    let mermas = await ctx.db.query("mermas").order("desc").collect();
    if (args.desde && args.hasta) {
      mermas = mermas.filter(
        (m) => m.fecha >= args.desde! && m.fecha <= args.hasta!
      );
    }
    return mermas;
  },
});

export const crear = mutation({
  args: {
    producto_id: v.string(),
    cantidad:    v.number(),
    motivo:      v.string(),
    fecha:       v.string(),
  },
  handler: async (ctx, args) => {
    const producto = await ctx.db.get(args.producto_id as any);
    const costo = producto?.costo || 0;

    return await ctx.db.insert("mermas", {
      producto_id:     args.producto_id,
      producto_nombre: producto?.nombre || "Desconocido",
      cantidad:        args.cantidad,
      costo_unitario:  costo,
      costo_total:     costo * args.cantidad,
      motivo:          args.motivo,
      fecha:           args.fecha,
    });

    // Descontar stock también
  },
});
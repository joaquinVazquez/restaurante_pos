// convex/mermas.ts
import { query, mutation } from "./_generated/server";
import { v } from "convex/values";

export const listar = query({
  args: {
    negocio_id: v.id("negocios"),
    desde: v.optional(v.string()),
    hasta: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    let mermas = await ctx.db
      .query("mermas")
      .withIndex("by_negocio", (q) => q.eq("negocio_id", args.negocio_id))
      .order("desc")
      .collect();

    if (args.desde && args.hasta) {
      mermas = mermas.filter(
        (m) => m.fecha >= args.desde! && m.fecha <= args.hasta!
      );
    }

    const resultado = [];
    for (const m of mermas) {
      const producto = await ctx.db.get(m.producto_id);
      resultado.push({
        ...m,
        producto_nombre: producto?.nombre || "Producto eliminado",
      });
    }
    return resultado;
  },
});

export const crear = mutation({
  args: {
    negocio_id:  v.id("negocios"),
    producto_id: v.id("productos"),
    cantidad:    v.number(),
    motivo:      v.string(),
    fecha:       v.string(),
  },
  handler: async (ctx, args) => {
    const producto = await ctx.db.get(args.producto_id);
    if (!producto || producto.negocio_id !== args.negocio_id) {
      throw new Error("Producto no encontrado");
    }
    if (producto.stock < args.cantidad) {
      throw new Error(`Stock insuficiente. Disponible: ${producto.stock}`);
    }

    const costo = producto.costo || 0;

    const merma_id = await ctx.db.insert("mermas", {
      negocio_id:      args.negocio_id,
      producto_id:     args.producto_id,
      cantidad:        args.cantidad,
      costo_unitario:  costo,
      costo_total:     costo * args.cantidad,
      motivo:          args.motivo,
      fecha:           args.fecha,
    });

    await ctx.db.patch(args.producto_id, {
      stock: producto.stock - args.cantidad,
    });

    return merma_id;
  },
});
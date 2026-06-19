// convex/ventas.ts
import { query, mutation } from "./_generated/server";
import { v } from "convex/values";

export const listar = query({
  args: {
    desde: v.optional(v.string()),
    hasta: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    let ventas = await ctx.db
      .query("ventas")
      .order("desc")
      .collect();

    if (args.desde && args.hasta) {
      ventas = ventas.filter((v) => {
        const fecha = new Date(v._creationTime)
          .toISOString().split("T")[0];
        return fecha >= args.desde! && fecha <= args.hasta!;
      });
    }

    return ventas;
  },
});

export const crear = mutation({
  args: {
    usuario_id:     v.optional(v.string()),
    cliente_id:     v.optional(v.string()),
    total:          v.number(),
    metodo_pago:    v.string(),
    monto_recibido: v.optional(v.number()),
    cambio:         v.optional(v.number()),
    items: v.array(v.object({
      producto_id:     v.string(),
      cantidad:        v.number(),
      precio_unitario: v.number(),
      subtotal:        v.number(),
    })),
  },
  handler: async (ctx, args) => {
    const { items, ...venta_data } = args;

    const venta_id = await ctx.db.insert("ventas", {
      ...venta_data,
      estado: "completada",
    });

    for (const item of items) {
      const producto = await ctx.db.get(
        item.producto_id as any);
      const costo       = producto?.costo || 0;
      const costo_total = costo * item.cantidad;
      const margen      = item.subtotal - costo_total;

      await ctx.db.insert("detalle_ventas", {
        venta_id:        venta_id,
        producto_id:     item.producto_id,
        producto_nombre: producto?.nombre || "",
        cantidad:        item.cantidad,
        precio_unitario: item.precio_unitario,
        costo_unitario:  costo,
        subtotal:        item.subtotal,
        costo_total:     costo_total,
        margen_total:    margen,
      });

      if (producto) {
        await ctx.db.patch(item.producto_id as any, {
          stock: producto.stock - item.cantidad,
        });
      }
    }

    return venta_id;
  },
});

export const resumen_dia = query({
  args: {},
  handler: async (ctx) => {
    const hoy = new Date();
    hoy.setHours(0, 0, 0, 0);

    const ventas = await ctx.db
      .query("ventas")
      .filter((q) =>
        q.gte(q.field("_creationTime"), hoy.getTime())
      )
      .collect();

    const total    = ventas.reduce(
      (s, v) => s + v.total, 0);
    const efectivo = ventas
      .filter((v) => v.metodo_pago === "efectivo")
      .reduce((s, v) => s + v.total, 0);
    const tarjeta  = ventas
      .filter((v) => v.metodo_pago === "tarjeta")
      .reduce((s, v) => s + v.total, 0);

    return {
      total_ventas: ventas.length,
      total,
      efectivo,
      tarjeta,
    };
  },
});
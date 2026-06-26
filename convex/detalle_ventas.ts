// convex/detalle_ventas.ts
import { query } from "./_generated/server";
import { v } from "convex/values";

export const listar_por_venta = query({
  args: {
    negocio_id: v.id("negocios"),
    venta_id: v.id("ventas"),
  },
  handler: async (ctx, args) => {
    const detalles = await ctx.db
      .query("detalle_ventas")
      .withIndex("by_venta", (q) => q.eq("venta_id", args.venta_id))
      .collect();

    // Verificación de seguridad: que la venta pertenezca al negocio activo
    return detalles.filter((d) => d.negocio_id === args.negocio_id);
  },
});

export const costo_total_periodo = query({
  args: {
    negocio_id: v.id("negocios"),
    venta_ids: v.array(v.id("ventas")),
  },
  handler: async (ctx, args) => {
    let total = 0;
    for (const venta_id of args.venta_ids) {
      const detalles = await ctx.db
        .query("detalle_ventas")
        .withIndex("by_venta", (q) => q.eq("venta_id", venta_id))
        .collect();
      for (const d of detalles) {
        if (d.negocio_id === args.negocio_id) {
          total += d.costo_total;
        }
      }
    }
    return total;
  },
});

export const productos_mas_vendidos = query({
  args: {
    negocio_id: v.id("negocios"),
    venta_ids: v.array(v.id("ventas")),
  },
  handler: async (ctx, args) => {
    const acumulado: Record<string, {
      producto_id: string;
      producto_nombre: string;
      cantidad: number;
      ingresos: number;
    }> = {};

    for (const venta_id of args.venta_ids) {
      const detalles = await ctx.db
        .query("detalle_ventas")
        .withIndex("by_venta", (q) => q.eq("venta_id", venta_id))
        .collect();

      for (const d of detalles) {
        if (d.negocio_id !== args.negocio_id) continue;
        const key = d.producto_id;
        if (!acumulado[key]) {
          acumulado[key] = {
            producto_id: key,
            producto_nombre: d.producto_nombre,
            cantidad: 0,
            ingresos: 0,
          };
        }
        acumulado[key].cantidad += d.cantidad;
        acumulado[key].ingresos += d.subtotal;
      }
    }

    return Object.values(acumulado).sort((a, b) => b.cantidad - a.cantidad);
  },
});
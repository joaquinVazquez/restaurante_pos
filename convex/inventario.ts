// convex/inventario.ts
import { query, mutation } from "./_generated/server";
import { v } from "convex/values";

export const listar = query({
  args: {
    negocio_id: v.id("negocios"),
    desde: v.optional(v.string()),
    hasta: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    let entradas = await ctx.db
      .query("entradas_inventario")
      .withIndex("by_negocio", (q) => q.eq("negocio_id", args.negocio_id))
      .order("desc")
      .collect();

    if (args.desde && args.hasta) {
      entradas = entradas.filter(
        (e) => e.fecha >= args.desde! && e.fecha <= args.hasta!
      );
    }

    const resultado = [];
    for (const e of entradas) {
      const producto = await ctx.db.get(e.producto_id);
      resultado.push({
        ...e,
        producto_nombre: producto?.nombre || "Producto eliminado",
      });
    }
    return resultado;
  },
});

export const crear = mutation({
  args: {
    negocio_id: v.id("negocios"),
    producto_id: v.id("productos"),
    cantidad: v.number(),
    costo_unitario: v.number(),
    proveedor: v.optional(v.string()),
    fecha: v.string(),
    actualizar_costo_producto: v.optional(v.boolean()),
  },
  handler: async (ctx, args) => {
    const producto = await ctx.db.get(args.producto_id);
    if (!producto || producto.negocio_id !== args.negocio_id) {
      throw new Error("Producto no encontrado");
    }
    if (args.cantidad <= 0) {
      throw new Error("La cantidad debe ser mayor a cero");
    }

    const costo_total = args.costo_unitario * args.cantidad;

    // 1. Crear el gasto vinculado
    const gasto_id = await ctx.db.insert("gastos", {
      negocio_id: args.negocio_id,
      categoria: "Insumos",
      descripcion: `Compra: ${producto.nombre} x${args.cantidad}` +
        (args.proveedor ? ` (${args.proveedor})` : ""),
      monto: costo_total,
      fecha: args.fecha,
    });

    // 2. Registrar la entrada de inventario
    const entrada_id = await ctx.db.insert("entradas_inventario", {
      negocio_id: args.negocio_id,
      producto_id: args.producto_id,
      cantidad: args.cantidad,
      costo_unitario: args.costo_unitario,
      costo_total,
      proveedor: args.proveedor,
      fecha: args.fecha,
      gasto_id,
    });

    // 3. Aumentar el stock (y opcionalmente actualizar el costo del producto)
    const updates: { stock: number; costo?: number } = {
      stock: producto.stock + args.cantidad,
    };
    if (args.actualizar_costo_producto) {
      updates.costo = args.costo_unitario;
    }
    await ctx.db.patch(args.producto_id, updates);

    return entrada_id;
  },
});
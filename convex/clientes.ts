// convex/clientes.ts
import { query, mutation } from "./_generated/server";
import { v } from "convex/values";

export const listar = query({
  args: {
    busqueda: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    let clientes = await ctx.db
      .query("clientes")
      .filter((q) => q.eq(q.field("activo"), true))
      .collect();

    if (args.busqueda) {
      const b = args.busqueda.toLowerCase();
      clientes = clientes.filter((c) =>
        c.nombre.toLowerCase().includes(b) ||
        (c.telefono || "").toLowerCase().includes(b) ||
        (c.email || "").toLowerCase().includes(b)
      );
    }

    return clientes;
  },
});

export const crear = mutation({
  args: {
    nombre: v.string(),
    telefono: v.optional(v.string()),
    email: v.optional(v.string()),
    direccion: v.optional(v.string()),
    notas: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("clientes", {
      ...args,
      activo: true,
    });
  },
});

export const actualizar = mutation({
  args: {
    id: v.id("clientes"),
    nombre: v.optional(v.string()),
    telefono: v.optional(v.string()),
    email: v.optional(v.string()),
    direccion: v.optional(v.string()),
    notas: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    const { id, ...campos } = args;
    return await ctx.db.patch(id, campos);
  },
});

export const desactivar = mutation({
  args: { id: v.id("clientes") },
  handler: async (ctx, args) => {
    return await ctx.db.patch(args.id, { activo: false });
  },
});

export const historial = query({
  args: {
    cliente_id: v.id("clientes"),
  },
  handler: async (ctx, args) => {
    const ventas = await ctx.db
      .query("ventas")
      .filter((q) => q.eq(q.field("cliente_id"), args.cliente_id))
      .order("desc")
      .collect();

    const salida = [];
    for (const venta of ventas) {
      const detalles = await ctx.db
        .query("detalle_ventas")
        .filter((q) => q.eq(q.field("venta_id"), venta._id))
        .collect();

      salida.push({
        id: venta._id,
        creado_en: new Date(venta._creationTime).toISOString(),
        total: venta.total,
        metodo_pago: venta.metodo_pago,
        productos: detalles.length,
      });
    }

    return salida;
  },
});

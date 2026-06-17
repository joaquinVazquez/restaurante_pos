// convex/configuracion.ts
import { query, mutation } from "./_generated/server";
import { v } from "convex/values";

export const listar = query({
  args: {},
  handler: async (ctx) => {
    return await ctx.db.query("configuracion").collect();
  },
});

export const guardar = mutation({
  args: {
    clave: v.string(),
    valor: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    const existe = await ctx.db
      .query("configuracion")
      .filter((q) => q.eq(q.field("clave"), args.clave))
      .first();

    if (existe) {
      return await ctx.db.patch(existe._id, { valor: args.valor });
    } else {
      return await ctx.db.insert("configuracion", {
        clave: args.clave,
        valor: args.valor,
      });
    }
  },
});
export const cambiar_password = mutation({
  args: {
    id:            v.id("usuarios"),
    password_hash: v.string(),
  },
  handler: async (ctx, args) => {
    return await ctx.db.patch(args.id, {
      password_hash: args.password_hash
    });
  },
});

export const toggle_activo = mutation({
  args: {
    id:     v.id("usuarios"),
    activo: v.boolean(),
  },
  handler: async (ctx, args) => {
    return await ctx.db.patch(args.id, { activo: args.activo });
  },
});
export const actualizar = mutation({
  args: {
    id:     v.id("categorias"),
    nombre: v.optional(v.string()),
    icono:  v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    const { id, ...campos } = args;
    return await ctx.db.patch(id, campos);
  },
});

export const eliminar = mutation({
  args: { id: v.id("categorias") },
  handler: async (ctx, args) => {
    return await ctx.db.patch(args.id, { activo: false });
  },
});
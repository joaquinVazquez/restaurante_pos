// convex/configuracion.ts
import { query, mutation } from "./_generated/server";
import { v } from "convex/values";

// ── Configuración del restaurante ───────────────────────
export const listar = query({
  args: { negocio_id: v.id("negocios") },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("configuracion")
      .withIndex("by_negocio", (q) => q.eq("negocio_id", args.negocio_id))
      .first();
  },
});

export const guardar = mutation({
  args: {
    negocio_id: v.id("negocios"),
    nombre_restaurante: v.optional(v.string()),
    direccion: v.optional(v.string()),
    telefono: v.optional(v.string()),
    email: v.optional(v.string()),
    rfc: v.optional(v.string()),
    mensaje_ticket: v.optional(v.string()),
    logo: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    const { negocio_id, ...campos } = args;
    const existe = await ctx.db
      .query("configuracion")
      .withIndex("by_negocio", (q) => q.eq("negocio_id", negocio_id))
      .first();

    if (existe) {
      return await ctx.db.patch(existe._id, campos);
    } else {
      return await ctx.db.insert("configuracion", {
        negocio_id,
        nombre_restaurante: campos.nombre_restaurante || "Mi Restaurante",
        ...campos,
      });
    }
  },
});

// ── Configuración de impresora ──────────────────────────
export const listar_impresora = query({
  args: { negocio_id: v.id("negocios") },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("config_impresora")
      .withIndex("by_negocio", (q) => q.eq("negocio_id", args.negocio_id))
      .first();
  },
});

export const guardar_impresora = mutation({
  args: {
    negocio_id: v.id("negocios"),
    nombre_impresora: v.optional(v.string()),
    ancho_papel: v.string(),
    mensaje_ticket: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    const { negocio_id, ...campos } = args;
    const existe = await ctx.db
      .query("config_impresora")
      .withIndex("by_negocio", (q) => q.eq("negocio_id", negocio_id))
      .first();

    if (existe) {
      return await ctx.db.patch(existe._id, campos);
    } else {
      return await ctx.db.insert("config_impresora", {
        negocio_id,
        ...campos,
      });
    }
  },
});

// ── Usuarios ─────────────────────────────────────────────
export const listar_usuarios = query({
  args: { negocio_id: v.id("negocios") },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("usuarios")
      .withIndex("by_negocio", (q) => q.eq("negocio_id", args.negocio_id))
      .collect();
  },
});

export const crear_usuario = mutation({
  args: {
    negocio_id: v.id("negocios"),
    nombre: v.string(),
    username: v.string(),
    password: v.string(),
    rol: v.string(),
  },
  handler: async (ctx, args) => {
    const existe = await ctx.db
      .query("usuarios")
      .withIndex("by_username", (q) => q.eq("username", args.username))
      .first();
    if (existe) {
      throw new Error("El nombre de usuario ya está registrado.");
    }
    return await ctx.db.insert("usuarios", {
      ...args,
      activo: true,
    });
  },
});

export const cambiar_password = mutation({
  args: {
    negocio_id: v.id("negocios"),
    id:         v.id("usuarios"),
    password:   v.string(),
  },
  handler: async (ctx, args) => {
    const usuario = await ctx.db.get(args.id);
    if (!usuario || usuario.negocio_id !== args.negocio_id) {
      throw new Error("Acceso denegado");
    }
    return await ctx.db.patch(args.id, {
      password: args.password
    });
  },
});

export const toggle_activo = mutation({
  args: {
    negocio_id: v.id("negocios"),
    id:     v.id("usuarios"),
    activo: v.boolean(),
  },
  handler: async (ctx, args) => {
    const usuario = await ctx.db.get(args.id);
    if (!usuario || usuario.negocio_id !== args.negocio_id) {
      throw new Error("Acceso denegado");
    }
    return await ctx.db.patch(args.id, { activo: args.activo });
  },
});

// ── Categorías ───────────────────────────────────────────
export const actualizar_categoria = mutation({
  args: {
    negocio_id: v.id("negocios"),
    id:     v.id("categorias"),
    nombre: v.optional(v.string()),
    icono:  v.optional(v.string()),
    activo: v.optional(v.boolean()),
  },
  handler: async (ctx, args) => {
    const { id, negocio_id, ...campos } = args;
    const categoria = await ctx.db.get(id);
    if (!categoria || categoria.negocio_id !== negocio_id) {
      throw new Error("Acceso denegado");
    }
    return await ctx.db.patch(id, campos);
  },
});

export const eliminar_categoria = mutation({
  args: {
    negocio_id: v.id("negocios"),
    id: v.id("categorias")
  },
  handler: async (ctx, args) => {
    const categoria = await ctx.db.get(args.id);
    if (!categoria || categoria.negocio_id !== args.negocio_id) {
      throw new Error("Acceso denegado");
    }
    return await ctx.db.patch(args.id, { activo: false });
  },
});
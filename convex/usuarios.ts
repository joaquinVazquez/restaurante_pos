import { query, mutation } from "./_generated/server";
import { v } from "convex/values";
import type { DataModel } from "./_generated/dataModel"; // <-- IMPORTANTE: Importar el tipo del esquema

export const login = query({
  args: { 
    username: v.string(), 
    password: v.string() 
  },
  handler: async (ctx, args) => {
    // Buscar
    const user = await ctx.db
      .query("usuarios")
      .withIndex("by_username", (q) => q.eq("username", args.username))
      .first();
    
    // Validar
    if (!user || user.password !== args.password || !user.activo) {
      return null;
    }
    
    return user; // Retorna el objeto tal cual está en la DB
  },
});

export const registrar_cuenta = mutation({
  args: {
    nombre_negocio: v.string(),
    nombre_usuario: v.string(),
    username: v.string(),
    password: v.string(),
  },
  handler: async (ctx, args) => {
    const existe = await ctx.db
      .query("usuarios")
      .withIndex("by_username", (q) => q.eq("username", args.username))
      .first();
      
    if (existe) {
      throw new Error("El nombre de usuario ya está registrado.");
    }

    const negocio_id = await ctx.db.insert("negocios", {
      nombre: args.nombre_negocio,
      activo: true,
    });

    const usuario_id = await ctx.db.insert("usuarios", {
      negocio_id: negocio_id,
      nombre: args.nombre_usuario,
      username: args.username,
      password: args.password,
      rol: "admin",
      activo: true,
    });

    return await ctx.db.get(usuario_id);
  }
});
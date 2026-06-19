// convex/usuarios.ts
import { query, mutation } from "./_generated/server";
import { v } from "convex/values";

export const login = query({
  args: {
    username: v.string(),
    password: v.string(),
  },
  handler: async (ctx, args) => {
    const usuario = await ctx.db
      .query("usuarios")
      .filter((q) =>
        q.and(
          q.eq(q.field("username"), args.username),
          q.eq(q.field("activo"), true)
        )
      )
      .first();

    if (!usuario) return null;
    if (usuario.password_hash !== args.password) return null;

    return {
      id:       usuario._id,
      nombre:   usuario.nombre,
      username: usuario.username,
      rol:      usuario.rol,
    };
  },
});

export const listar = query({
  args: {},
  handler: async (ctx) => {
    return await ctx.db
      .query("usuarios")
      .filter((q) => q.eq(q.field("activo"), true))
      .collect();
  },
});

export const crear = mutation({
  args: {
    nombre:        v.string(),
    username:      v.string(),
    password_hash: v.string(),
    rol:           v.string(),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("usuarios", {
      ...args,
      activo: true,
    });
  },
});

export const cambiar_password = mutation({
  args: {
    id: v.id("usuarios"),
    password_hash: v.string(),
  },
  handler: async (ctx, args) => {
    return await ctx.db.patch(args.id, {
      password_hash: args.password_hash,
    });
  },
});

export const toggle_activo = mutation({
  args: {
    id: v.id("usuarios"),
    activo: v.boolean(),
  },
  handler: async (ctx, args) => {
    return await ctx.db.patch(args.id, { activo: args.activo });
  },
});

export const seed = mutation({
  args: {},
  handler: async (ctx) => {
    const existe = await ctx.db
      .query("usuarios")
      .first();
    if (existe) return "ya existen datos";

    await ctx.db.insert("usuarios", {
      nombre: "Administrador",
      username: "admin",
      password_hash: "admin123",
      rol: "admin",
      activo: true,
    });

    await ctx.db.insert("usuarios", {
      nombre: "Cajero",
      username: "cajero1",
      password_hash: "cajero123",
      rol: "cajero",
      activo: true,
    });

    const cat1 = await ctx.db.insert("categorias", {
      nombre: "Bebidas", icono: "🥤", activo: true });
    const cat2 = await ctx.db.insert("categorias", {
      nombre: "Antojitos", icono: "🌮", activo: true });
    const cat3 = await ctx.db.insert("categorias", {
      nombre: "Platos Fuertes", icono: "🍽️", activo: true });
    const cat4 = await ctx.db.insert("categorias", {
      nombre: "Postres", icono: "🍰", activo: true });
    const cat5 = await ctx.db.insert("categorias", {
      nombre: "Desayunos", icono: "🍳", activo: true });

    const cats = [cat1, cat2, cat3, cat4, cat5];

    const productos = [
      { nombre: "Agua Natural 500ml", precio: 15, stock: 100, cat: 0 },
      { nombre: "Refresco 600ml",     precio: 22, stock: 80,  cat: 0 },
      { nombre: "Café Americano",     precio: 25, stock: 50,  cat: 0 },
      { nombre: "Taco de Pastor",     precio: 18, stock: 60,  cat: 1 },
      { nombre: "Taco de Bistec",     precio: 20, stock: 60,  cat: 1 },
      { nombre: "Quesadilla",         precio: 35, stock: 40,  cat: 1 },
      { nombre: "Carne Asada",        precio: 120, stock: 20, cat: 2 },
      { nombre: "Pollo en Mole",      precio: 95,  stock: 15, cat: 2 },
      { nombre: "Flan Napolitano",    precio: 40,  stock: 25, cat: 3 },
      { nombre: "Chilaquiles Rojos",  precio: 75,  stock: 30, cat: 4 },
    ];

    for (const p of productos) {
      await ctx.db.insert("productos", {
        nombre:       p.nombre,
        precio:       p.precio,
        stock:        p.stock,
        categoria_id: cats[p.cat],
        activo:       true,
      });
    }

    await ctx.db.insert("configuracion", {
      clave: "restaurante_nombre",
      valor: "Mi Restaurante",
      descripcion: "Nombre del restaurante"
    });

    return "seed completado";
  },
});

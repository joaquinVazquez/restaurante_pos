--
-- PostgreSQL database dump
--

\restrict yEOPrVIxR1HAqegYhUymLVpEWtj474rci0beFYTWeUVWgFuMmtDe6LJDURbN6Ag

-- Dumped from database version 18.3
-- Dumped by pg_dump version 18.3

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: categorias; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.categorias (
    id integer NOT NULL,
    nombre character varying(50) NOT NULL,
    icono character varying(10),
    activo boolean DEFAULT true,
    creado_en timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.categorias OWNER TO postgres;

--
-- Name: categorias_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.categorias_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.categorias_id_seq OWNER TO postgres;

--
-- Name: categorias_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.categorias_id_seq OWNED BY public.categorias.id;


--
-- Name: clientes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.clientes (
    id integer NOT NULL,
    nombre character varying(100) NOT NULL,
    telefono character varying(20),
    email character varying(100),
    direccion text,
    notas text,
    activo boolean DEFAULT true,
    creado_en timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.clientes OWNER TO postgres;

--
-- Name: clientes_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.clientes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.clientes_id_seq OWNER TO postgres;

--
-- Name: clientes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.clientes_id_seq OWNED BY public.clientes.id;


--
-- Name: cortes_caja; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cortes_caja (
    id integer NOT NULL,
    fecha date NOT NULL,
    total_ventas integer DEFAULT 0,
    total_ingresos numeric(10,2) DEFAULT 0,
    efectivo numeric(10,2) DEFAULT 0,
    tarjeta numeric(10,2) DEFAULT 0,
    observaciones text,
    creado_en timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.cortes_caja OWNER TO postgres;

--
-- Name: cortes_caja_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.cortes_caja_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.cortes_caja_id_seq OWNER TO postgres;

--
-- Name: cortes_caja_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.cortes_caja_id_seq OWNED BY public.cortes_caja.id;


--
-- Name: detalle_ventas; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.detalle_ventas (
    id integer NOT NULL,
    venta_id integer,
    producto_id integer,
    cantidad integer NOT NULL,
    precio_unitario numeric(10,2) NOT NULL,
    subtotal numeric(10,2) GENERATED ALWAYS AS (((cantidad)::numeric * precio_unitario)) STORED,
    CONSTRAINT detalle_ventas_cantidad_check CHECK ((cantidad > 0))
);


ALTER TABLE public.detalle_ventas OWNER TO postgres;

--
-- Name: detalle_ventas_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.detalle_ventas_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.detalle_ventas_id_seq OWNER TO postgres;

--
-- Name: detalle_ventas_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.detalle_ventas_id_seq OWNED BY public.detalle_ventas.id;


--
-- Name: productos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.productos (
    id integer NOT NULL,
    nombre character varying(100) NOT NULL,
    descripcion text,
    precio numeric(10,2) NOT NULL,
    stock integer DEFAULT 0 NOT NULL,
    categoria_id integer,
    activo boolean DEFAULT true,
    creado_en timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    imagen character varying(255),
    CONSTRAINT productos_precio_check CHECK ((precio > (0)::numeric)),
    CONSTRAINT productos_stock_check CHECK ((stock >= 0))
);


ALTER TABLE public.productos OWNER TO postgres;

--
-- Name: productos_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.productos_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.productos_id_seq OWNER TO postgres;

--
-- Name: productos_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.productos_id_seq OWNED BY public.productos.id;


--
-- Name: usuarios; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.usuarios (
    id integer NOT NULL,
    nombre character varying(100) NOT NULL,
    username character varying(50) NOT NULL,
    password_hash character varying(255) NOT NULL,
    rol character varying(20) NOT NULL,
    activo boolean DEFAULT true,
    creado_en timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT usuarios_rol_check CHECK (((rol)::text = ANY ((ARRAY['admin'::character varying, 'cajero'::character varying])::text[])))
);


ALTER TABLE public.usuarios OWNER TO postgres;

--
-- Name: usuarios_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.usuarios_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.usuarios_id_seq OWNER TO postgres;

--
-- Name: usuarios_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.usuarios_id_seq OWNED BY public.usuarios.id;


--
-- Name: ventas; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.ventas (
    id integer NOT NULL,
    usuario_id integer,
    total numeric(10,2) NOT NULL,
    metodo_pago character varying(20),
    monto_recibido numeric(10,2),
    cambio numeric(10,2),
    estado character varying(20) DEFAULT 'completada'::character varying,
    creado_en timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    cliente_id integer,
    CONSTRAINT ventas_metodo_pago_check CHECK (((metodo_pago)::text = ANY ((ARRAY['efectivo'::character varying, 'tarjeta'::character varying])::text[])))
);


ALTER TABLE public.ventas OWNER TO postgres;

--
-- Name: ventas_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.ventas_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.ventas_id_seq OWNER TO postgres;

--
-- Name: ventas_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.ventas_id_seq OWNED BY public.ventas.id;


--
-- Name: categorias id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categorias ALTER COLUMN id SET DEFAULT nextval('public.categorias_id_seq'::regclass);


--
-- Name: clientes id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.clientes ALTER COLUMN id SET DEFAULT nextval('public.clientes_id_seq'::regclass);


--
-- Name: cortes_caja id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cortes_caja ALTER COLUMN id SET DEFAULT nextval('public.cortes_caja_id_seq'::regclass);


--
-- Name: detalle_ventas id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.detalle_ventas ALTER COLUMN id SET DEFAULT nextval('public.detalle_ventas_id_seq'::regclass);


--
-- Name: productos id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.productos ALTER COLUMN id SET DEFAULT nextval('public.productos_id_seq'::regclass);


--
-- Name: usuarios id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuarios ALTER COLUMN id SET DEFAULT nextval('public.usuarios_id_seq'::regclass);


--
-- Name: ventas id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ventas ALTER COLUMN id SET DEFAULT nextval('public.ventas_id_seq'::regclass);


--
-- Data for Name: categorias; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.categorias (id, nombre, icono, activo, creado_en) FROM stdin;
1	Bebidas	🥤	t	2026-04-08 19:16:27.065256
2	Antojitos	🌮	t	2026-04-08 19:16:27.065256
3	Platos Fuertes	🍽️	t	2026-04-08 19:16:27.065256
4	Postres	🍰	t	2026-04-08 19:16:27.065256
5	Desayunos	🍳	t	2026-04-08 19:16:27.065256
\.


--
-- Data for Name: clientes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.clientes (id, nombre, telefono, email, direccion, notas, activo, creado_en) FROM stdin;
1	Scarly Ivetzi Padilla Cruz	9673880382	scarlypadilla72@gmail.com	Av Central, ramajal	\N	t	2026-04-23 21:06:30.145938
2	Carlos Valdez	9921394207	\N	\N	\N	t	2026-04-25 09:47:52.083024
\.


--
-- Data for Name: cortes_caja; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.cortes_caja (id, fecha, total_ventas, total_ingresos, efectivo, tarjeta, observaciones, creado_en) FROM stdin;
1	2026-04-11	3	687.00	570.00	117.00	\N	2026-04-11 10:06:52.033484
2	2026-04-11	4	917.00	800.00	117.00	\N	2026-04-11 10:11:58.738434
3	2026-04-11	6	997.00	880.00	117.00	\N	2026-04-11 10:38:50.749216
4	2026-04-14	6	695.00	695.00	0.00	\N	2026-04-14 18:22:41.551157
5	2026-04-14	6	695.00	695.00	0.00	\N	2026-04-14 18:23:14.158881
\.


--
-- Data for Name: detalle_ventas; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.detalle_ventas (id, venta_id, producto_id, cantidad, precio_unitario) FROM stdin;
1	1	8	1	95.00
2	1	9	1	40.00
3	1	2	1	22.00
4	3	1	3	15.00
5	3	3	2	25.00
6	3	7	2	120.00
7	3	8	1	95.00
8	4	1	1	15.00
9	4	3	1	25.00
10	5	1	1	15.00
11	5	3	1	25.00
12	6	3	1	25.00
13	6	10	1	75.00
14	7	7	1	120.00
15	7	8	1	95.00
16	8	3	1	25.00
17	8	9	1	30.00
18	9	7	2	120.00
19	9	9	1	30.00
20	9	1	1	15.00
21	10	7	2	120.00
22	10	9	1	30.00
23	10	1	1	15.00
24	11	9	2	30.00
25	11	6	1	35.00
26	11	2	1	22.00
27	12	1	1	15.00
28	12	7	1	120.00
29	12	8	1	95.00
30	13	1	1	15.00
31	13	3	1	25.00
32	14	2	1	22.00
33	14	4	1	18.00
34	15	1	1	15.00
35	15	3	1	25.00
36	15	9	1	30.00
37	16	1	1	15.00
38	16	3	1	25.00
39	16	9	1	30.00
40	17	1	1	15.00
41	17	3	4	25.00
42	17	7	1	120.00
43	18	3	2	25.00
44	19	1	1	15.00
45	19	7	1	120.00
46	19	4	1	18.00
47	20	10	1	75.00
48	20	2	1	22.00
49	20	5	1	20.00
50	21	10	1	75.00
51	21	3	1	25.00
52	22	10	1	75.00
53	22	3	1	25.00
54	23	10	1	75.00
55	23	3	1	25.00
56	24	1	1	15.00
57	24	6	1	35.00
58	25	6	2	35.00
59	25	2	1	22.00
60	25	8	1	95.00
\.


--
-- Data for Name: productos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.productos (id, nombre, descripcion, precio, stock, categoria_id, activo, creado_en, imagen) FROM stdin;
5	Taco de Bistec	Con guacamole y salsa verde	20.00	59	2	t	2026-04-08 19:16:27.065256	\N
7	Carne Asada	Con arroz, frijoles y tortillas	120.00	10	\N	t	2026-04-08 19:16:27.065256	assets/productos\\Carne_Asada_carne asada.webp
13	Chilaquiles	\N	100.00	20	\N	t	2026-04-14 18:21:40.345862	assets/productos\\Chilaquiles_chilaquiles.webp
10	Chilaquiles Rojos	Con crema, queso y huevo	75.00	25	\N	t	2026-04-08 19:16:27.065256	assets/productos\\Chilaquiles_Rojos_chilaquiles rojos.webp
3	Café Americano	Café de olla recién hecho	25.00	32	\N	t	2026-04-08 19:16:27.065256	assets/productos\\Café_Americano_cafe de olla.webp
1	Agua Natural 600ml	Agua purificada fría	15.00	86	\N	t	2026-04-08 19:16:27.065256	assets/productos\\Agua_Natural_600ml_agua enbotellada.webp
11	Tostadas de Pollo	\N	15.00	100	2	t	2026-04-11 09:19:36.367463	assets/productos\\Tostadas_de_Pollo_tostadas de pollo.jpg
12	Agua chile	\N	190.00	10	\N	f	2026-04-14 18:20:27.472451	assets/productos\\Agua_chile_agua chiles verdes.webp
6	Quesadilla	Con queso Oaxaca y epazote	35.00	36	\N	t	2026-04-08 19:16:27.065256	assets/productos\\Quesadilla_quesadilla.webp
2	Refresco 600ml	Coca-Cola, Pepsi o Sprite	22.00	75	1	t	2026-04-08 19:16:27.065256	\N
8	Pollo en Mole	Receta tradicional de la casa	95.00	10	\N	t	2026-04-08 19:16:27.065256	assets/productos\\Pollo_en_Mole_mole de pollo.webp
9	Flan Napolitano	Casero con cajeta	30.00	0	\N	t	2026-04-08 19:16:27.065256	assets/productos\\Flan_Napolitano_flan napolitano.webp
4	Taco de Pastor	Con cilantro, cebolla y piña	18.00	58	2	t	2026-04-08 19:16:27.065256	\N
\.


--
-- Data for Name: usuarios; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.usuarios (id, nombre, username, password_hash, rol, activo, creado_en) FROM stdin;
1	Administrador	admin	admin123	admin	t	2026-04-08 19:16:27.065256
2	Cajero Principal	cajero1	cajero123	cajero	t	2026-04-08 19:16:27.065256
\.


--
-- Data for Name: ventas; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.ventas (id, usuario_id, total, metodo_pago, monto_recibido, cambio, estado, creado_en, cliente_id) FROM stdin;
1	1	157.00	efectivo	1000.00	843.00	completada	2026-04-09 22:00:25.848197	\N
2	1	157.00	efectivo	1000.00	843.00	completada	2026-04-09 22:00:29.6583	\N
3	1	430.00	efectivo	500.00	70.00	completada	2026-04-09 22:12:41.580599	\N
4	1	40.00	efectivo	400.00	360.00	completada	2026-04-10 22:37:26.238497	\N
5	1	40.00	efectivo	400.00	360.00	completada	2026-04-10 22:37:28.10457	\N
6	1	100.00	efectivo	500.00	400.00	completada	2026-04-10 22:39:10.100196	\N
7	1	215.00	efectivo	1000.00	785.00	completada	2026-04-10 23:07:43.130073	\N
8	1	55.00	efectivo	100.00	45.00	completada	2026-04-10 23:12:00.615382	\N
9	1	285.00	efectivo	300.00	15.00	completada	2026-04-11 09:25:17.880634	\N
10	1	285.00	efectivo	300.00	15.00	completada	2026-04-11 09:25:20.083986	\N
11	1	117.00	tarjeta	\N	\N	completada	2026-04-11 09:26:16.728002	\N
12	1	230.00	efectivo	500.00	270.00	completada	2026-04-11 10:11:00.776149	\N
13	1	40.00	efectivo	200.00	160.00	completada	2026-04-11 10:26:52.777216	\N
14	1	40.00	efectivo	100.00	60.00	completada	2026-04-11 10:35:36.802966	\N
15	1	70.00	efectivo	500.00	430.00	completada	2026-04-14 17:25:59.084002	\N
16	1	70.00	efectivo	500.00	430.00	completada	2026-04-14 17:26:01.299524	\N
17	1	235.00	efectivo	235.00	0.00	completada	2026-04-14 17:57:43.659085	\N
18	1	50.00	efectivo	100.00	50.00	completada	2026-04-14 18:16:27.207316	\N
19	1	153.00	efectivo	200.00	47.00	completada	2026-04-14 18:17:45.346894	\N
20	1	117.00	efectivo	200.00	83.00	completada	2026-04-14 18:18:31.449656	\N
21	1	100.00	efectivo	200.00	100.00	completada	2026-04-23 21:07:14.929458	\N
22	1	100.00	efectivo	200.00	100.00	completada	2026-04-23 21:07:17.396226	\N
23	1	100.00	efectivo	200.00	100.00	completada	2026-04-23 21:07:21.32306	\N
24	1	50.00	efectivo	200.00	150.00	completada	2026-04-24 23:43:27.90831	\N
25	1	187.00	efectivo	500.00	313.00	completada	2026-04-25 09:45:54.160194	\N
\.


--
-- Name: categorias_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.categorias_id_seq', 6, true);


--
-- Name: clientes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.clientes_id_seq', 2, true);


--
-- Name: cortes_caja_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.cortes_caja_id_seq', 5, true);


--
-- Name: detalle_ventas_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.detalle_ventas_id_seq', 60, true);


--
-- Name: productos_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.productos_id_seq', 13, true);


--
-- Name: usuarios_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.usuarios_id_seq', 2, true);


--
-- Name: ventas_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.ventas_id_seq', 25, true);


--
-- Name: categorias categorias_nombre_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categorias
    ADD CONSTRAINT categorias_nombre_key UNIQUE (nombre);


--
-- Name: categorias categorias_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categorias
    ADD CONSTRAINT categorias_pkey PRIMARY KEY (id);


--
-- Name: clientes clientes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.clientes
    ADD CONSTRAINT clientes_pkey PRIMARY KEY (id);


--
-- Name: cortes_caja cortes_caja_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cortes_caja
    ADD CONSTRAINT cortes_caja_pkey PRIMARY KEY (id);


--
-- Name: detalle_ventas detalle_ventas_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.detalle_ventas
    ADD CONSTRAINT detalle_ventas_pkey PRIMARY KEY (id);


--
-- Name: productos productos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.productos
    ADD CONSTRAINT productos_pkey PRIMARY KEY (id);


--
-- Name: usuarios usuarios_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_pkey PRIMARY KEY (id);


--
-- Name: usuarios usuarios_username_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_username_key UNIQUE (username);


--
-- Name: ventas ventas_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ventas
    ADD CONSTRAINT ventas_pkey PRIMARY KEY (id);


--
-- Name: detalle_ventas detalle_ventas_producto_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.detalle_ventas
    ADD CONSTRAINT detalle_ventas_producto_id_fkey FOREIGN KEY (producto_id) REFERENCES public.productos(id);


--
-- Name: detalle_ventas detalle_ventas_venta_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.detalle_ventas
    ADD CONSTRAINT detalle_ventas_venta_id_fkey FOREIGN KEY (venta_id) REFERENCES public.ventas(id) ON DELETE CASCADE;


--
-- Name: productos productos_categoria_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.productos
    ADD CONSTRAINT productos_categoria_id_fkey FOREIGN KEY (categoria_id) REFERENCES public.categorias(id) ON DELETE SET NULL;


--
-- Name: ventas ventas_cliente_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ventas
    ADD CONSTRAINT ventas_cliente_id_fkey FOREIGN KEY (cliente_id) REFERENCES public.clientes(id);


--
-- Name: ventas ventas_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ventas
    ADD CONSTRAINT ventas_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuarios(id);


--
-- PostgreSQL database dump complete
--

\unrestrict yEOPrVIxR1HAqegYhUymLVpEWtj474rci0beFYTWeUVWgFuMmtDe6LJDURbN6Ag


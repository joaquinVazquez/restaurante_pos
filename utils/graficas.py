# utils/graficas.py
"""
Módulo auxiliar para generar gráficas con Matplotlib y devolverlas
como imágenes en memoria (base64), listas para usarse en ft.Image(src_base64=...).
"""
import base64
import io

import matplotlib
matplotlib.use("Agg")  # Backend sin interfaz gráfica, requerido para correr junto a Flet
import matplotlib.pyplot as plt

COLOR_ACENTO = "#00b894"
COLOR_AZUL = "#3498db"
COLOR_NARANJA = "#ff7a00"
COLOR_TEXTO = "#2c3e50"
COLOR_SUBTEXTO = "#7f8c8d"


def _fig_a_base64(fig) -> str:
    """Convierte una figura de matplotlib a una cadena base64 (PNG)."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight", transparent=True)
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")


def grafica_barras_comparativa(datos: list, titulo: str = "") -> str:
    """
    datos: lista de dicts con claves 'grupo' y 'total'.
    Devuelve una imagen base64 de barras verticales.
    """
    if not datos:
        return ""

    grupos = [str(d["grupo"]) for d in datos]
    totales = [float(d["total"]) for d in datos]

    fig, ax = plt.subplots(figsize=(7, 3.5))
    barras = ax.bar(grupos, totales, color=COLOR_ACENTO, width=0.6)

    ax.set_title(titulo, fontsize=12, color=COLOR_TEXTO, fontweight="bold")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(colors=COLOR_SUBTEXTO)
    ax.yaxis.set_visible(False)

    for barra, valor in zip(barras, totales):
        ax.text(
            barra.get_x() + barra.get_width() / 2,
            barra.get_height(),
            f"${valor:,.0f}",
            ha="center", va="bottom",
            fontsize=9, color=COLOR_TEXTO,
        )

    fig.tight_layout()
    return _fig_a_base64(fig)


def grafica_productos_top(productos: list) -> str:
    """
    productos: lista de dicts con 'producto_nombre' y 'cantidad'.
    Devuelve una imagen base64 de barras horizontales (top vendidos arriba).
    """
    if not productos:
        return ""

    # Invertimos para que el #1 quede arriba en barh
    datos = list(reversed(productos))
    nombres = [d["producto_nombre"][:22] for d in datos]
    cantidades = [d["cantidad"] for d in datos]

    fig, ax = plt.subplots(figsize=(7, max(2.5, 0.5 * len(datos))))
    barras = ax.barh(nombres, cantidades, color=COLOR_AZUL, height=0.6)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.tick_params(colors=COLOR_TEXTO, labelsize=10)
    ax.xaxis.set_visible(False)

    for barra, valor in zip(barras, cantidades):
        ax.text(
            barra.get_width(),
            barra.get_y() + barra.get_height() / 2,
            f" {valor:.0f}",
            va="center", ha="left",
            fontsize=9, color=COLOR_TEXTO, fontweight="bold",
        )

    fig.tight_layout()
    return _fig_a_base64(fig)
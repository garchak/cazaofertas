import json
import time
import asyncio
import os
from serpapi import GoogleSearch
from telegram import Bot

# -----------------------
# CONFIGURACIÓN (desde GitHub Secrets)
# -----------------------

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

bot = Bot(token=TELEGRAM_TOKEN)

# -----------------------
# FUNCIONES
# -----------------------

def cargar_productos():
    with open("productos.json", "r", encoding="utf-8") as f:
        return json.load(f)

def buscar_producto(query, precio_max):
    params = {
        "engine": "google_shopping",
        "q": query,
        "api_key": SERPAPI_KEY,
        "gl": "es",
        "hl": "es"
    }

    search = GoogleSearch(params)
    data = search.get_dict()

    resultados = []
    items = data.get("shopping_results", [])

    for item in items:
        precio = item.get("extracted_price")
        if precio and precio <= precio_max:
            resultados.append({
                "titulo": item.get("title"),
                "link": item.get("product_link"),
                "precio": precio,
                "tienda": item.get("source")
            })

    return resultados

async def enviar_telegram(mensaje):
    try:
        await bot.send_message(
            chat_id=CHAT_ID,
            text=mensaje,
            parse_mode="HTML",
            read_timeout=60,
            write_timeout=60
        )
    except Exception as e:
        print(f"⚠️ Aviso Telegram: {e}")

# -----------------------
# MAIN
# -----------------------

async def main():
    productos = cargar_productos()
    hay_ofertas = False

    for producto in productos:
        print(f"Buscando: {producto['nombre']} ...")

        resultados = buscar_producto(producto["query"], producto["precio_max"])

        if resultados:
            hay_ofertas = True
            mensaje = f"🔥 <b>{producto['nombre']}</b> 🔥\n\n"

            for r in resultados:
                mensaje += f"💰 {r['precio']}€ - {r['tienda']}\n"
                mensaje += f"<a href='{r['link']}'>{r['titulo']}</a>\n\n"

            await enviar_telegram(mensaje)

        time.sleep(2)

    if not hay_ofertas:
        await enviar_telegram("No hay ofertas interesantes esta vez 💤")

# -----------------------
# RUN
# -----------------------

if __name__ == "__main__":
    asyncio.run(main())

import requests
from bs4 import BeautifulSoup
import re
import time
import schedule

TOKEN_TELEGRAM = "8460939253:AAHrEyJjP4oWBeOWhQdUz9r3EN4_I34bbbM"
CHAT_ID = "6784502890"
SERP_API_KEY = "0e906b47ed88b5358360dfb283acb147ba94f4b50f77760c11f0014ace9739d4" 

PRODUTO = "placa de vídeo rtx 7600"  #produto
PRECO_MAX = 1600.00  #preço que eu quero 
INTERVALO_HORAS = 5  #intervalo de tempo para procurar(em horas)

LOJAS_CONFIAVEIS = [
    "amazon.com.br",
    "mercadolivre.com.br",
    "kabum.com.br",
    "magazineluiza.com.br",
    "americanas.com.br",
    "submarino.com.br",
    "shopee.com.br",
    "pichau.com.br",
    "terabyteshop.com.br"
]

def enviar_telegram(msg):   #bot do telegram
    url = f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except Exception as e:
        print("Erro ao enviar Telegram:", e)

def buscar_links():    #procurar produto na internet
    url = "https://serpapi.com/search.json"
    params = {
        "engine": "google",
        "q": PRODUTO,
        "api_key": SERP_API_KEY,
        "hl": "pt"
    }
    r = requests.get(url, params=params)
    data = r.json()
    if "organic_results" not in data:
        print("Nenhum resultado orgânico encontrado na busca")
        return []
    links = [item["link"] for item in data.get("organic_results", []) if "link" in item]
    links_filtrados = [link for link in links if any(loja in link for loja in LOJAS_CONFIAVEIS)]
    return links_filtrados

def extrair_preco(url):    #comparador de preço
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        #amazon
        if "amazon.com.br" in url:
            preco_tag = soup.select_one("#priceblock_ourprice, #priceblock_dealprice")
            if preco_tag:
                preco_str = preco_tag.get_text(strip=True)
                return tratar_preco(preco_str)

        #mercado livre
        elif "mercadolivre.com.br" in url:
            preco_tag = soup.select_one("span.price-tag-fraction")
            if preco_tag:
                preco_str = preco_tag.get_text(strip=True)
                # às vezes tem centavos em outra tag
                centavos_tag = soup.select_one("span.price-tag-cents")
                if centavos_tag:
                    preco_str += "," + centavos_tag.get_text(strip=True)
                return tratar_preco("R$ " + preco_str)

        #kabum
        elif "kabum.com.br" in url:
            preco_tag = soup.select_one(".price-tag")
            if preco_tag:
                preco_str = preco_tag.get_text(strip=True)
                return tratar_preco(preco_str)

        #magazine luiza
        elif "magazineluiza.com.br" in url:
            preco_tag = soup.select_one(".price-template__text")
            if preco_tag:
                preco_str = preco_tag.get_text(strip=True)
                return tratar_preco(preco_str)

        #americanas e submarino
        elif "americanas.com.br" in url or "submarino.com.br" in url:
            preco_tag = soup.select_one(".sales-price")
            if preco_tag:
                preco_str = preco_tag.get_text(strip=True)
                return tratar_preco(preco_str)

        #shopee
        elif "shopee.com.br" in url:
            preco_tag = soup.select_one("div._3e_UQT span._3_ISdg")
            if preco_tag:
                preco_str = preco_tag.get_text(strip=True)
                return tratar_preco(preco_str)

        #pichau
        elif "pichau.com.br" in url:
            preco_tag = soup.select_one(".preco_desconto")
            if preco_tag:
                preco_str = preco_tag.get_text(strip=True)
                return tratar_preco(preco_str)

        #terabyte 
        elif "terabyteshop.com.br" in url:
            preco_tag = soup.select_one(".preco-promocional")
            if preco_tag:
                preco_str = preco_tag.get_text(strip=True)
                return tratar_preco(preco_str)

        #tratar preços para ver se tem algum valor em reais
        texto = soup.get_text()
        match = re.search(r"R\$ ?\d{1,3}(?:\.\d{3})*,\d{2}", texto)
        if match:
            return tratar_preco(match.group())

    except Exception as e:
        print(f"Erro ao extrair preço de {url}: {e}")
    return None

def tratar_preco(preco_str):
    preco_str = preco_str.replace("R$", "").replace(".", "").replace(",", ".").strip()
    try:
        preco = float(preco_str)
        #valores abaixo desse aqui em baixo(500) provavelmente é valor de parcela
        if preco < 500:
            return None
        return preco
    except:
        return None

def procurar_ofertas():
    try:
        print(f"🔍 Buscando ofertas para '{PRODUTO}'...")
        links = buscar_links()
        ofertas = []
        for link in links:
            preco = extrair_preco(link)
            if preco and preco <= PRECO_MAX:
                ofertas.append(f"{link} - R$ {preco:.2f}")

        if ofertas:
            mensagem = "🔥 Ofertas encontradas:\n" + "\n".join(ofertas)
            enviar_telegram(mensagem)
            print(mensagem)
        else:
            print("Nenhuma oferta no preço desejado encontrada.")
            enviar_telegram("Nenhuma oferta no preço desejado encontrada.")
    except Exception as e:
        print("Erro na busca de ofertas:", e)

if __name__ == "__main__":
    print(f"📡 Bot iniciado. Monitorando '{PRODUTO}' a cada {INTERVALO_HORAS} horas{'s' if INTERVALO_HORAS > 1 else ''}.")
    schedule.every(INTERVALO_HORAS).hours.do(procurar_ofertas)

    while True:
        schedule.run_pending()
        time.sleep(1)

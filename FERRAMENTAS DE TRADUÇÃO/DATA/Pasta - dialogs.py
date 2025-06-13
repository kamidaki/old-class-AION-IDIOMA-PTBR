import os
import re
import asyncio
import aiohttp
from datetime import datetime
from urllib.parse import quote
from bs4 import BeautifulSoup, Comment

#------------------------------
# CONFIGURAÇÕES
#------------------------------
DIR_ORIGEM      = r"F:\Servidor Aion\dialogs"
DIR_DESTINO     = r"F:\Servidor Aion\dialogs\traduzidos"
LOG_FILE        = os.path.join(DIR_DESTINO, 'translated.log')
ENCODING        = 'utf-8'
PLACEHOLDER_PATTERN = re.compile(r"(\[.*?\]|\{.*?\})")

async def traduzir_texto(session: aiohttp.ClientSession, texto: str)-> str:
    parts = PLACEHOLDER_PATTERN.split(texto)
    trad_parts = []
    for part in parts:
        if PLACEHOLDER_PATTERN.fullmatch(part) or not part.strip():
            trad_parts.append(part)
        else:
            q   = quote(part, safe='')
            url = (
                f"https://translate.googleapis.com/translate_a/single?client=gtx"
                f"&sl=auto&tl=pt&dt=t&q={q}"
            )
            try:
                async with session.get(url, headers={'User-Agent': 'Mozilla/5.0'}) as resp:
                    if resp.status != 200 or 'application/json' not in resp.headers.get('Content-Type',''):
                        raise RuntimeError(f"{resp.status} / {resp.headers.get('Content-Type')}")
                    data = await resp.json()
                    trad_parts.append(''.join(seg[0] for seg in data[0]))
            except Exception as e:
                print(f"   ⚠️ Erro trad: “{part[:30]}…”-> pulando esse trecho ({e})")
                trad_parts.append(part)
    return ''.join(trad_parts)

async def traduzir_arquivo(session: aiohttp.ClientSession, caminho_in: str, caminho_out: str):
    rel = os.path.relpath(caminho_in, DIR_ORIGEM)
    print(f"\n🔄 Traduzindo: {rel}")
    # leitura tolerante
    try:
        with open(caminho_in, encoding=ENCODING, errors='ignore') as f:
            html = f.read()
    except Exception as e:
        print(f"⚠️ Não foi possível ler {rel}: {e} — pulando.")
        return

    soup = BeautifulSoup(html, 'html.parser')
    tasks = []

    # Detecta automaticamente todas as TAGS “leaf” com texto
    for elem in soup.find_all():
        name = elem.name.lower()
        # pula blocos de código e comentários
        if name in ['script', 'style']:
            continue
        # pula elementos que têm sub-tags (não são leaf)
        if elem.find(True):
            continue
        text = elem.get_text(strip=False)
        if text and text.strip():
            tasks.append((elem, traduzir_texto(session, text)))

    # aplica traduções
    for elem, task in tasks:
        try:
            trad = await task
            elem.clear()
            elem.append(trad)
        except Exception as e:
            print(f"   ⚠️ Falha bloco em {rel}: {e} — pulando bloco.")

    os.makedirs(os.path.dirname(caminho_out), exist_ok=True)
    with open(caminho_out, 'w', encoding=ENCODING, errors='ignore') as f:
        f.write(str(soup))
    # registra no log
    with open(LOG_FILE, 'a', encoding=ENCODING) as logf:
        logf.write(rel + '\n')
    print(f"✅ Salvo: {rel}")

async def main():
    # carrega já traduzidos
    processed = set()
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, encoding=ENCODING) as logf:
            processed = {l.strip() for l in logf if l.strip()}

    async with aiohttp.ClientSession() as session:
        for raiz, _, arquivos in os.walk(DIR_ORIGEM):
            for nome in sorted(arquivos):
                if not nome.lower().endswith('.html'):
                    continue
                caminho_in  = os.path.join(raiz, nome)
                rel         = os.path.relpath(caminho_in, DIR_ORIGEM)
                caminho_out = os.path.join(DIR_DESTINO, rel)
                if rel in processed:
                    print(f"⏭ Ignorando já traduzido: {rel}")
                    continue
                try:
                    await traduzir_arquivo(session, caminho_in, caminho_out)
                except Exception as e:
                    print(f"❌ Erro geral em {rel}: {e} — pulando arquivo.")
    print("\n🎉 Tradução concluída.")

if __name__ == '__main__':
    asyncio.run(main())

import os
import re
import asyncio
import aiohttp
from bs4 import BeautifulSoup, Comment
from datetime import datetime

#------------------------------
# CONFIGURAÇÕES GLOBAIS
#------------------------------
DIR_ORIGEM     = r"F:\Servidor Aion\help"
DIR_DESTINO    = r"F:\Servidor Aion\help\traduzidos"
FORMATO        = 'utf-16'

# padrões a proteger (placeholders, variáveis, formatações, quebras de linha)
PADROES_PROTEGER = [
    r'%\d*\.\d*f',    # %1.2f
    r'%\w+',          # %s, %d
    r'{\d+}',         # {0}
    r'\$\w+',         # $VAR
    r'\[\%[^\]]+\]',  # [%STR_HP]
    r'\\n'            # \n literais
]
SPLIT_REGEX = re.compile('(' + '|'.join(PADROES_PROTEGER) + ')')

async def traduzir_google(session: aiohttp.ClientSession, texto: str)-> str:
    """Tradução via Google Translate (mobile)."""
    await asyncio.sleep(0.6)
    q   = aiohttp.helpers.quote(texto, safe='')
    url = f"https://translate.google.com/m?sl=auto&tl=pt&q={q}"
    async with session.get(url, headers={'User-Agent':'Mozilla/5.0'}) as resp:
        html = await resp.text()
        m = re.search(r'class="result-container">(.*?)<', html)
        return m.group(1) if m else texto

async def traduzir_segmentos(texto: str, session: aiohttp.ClientSession)-> str:
    """
    Divide 'texto' em pedaços pelos placeholders, traduz apenas o que precisa
    e recompõe.
    """
    parts = SPLIT_REGEX.split(texto)
    for i, part in enumerate(parts):
        if not part.strip():
            continue
        # pula se for placeholder
        if any(re.fullmatch(p, part, flags=re.IGNORECASE) for p in PADROES_PROTEGER):
            continue
        parts[i] = await traduzir_google(session, part)
    return ''.join(parts)

async def process_sections(raw: str, tag: str, session: aiohttp.ClientSession)-> str:
    """
    Traduz o conteúdo entre <tag>...</tag> (e.g. <question>).
    """
    pattern = re.compile(rf'(<{tag}>)(.*?)(</{tag}>)', re.DOTALL)
    out, last = [], 0
    for m in pattern.finditer(raw):
        out.append(raw[last:m.start()])
        texto = m.group(2)
        novo   = await traduzir_segmentos(texto, session)
        out.append(m.group(1) + novo + m.group(3))
        last = m.end()
    out.append(raw[last:])
    return ''.join(out)

async def process_cdata_html(raw: str, session: aiohttp.ClientSession)-> str:
    """
    Localiza cada <Contents cdata="true"> <![CDATA[ ... ]]> </Contents>,
    parseia o HTML interno, traduz apenas os textos visíveis, e recompõe.
    """
    pattern = re.compile(
        r'(<Contents\s+cdata="true">\s*<!\[CDATA\[)(.*?)(\]\]>\s*</Contents>)',
        re.DOTALL
    )
    out, last = [], 0
    for m in pattern.finditer(raw):
        out.append(raw[last:m.start()])
        prefix, inner_html, suffix = m.groups()
        soup = BeautifulSoup(inner_html, 'html.parser')
        for node in soup.find_all(string=True):
            # pula comentários e código
            if isinstance(node, Comment) or node.parent.name in ['script', 'style']:
                continue
            txt = str(node)
            if not txt.strip():
                continue
            novo = await traduzir_segmentos(txt, session)
            node.replace_with(novo)
        new_inner = str(soup)
        out.append(prefix + new_inner + suffix)
        last = m.end()
    out.append(raw[last:])
    return ''.join(out)

async def process_file(session: aiohttp.ClientSession, caminho_in: str):
    rel = os.path.relpath(caminho_in, DIR_ORIGEM)
    caminho_out = os.path.join(DIR_DESTINO, rel)
    os.makedirs(os.path.dirname(caminho_out), exist_ok=True)

    print(f"\nIniciando: {rel}")
    inicio = datetime.now()

    # lê todo o arquivo
    raw = open(caminho_in, encoding=FORMATO).read()

    # 1) traduz <question> e <answer>
    raw = await process_sections(raw, 'question', session)
    raw = await process_sections(raw, 'answer',   session)

    # 2) traduz todo o HTML dentro de CDATA em <Contents>
    raw = await process_cdata_html(raw, session)

    # grava resultado
    with open(caminho_out, 'w', encoding=FORMATO) as f:
        f.write(raw)

    print(f"✅ Salvo: {rel} (tempo: {datetime.now()- inicio})")

async def main():
    async with aiohttp.ClientSession() as session:
        # processa somente arquivos .xml
        for raiz, _, arquivos in os.walk(DIR_ORIGEM):
            for arq in sorted(arquivos):
                if not arq.lower().endswith('.xml'):
                    continue
                await process_file(session, os.path.join(raiz, arq))
    print("\n🎉 Todas as traduções concluídas.")

if __name__ == '__main__':
    asyncio.run(main())

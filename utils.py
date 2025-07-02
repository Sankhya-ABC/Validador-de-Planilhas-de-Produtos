import unicodedata
import re

def limpar_para_contagem(texto):
    if texto is None:
        return ''
    texto = unicodedata.normalize('NFC', str(texto))
    texto = ''.join(ch for ch in texto if not unicodedata.category(ch).startswith('C'))
    texto = re.sub(r'\s+', ' ', texto)
    return texto.strip()

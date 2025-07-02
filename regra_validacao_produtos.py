import re
import pandas as pd
from utils import limpar_para_contagem

OPCOES_USO_PROD = {"1", "2", "4", "B", "C", "D", "E", "F", "I", "M", "O", "P", "R", "T", "V"}
OPCOES_UNIDADE = {"CX", "DZ", "GR", "HR", "KG", "KW", "LT", "ML", "MT", "PC", "PT", "TN", "UN"}
OPCOES_IDENTIF_IMOBILIZADO = {"1", "2", "3", "4", "5", "6", "99"}
OPCOES_UTILIZ_IMOBILIZADO = {"1", "2", "3", "9"}

REGRAS_PRODUTO = {
    "GRUPO_PAI": {"obrigatorio": True, "tipo": "alfanumerico", "max_tamanho": 30},
    "GRUPO_FILHO": {"obrigatorio": False, "tipo": "alfanumerico", "max_tamanho": 30},
    "GRUPO_NETO": {"obrigatorio": False, "tipo": "alfanumerico", "max_tamanho": 30},
    "GRUPO_BISNETO": {"obrigatorio": False, "tipo": "alfanumerico", "max_tamanho": 30},
    "COD_SIST_ANTERIOR": {"obrigatorio": False, "tipo": "alfanumerico", "max_tamanho": None},
    "DESCR_PROD": {"obrigatorio": True, "tipo": "alfanumerico", "max_tamanho": 100},
    "COMPLEMENTO": {"obrigatorio": False, "tipo": "alfanumerico", "max_tamanho": 100},
    "USO_PROD": {"obrigatorio": True, "tipo": "alfanumerico", "max_tamanho": 1, "opcoes": OPCOES_USO_PROD},
    "UNIDADE": {"obrigatorio": True, "tipo": "alfanumerico", "max_tamanho": 2, "opcoes": OPCOES_UNIDADE},
    "COD_BARRAS": {"obrigatorio": False, "tipo": "alfanumerico", "max_tamanho": 15},
    "NCM": {"obrigatorio": True, "tipo": "numerico", "max_tamanho": 8},
    "MARCA": {"obrigatorio": False, "tipo": "alfanumerico", "max_tamanho": 20},
    "REF_FORN": {"obrigatorio": False, "tipo": "alfanumerico", "max_tamanho": 30},
    "IDENTIF_IMOBILIZADO": {"obrigatorio": False, "tipo": "numerico", "max_tamanho": 2, "opcoes": OPCOES_IDENTIF_IMOBILIZADO},
    "UTILIZ_IMOBILIZADO": {"obrigatorio": False, "tipo": "numerico", "max_tamanho": 1, "opcoes": OPCOES_UTILIZ_IMOBILIZADO},
}

def limpar_valor(valor, coluna=None):
    if valor is None:
        return ''
    val_str = str(valor).strip()
    if coluna in ["COD_BARRA", "NCM", "IDENTIF_IMOBILIZADO", "UTILIZ_IMOBILIZADO"]:
        val_str = re.sub(r"[\.\-,\s]", "", val_str)
    return val_str

def is_vazio(valor):
    if valor is None:
        return True
    val = str(valor).strip().lower()
    return val == "" or val in {"nan", "none"}

def validar_campo_basico(coluna, valor, regra):
    if valor is None or (isinstance(valor, float) and pd.isna(valor)):
        if regra.get("obrigatorio", False):
            return False, "Campo obrigatorio não preenchido"
        return True, None
    val_original = str(valor).strip()
    if val_original == "":
        if regra.get("obrigatorio", False):
            return False, "Campo obrigatório não preenchido"
        return True, None
    val_str = limpar_valor(val_original, coluna)
    tipo = regra.get("tipo")
    if tipo == "alfanumerico":
        contagem = len(limpar_para_contagem(val_str))
        max_t = regra.get("max_tamanho")
        if max_t is not None and contagem > max_t:
            return False, f"Tamanho excede máximo de {max_t} (encontrador {contagem})"
    elif tipo == "numerico":
        if val_str == "":
            if regra.get("obrigatorio", False):
                return False, "Campo obrigatório não preenchido"
            return True, None
        if not re.fullmatch(r"\d+", val_str):
            return False, "Deve conter apenas dígitos"
        max_t = regra.get("max_tamanho")
        if max_t is not None and len(val_str) > max_t:
            return False, f"Tamanho exece máximo de {max_t} dígitos"
    opcoes = regra.get("opcoes")
    if opcoes is not None and val_str not in opcoes:
        return False, f"Valor '{'{valor_original}'} não está entre opções permitidas"
    return True, None

def validar_linha_produto(row: pd.Series, regras=REGRAS_PRODUTO):
    erros = []
    for coluna, regra in regras.items():
        valor = row.get(coluna)
        ok, msg = validar_campo_basico(coluna, valor, regra)
        if not ok:
            erros.append(f"{coluna}: {msg}")
    val_ncm = row.get("NCM")
    if val_ncm is not None and not (isinstance(val_ncm, float) and pd.isna(val_ncm)) and str(val_ncm).strip() != "":
        val_original = str(val_ncm).strip()
        val_str = limpar_valor(val_original, "NCM")
        if val_str == "":
            erros.append("NCM: valor vazio após limpeza")
        elif not re.fullmatch(r"\d+", val_str):
            erros.append("NCM: deve conter apenas dígitos após limpar pontuação")
        elif len(val_str) > 8:
            erros.append(f"NCM: possui mais de 8 dígitos ('{val_str}')")
    gf = row.get("GRUPO_FILHO"); gn = row.get("GRUPO_NETO"); gb = row.get("GRUPO_BISNETO")
    if gn and str(gn).strip() != "" and (not gf or str(gf).strip() == ""):
        erros.append("GRUPO_FILHO: obrigatorio quando GRUPO_NETO está preenchido")
    if gb and str(gb).strip() != "" and (not gn or str(gn).strip() == ""):
        erros.append("GRUPO_NETO: obrigatório quando GRUPO_BISNETO está preenchido")
    uso = row.get("USO_PROD")
    uso_str = str(uso).strip() if uso is not None else None
    ident = row.get("IDENTIF_IMOBILIZADO")
    util = row.get("UTILIZ_IMOBILIZADO")
    if uso_str == "I":
        if is_vazio(ident):
            erros.append("IDENTIF_IMOBILIZADO: obrigatório quando USO_PROD = 'I'")
        else:
            orig = str(ident).strip(); s = limpar_valor(orig, "IDENTIF_IMOBILIZADO")
            if not re.fullmatch(r"\d+", s):
                erros.append("IDENTIF_IMOBILIZADO: deve conter apenas dígitos após limpeza")
            elif s not in OPCOES_IDENTIF_IMOBILIZADO:
                erros.append(f"IDENTIF_IMOBILIZADO: '{orig}' não está entre opções permitidas")
        if is_vazio(ident):
            erros.append("IDENTIF_IMOBILIZADO: obrigatório quando USO_PROD = 'I'")
        else:
            orig = str(util).strip(); s = limpar_valor(orig, "UTILIZ_IMOBILIZADO")
            if not re.fullmatch(r"\d+", s):
                erros.append("UTILIZ_IMOBILIZADO: deve conter apenas dígitos após limpeza")
            elif s not in OPCOES_UTILIZ_IMOBILIZADO:
                erros.append(f"UTILIZ_IMOBILIZADO: '{orig}' não está entre opções permitidas")
    else:
        if not is_vazio(ident):
            erros.append("IDENTIF_IMOBILIZADO: deve estar vazio quando USO_PROD ≠ 'I'")
        if not is_vazio(util):
            erros.append("UTILIZ_IMOBILIZADO: deve estar vazio quando USO_PROD ≠ 'I'")
    return (False, erros) if erros else (True, [])
    
"""Monta o comprovante "PAGAMENTO PIX" (texto de preview e bytes ESC/POS)."""
from dataclasses import dataclass
from datetime import date

ESC = b"\x1b"
GS = b"\x1d"

# Largura em caracteres (fonte A) por largura de papel
COLUNAS = {"80mm": 48, "58mm": 32}


@dataclass
class Recibo:
    nome: str = ""
    qtd_show: str = ""
    comissoes: str = ""
    total: str = ""
    responsavel: str = ""
    data: str = ""  # DD/MM/AAAA; vazio => linha em branco para escrever a mão

    @staticmethod
    def hoje() -> str:
        return date.today().strftime("%d/%m/%Y")


VALOR_SHOW = 90
VALOR_COMISSAO = 5


def _inteiro(texto: str) -> int:
    try:
        return max(0, int(texto.strip()))
    except ValueError:
        return 0


def calcular_total(qtd_show: str, comissoes: str) -> str:
    """Total = shows x R$ 90 + comissões x R$ 5, formatado 'R$ 95,00' ('' se ambos vazios)."""
    if not qtd_show.strip() and not comissoes.strip():
        return ""
    total = _inteiro(qtd_show) * VALOR_SHOW + _inteiro(comissoes) * VALOR_COMISSAO
    return f"R$ {total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _campo(rotulo: str, valor: str, colunas: int) -> str:
    """'ROTULO: valor' (sem linhas de preenchimento)."""
    valor = " ".join(valor.split())
    return (f"{rotulo}: {valor}" if valor else f"{rotulo}:")[:colunas]


def _data(valor: str, colunas: int) -> str:
    rotulo = "DATA"
    if valor:
        corpo = f"{rotulo}: {valor}"
    else:
        corpo = f"{rotulo}: ____/____/______"
    return corpo.center(colunas).rstrip()


def linhas(r: Recibo, colunas: int = 48) -> list[str]:
    """Linhas de texto do comprovante (usadas no preview e na impressão)."""
    return [
        "PAGAMENTO PIX".center(colunas),
        "",
        _campo("NOME", r.nome, colunas),
        "",
        _campo("QTD SHOW", r.qtd_show, colunas),
        "",
        _campo("COMISSÕES", r.comissoes, colunas),
        "",
        _campo("TOTAL", r.total or calcular_total(r.qtd_show, r.comissoes), colunas),
        "",
        _campo("RESPONSAVEL", r.responsavel, colunas),
        "",
        _data(r.data, colunas),
    ]


def escpos(r: Recibo, colunas: int = 48, codepage: int = 3, cortar: bool = True) -> bytes:
    """Bytes ESC/POS. codepage 3 = CP860 (português) em impressoras Epson."""
    enc = "cp860"
    txt = linhas(r, colunas)

    def t(s: str) -> bytes:
        return s.encode(enc, errors="replace")

    out = bytearray()
    out += ESC + b"@"                      # inicializa
    out += ESC + b"t" + bytes([codepage])  # tabela de caracteres
    out += ESC + b"a\x01" + ESC + b"E\x01"  # centro + negrito
    out += GS + b"!\x11"                   # título em dobro (largura/altura)
    out += t(txt[0].strip()) + b"\n"
    out += GS + b"!\x00" + ESC + b"E\x00" + ESC + b"a\x00"
    out += b"\n"
    for linha in txt[2:]:
        if linha.strip() == "":
            out += b"\n"
            continue
        out += ESC + b"E\x01" + t(linha) + ESC + b"E\x00" + b"\n"
    out += b"\n\n\n"
    if cortar:
        out += GS + b"V\x42\x00"           # avança e corta (parcial)
    return bytes(out)

"""Monta o comprovante "PAGAMENTO PIX" (texto de preview e bytes ESC/POS)."""
import textwrap
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


VALORES_SHOW = (60, 50)  # valor por show conforme a pessoa
VALOR_SHOW = VALORES_SHOW[0]  # padrão
VALOR_COMISSAO = 5


def _inteiro(texto: str) -> int:
    try:
        return max(0, int(texto.strip()))
    except ValueError:
        return 0


def calcular_total(qtd_show: str, comissoes: str, valor_show: int = VALOR_SHOW) -> str:
    """Total = shows x valor_show (R$ 60 ou 50) + comissões x R$ 5, formatado 'R$ 95,00' ('' se ambos vazios)."""
    if not qtd_show.strip() and not comissoes.strip():
        return ""
    total = _inteiro(qtd_show) * valor_show + _inteiro(comissoes) * VALOR_COMISSAO
    return f"R$ {total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


# Tamanhos (GS ! n): 0x11 = dobro largura+altura, 0x01 = dobro altura
GRANDE, ALTO = 0x11, 0x01


def blocos(r: Recibo, colunas: int = 48) -> list[tuple[str, int]]:
    """Lista de (texto, tamanho): uma linha por campo, bloco centralizado no papel
    (a centralização é feita com espaços, na largura do tamanho escolhido).

    Papel largo (80 mm): dobro de largura e altura (colunas//2 caracteres).
    Papel estreito (58 mm): só dobro de altura, para caber o texto.
    """
    tam = GRANDE if colunas >= 48 else ALTO
    larg = colunas // 2 if tam == GRANDE else colunas
    total = r.total or calcular_total(r.qtd_show, r.comissoes)
    campos = [
        ("NOME", r.nome),
        ("QTD SHOW", r.qtd_show),
        ("COMISSÕES", r.comissoes),
        ("TOTAL", total),
        ("RESPONSAVEL", r.responsavel),
        ("DATA", r.data or "____/____/______"),
    ]
    corpo: list[str] = []
    for rotulo, valor in campos:
        valor = " ".join(valor.split())
        texto = f"{rotulo}: {valor}" if valor else f"{rotulo}:"
        corpo += textwrap.wrap(texto, larg, break_long_words=True)
    margem = " " * ((larg - max(len(l) for l in corpo)) // 2)  # bloco centralizado, texto alinhado
    return [("PAGAMENTO PIX".center(larg).rstrip(), tam), ("", 0)] + [(margem + l, tam) for l in corpo]


def linhas(r: Recibo, colunas: int = 48) -> list[str]:
    """Texto centralizado para a prévia na tela."""
    # largura útil = colunas//2 em tamanho dobrado; centraliza esse bloco na prévia
    out = []
    for t, tam in blocos(r, colunas):
        util = colunas // 2 if tam == GRANDE else colunas
        out.append(" " * ((colunas - util) // 2) + t)
    return out


def escpos(r: Recibo, colunas: int = 48, codepage: int = 3, cortar: bool = True) -> bytes:
    """Bytes ESC/POS. codepage 3 = CP860 (português) em impressoras Epson."""
    out = bytearray()
    out += ESC + b"@"                        # inicializa
    out += ESC + b"t" + bytes([codepage])    # tabela de caracteres
    out += ESC + b"a\x00" + ESC + b"E\x01"   # esquerda (margem já embutida) + negrito
    for texto, tam in blocos(r, colunas):
        out += GS + b"!" + bytes([tam])
        out += texto.encode("cp860", errors="replace") + b"\n"
    out += GS + b"!\x00" + ESC + b"E\x00"
    out += b"\n\n\n"
    if cortar:
        out += GS + b"V\x42\x00"             # avança e corta (parcial)
    return bytes(out)

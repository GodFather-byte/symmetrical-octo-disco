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
TITULO, ROTULO, VALOR = 0x11, 0x01, 0x11


def blocos(r: Recibo, colunas: int = 48) -> list[tuple[str, int]]:
    """Lista de (texto, tamanho). Tudo centralizado; '' = linha em branco.

    Em tamanho dobrado cabem colunas//2 caracteres por linha, então valores
    longos são quebrados em mais de uma linha.
    """
    larg = colunas // 2
    total = r.total or calcular_total(r.qtd_show, r.comissoes)
    campos = [
        ("NOME", r.nome),
        ("QTD SHOW", r.qtd_show),
        ("COMISSÕES", r.comissoes),
        ("TOTAL", total),
        ("RESPONSAVEL", r.responsavel),
        ("DATA", r.data or "____/____/______"),
    ]
    out: list[tuple[str, int]] = [("PAGAMENTO PIX", TITULO), ("", 0)]
    for rotulo, valor in campos:
        out.append((rotulo, ROTULO))
        valor = " ".join(valor.split())
        for linha in textwrap.wrap(valor, larg, break_long_words=True) or [""]:
            out.append((linha, VALOR))
        out.append(("", 0))
    return out


def linhas(r: Recibo, colunas: int = 48) -> list[str]:
    """Texto centralizado para a prévia na tela."""
    return [t.center(colunas).rstrip() for t, _ in blocos(r, colunas)]


def escpos(r: Recibo, colunas: int = 48, codepage: int = 3, cortar: bool = True) -> bytes:
    """Bytes ESC/POS. codepage 3 = CP860 (português) em impressoras Epson."""
    out = bytearray()
    out += ESC + b"@"                        # inicializa
    out += ESC + b"t" + bytes([codepage])    # tabela de caracteres
    out += ESC + b"a\x01" + ESC + b"E\x01"   # centralizado + negrito
    for texto, tam in blocos(r, colunas):
        out += GS + b"!" + bytes([tam])
        out += texto.encode("cp860", errors="replace") + b"\n"
    out += GS + b"!\x00" + ESC + b"E\x00" + ESC + b"a\x00"
    out += b"\n\n\n"
    if cortar:
        out += GS + b"V\x42\x00"             # avança e corta (parcial)
    return bytes(out)

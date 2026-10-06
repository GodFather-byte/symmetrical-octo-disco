"""Envio de bytes RAW para impressora instalada no Windows (spooler)."""
import sys


def disponivel() -> bool:
    return sys.platform == "win32"


def listar() -> list[str]:
    if not disponivel():
        return []
    import win32print

    flags = win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS
    return [p[2] for p in win32print.EnumPrinters(flags)]


def padrao() -> str:
    if not disponivel():
        return ""
    import win32print

    try:
        return win32print.GetDefaultPrinter()
    except Exception:
        return ""


def sugerida(nomes: list[str]) -> str:
    """Prefere uma impressora Epson/TM; senão a padrão do Windows."""
    for n in nomes:
        low = n.lower()
        if "epson" in low or "tm-" in low or "tm_" in low:
            return n
    p = padrao()
    return p if p in nomes else (nomes[0] if nomes else "")


def imprimir(nome: str, dados: bytes, titulo: str = "Pagamento PIX") -> None:
    if not disponivel():
        raise RuntimeError("Impressão só funciona no Windows.")
    import win32print

    h = win32print.OpenPrinter(nome)
    try:
        win32print.StartDocPrinter(h, 1, (titulo, None, "RAW"))
        try:
            win32print.StartPagePrinter(h)
            win32print.WritePrinter(h, dados)
            win32print.EndPagePrinter(h)
        finally:
            win32print.EndDocPrinter(h)
    finally:
        win32print.ClosePrinter(h)

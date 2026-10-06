"""Interface (Tkinter) para preencher e imprimir o comprovante PAGAMENTO PIX."""
import json
import os
import tkinter as tk
from tkinter import messagebox, ttk

from . import __version__, printer
from .ticket import COLUNAS, VALOR_COMISSAO, VALOR_SHOW, Recibo, calcular_total, escpos, linhas

CONFIG = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "ReciboPix.json")

CAMPOS = [
    ("nome", "Nome"),
    ("qtd_show", "Qtd Show"),
    ("comissoes", "Comissões"),
    ("total", "Total"),
    ("responsavel", "Responsável"),
]


def _carregar() -> dict:
    try:
        with open(CONFIG, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _salvar(cfg: dict) -> None:
    try:
        with open(CONFIG, "w", encoding="utf-8") as f:
            json.dump(cfg, f)
    except Exception:
        pass


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"Pagamento PIX - Impressão  v{__version__}")
        self.resizable(False, False)
        cfg = _carregar()
        self.vars = {k: tk.StringVar() for k, _ in CAMPOS}
        self.vars["data"] = tk.StringVar(value=Recibo.hoje())
        self.papel = tk.StringVar(value=cfg.get("papel", "80mm"))
        self.impressora = tk.StringVar()
        self.copias = tk.IntVar(value=1)
        self._montar(cfg)
        for k in ("qtd_show", "comissoes"):
            self.vars[k].trace_add("write", lambda *_: self.vars["total"].set(
                calcular_total(self.vars["qtd_show"].get(), self.vars["comissoes"].get())))
        for v in self.vars.values():
            v.trace_add("write", lambda *_: self._preview())
        self.papel.trace_add("write", lambda *_: self._preview())
        self._preview()
        self.bind("<Control-p>", lambda e: self.imprimir())

    def _montar(self, cfg):
        pad = {"padx": 8, "pady": 4}
        f = ttk.Frame(self, padding=10)
        f.grid(row=0, column=0, sticky="nsew")

        self.entradas = []
        for i, (k, rotulo) in enumerate(CAMPOS):
            ttk.Label(f, text=rotulo).grid(row=i, column=0, sticky="w", **pad)
            e = ttk.Entry(f, textvariable=self.vars[k], width=34)
            e.grid(row=i, column=1, **pad)
            if k == "total":  # calculado automaticamente
                e.configure(state="readonly")
                ttk.Label(f, text=f"(show R$ {VALOR_SHOW} + comissão R$ {VALOR_COMISSAO})", foreground="#666").grid(row=i, column=2, sticky="w")
            else:
                self.entradas.append(e)
        n = len(CAMPOS)
        ttk.Label(f, text="Data").grid(row=n, column=0, sticky="w", **pad)
        e = ttk.Entry(f, textvariable=self.vars["data"], width=14)
        e.grid(row=n, column=1, sticky="w", **pad)
        self.entradas.append(e)
        # Enter: vai para o próximo campo; no último (Data), imprime.
        for i, e in enumerate(self.entradas):
            if i + 1 < len(self.entradas):
                e.bind("<Return>", lambda ev, nxt=self.entradas[i + 1]: (nxt.focus_set(), nxt.select_range(0, "end"), "break")[-1])
            else:
                e.bind("<Return>", lambda ev: (self.imprimir(), "break")[-1])
        self.entradas[0].focus_set()

        ttk.Separator(f).grid(row=n + 1, column=0, columnspan=2, sticky="ew", pady=6)

        ttk.Label(f, text="Impressora").grid(row=n + 2, column=0, sticky="w", **pad)
        nomes = printer.listar()
        self.cb = ttk.Combobox(f, textvariable=self.impressora, values=nomes, width=32, state="readonly")
        self.cb.grid(row=n + 2, column=1, **pad)
        self.impressora.set(cfg.get("impressora") if cfg.get("impressora") in nomes else printer.sugerida(nomes))

        ttk.Label(f, text="Papel").grid(row=n + 3, column=0, sticky="w", **pad)
        pf = ttk.Frame(f)
        pf.grid(row=n + 3, column=1, sticky="w", **pad)
        for p in COLUNAS:
            ttk.Radiobutton(pf, text=p, value=p, variable=self.papel).pack(side="left", padx=4)
        ttk.Label(pf, text="  Cópias").pack(side="left")
        ttk.Spinbox(pf, from_=1, to=10, width=3, textvariable=self.copias).pack(side="left", padx=4)

        bf = ttk.Frame(f)
        bf.grid(row=n + 4, column=0, columnspan=2, pady=8)
        ttk.Button(bf, text="Imprimir (Ctrl+P)", command=self.imprimir).pack(side="left", padx=6)
        ttk.Button(bf, text="Limpar", command=self.limpar).pack(side="left", padx=6)

        self.prev = tk.Text(f, width=50, height=15, font=("Courier New", 9), bg="#fffef2", state="disabled")
        self.prev.grid(row=n + 5, column=0, columnspan=2, **pad)

    def _recibo(self) -> Recibo:
        return Recibo(**{k: v.get() for k, v in self.vars.items()})

    def _preview(self):
        col = COLUNAS[self.papel.get()]
        self.prev.configure(state="normal", width=col + 2)
        self.prev.delete("1.0", "end")
        self.prev.insert("1.0", "\n".join(linhas(self._recibo(), col)))
        self.prev.configure(state="disabled")

    def limpar(self):
        for k, v in self.vars.items():
            v.set(Recibo.hoje() if k == "data" else "")
        self.entradas[0].focus_set()

    def imprimir(self):
        nome = self.impressora.get()
        if not nome:
            messagebox.showerror("Impressora", "Nenhuma impressora selecionada/instalada.")
            return
        try:
            dados = escpos(self._recibo(), COLUNAS[self.papel.get()]) * max(1, int(self.copias.get()))
            printer.imprimir(nome, dados)
        except Exception as e:  # noqa: BLE001
            messagebox.showerror("Erro ao imprimir", str(e))
            return
        _salvar({"impressora": nome, "papel": self.papel.get()})
        self.limpar()  # pronto para o próximo recibo


def main():
    App().mainloop()

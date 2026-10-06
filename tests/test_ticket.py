from recibo_pix.ticket import Recibo, escpos, linhas


def test_linhas_largura():
    for col in (48, 32):
        for l in linhas(Recibo(nome="João", total="R$ 100,00", data="06/10/2026"), col):
            assert len(l) <= col


def test_campos_preenchidos():
    txt = "\n".join(linhas(Recibo(nome="João", comissoes="10%", responsavel="Ana", data="06/10/2026")))
    assert "NOME: João" in txt and "COMISSÕES: 10%" in txt and "RESPONSAVEL: Ana" in txt and "_" not in txt.split("DATA")[0]
    assert "DATA: 06/10/2026" in txt


def test_data_vazia_mostra_linha():
    assert "____/____/______" in "\n".join(linhas(Recibo()))


def test_escpos():
    b = escpos(Recibo(comissoes="é"))
    assert b.startswith(b"\x1b@") and b.endswith(b"\x1dV\x42\x00")
    assert "COMISSÕES".encode("cp860") in b


def test_total():
    from recibo_pix.ticket import calcular_total
    assert calcular_total("1", "1") == "R$ 95,00"
    assert calcular_total("3", "2") == "R$ 280,00"
    assert calcular_total("15", "") == "R$ 1.350,00"
    assert calcular_total("", "") == ""

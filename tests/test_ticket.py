from recibo_pix.ticket import Recibo, blocos, escpos, linhas


def test_linhas_largura():
    for col in (48, 32):
        r = Recibo(nome="Maria Aparecida dos Santos Oliveira", total="R$ 100,00", data="06/10/2026")
        for l in linhas(r, col):
            assert len(l) <= col
        for t, tam in blocos(r, col):
            assert len(t) <= (col if tam == 0x01 else col // 2)
    assert len(blocos(Recibo(), 48)) == 8  # compacto: título + 6 campos


def test_campos_preenchidos():
    txt = "\n".join(linhas(Recibo(nome="João", qtd_show="1", comissoes="1", responsavel="Ana", data="06/10/2026")))
    for esperado in ("NOME", "João", "COMISSÕES", "R$ 65,00", "RESPONSAVEL", "Ana", "06/10/2026"):
        assert esperado in txt


def test_data_vazia_mostra_linha():
    assert "____/____/______" in "\n".join(linhas(Recibo()))


def test_escpos():
    b = escpos(Recibo(comissoes="é"))
    assert b.startswith(b"\x1b@") and b.endswith(b"\x1dV\x42\x00")
    assert b"\x1d!\x11" in b
    assert "COMISSÕES".encode("cp860") in b


def test_total():
    from recibo_pix.ticket import calcular_total
    assert calcular_total("1", "1") == "R$ 65,00"
    assert calcular_total("1", "1", 50) == "R$ 55,00"
    assert calcular_total("3", "2") == "R$ 190,00"
    assert calcular_total("3", "2", 50) == "R$ 160,00"
    assert calcular_total("20", "") == "R$ 1.200,00"
    assert calcular_total("", "") == ""

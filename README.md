# Recibo PIX – impressão em impressora térmica Epson

Programa para Windows que preenche e imprime o comprovante **PAGAMENTO PIX**
(Nome, Qtd Show, Comissões, Total, Responsável, Data) em impressora térmica
Epson (ESC/POS, ex.: TM-T20, TM-T88), papel 80 mm ou 58 mm.

## Instalar (usuário)
1. Em **Actions → Build Windows** baixe o artefato `ReciboPix-Setup` (ou a *Release*, se houver).
2. Execute `ReciboPix-Setup.exe` e siga o instalador (cria atalho na Área de Trabalho).
3. Instale o driver da Epson normalmente no Windows; o programa lista as impressoras instaladas.

## Uso
Preencha os campos, confira a prévia, escolha a impressora/papel e clique **Imprimir** (Ctrl+P).
Campos vazios saem como linha em branco para escrever à mão. Se a data ficar vazia, imprime `____/____/______`.

## Gerar o instalador manualmente
No Windows com Python 3.12+ (e Inno Setup 6 opcional): `build.bat`.

## Desenvolvimento
`python main.py` (a impressão só funciona no Windows) · `pytest tests`

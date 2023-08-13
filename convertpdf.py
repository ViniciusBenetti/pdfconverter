import PySimpleGUI as psg
from docx2pdf import convert
import time

psg.theme('LightBlue')
psg.set_options(font=('Nunito',12))
layout = [
    [psg.Text('')],
    [psg.Text('selecione o arquivo: (arquivos suportados: docx,doc,txt,bmp,jpg,png,jpeg)')],
    [psg.Input(key='arquivo'), psg.FileBrowse(('pesquisar'))],
    [psg.Text('escolha o nome do arquivo')],
    [psg.Input(key='nome')],
    [psg.Text('selecione o local que irá salvar:')],
    [psg.Input(key='salvar'), psg.FolderBrowse('pesquisar')],
    [psg.Button('converter'),psg.Button('sair'),psg.Text('',key='OUT')],
]
janela = psg.Window('converter para PDF',layout)

while True:
    evento, valores = janela.read()

    if evento == 'sair' or evento == psg.WINDOW_CLOSED:
        break

    elif evento == 'converter':
        if '.docx' in valores['arquivo'] or '.doc' in valores['arquivo']:
            try:
                convert(valores['arquivo'],valores['salvar']+'/'+valores['nome']+'.pdf')
                time.sleep(1)
                janela['OUT'].update('convertido!')

            except:
                janela['OUT'].update('erro ao converter arquivo word em pdf')



janela.close()




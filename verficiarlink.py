import mysql.connector
from datetime import date
import stopPhishing
import asyncio
import PySimpleGUI as sg


async def checkMessageFull(TEST_MESSAGE):
    isGrabber = await stopPhishing.checkMessage(TEST_MESSAGE)
    return isGrabber

current_user_id = None 

def obter_id_usuario(cur, nome_usuario, senha_usuario):
    cur.execute("SELECT id_usuario FROM usuario WHERE nome = %s AND senha = %s", (nome_usuario, senha_usuario))
    user_id = cur.fetchone()
    return user_id

def criar_usuario(cur, nome_usuario, senha_usuario):
    cur.execute("INSERT INTO usuario (nome, senha) VALUES (%s, %s)", (nome_usuario, senha_usuario))
    cur.execute("SELECT LAST_INSERT_ID()")  # Isso obtém o ID do último registro inserido.
    user_id = cur.fetchone()[0]
    return user_id

def obter_links_usuario(cur, user_id):

    try:
        cur.execute("SELECT * FROM link WHERE id_usuario = %s", (user_id))

    except:
        cur.execute("SELECT * FROM link WHERE id_usuario = %s", (user_id,))

    user_links = cur.fetchall()
    return user_links


conn = mysql.connector.connect(
        host="seuhost",
        user="seuusuario",
        password="suasenha",
        database="seudb"
    )


cur = conn.cursor()

usuario_tbl = """CREATE TABLE IF NOT EXISTS usuario (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    senha VARCHAR(255) NOT NULL
)"""
cur.execute(usuario_tbl)


link_tbl = """CREATE TABLE IF NOT EXISTS link (
    id_link INT AUTO_INCREMENT PRIMARY KEY,
    linkstr VARCHAR(255),
    id_usuario INT,
    criacao DATE NOT NULL,
    phishing BOOLEAN
)"""
cur.execute(link_tbl)


sg.theme('default')

layout = [
    [sg.Text('Digite o nome do seu usuário:'), sg.InputText(key='nome')],
    [sg.Text('Digite a senha do seu usuário:'), sg.InputText(key='senha')],
    [sg.Button('Autenticar/Criar Usuário')],
    [sg.Text('Digite o link que deseja validar:'), sg.InputText(key='link')],
    [sg.Button('Validar Link')],
    [sg.Text('', size=(30, 2), key='result')],
    [sg.Text('Links para este usuário:')],
    [sg.Multiline('', size=(30, 5), key='user_links', disabled=True, auto_refresh=True, text_color='black', background_color='white')]
]

window = sg.Window('Verificador de Malware', layout, font=('Times New Roman', 12))


while True:
    event, values = window.read()

    if event == sg.WINDOW_CLOSED:
        break

    if event == 'Autenticar/Criar Usuário':
        nome_usuario = values['nome']
        senha_usuario = values['senha']

        if not nome_usuario or not senha_usuario:
            window['result'].update("Nome e senha são campos obrigatórios.")
        else:
            user_id = obter_id_usuario(cur, nome_usuario, senha_usuario)

            if user_id:
                window['result'].update("Usuário autenticado com sucesso.")
                current_user_id = user_id
                current_user_id = int("".join(map(str, current_user_id)))
                window['nome'].update('')
                window['senha'].update('')

            else:
                window['result'].update("Usuário não autenticado. Criando um novo usuário...")
                user_id = criar_usuario(cur, nome_usuario, senha_usuario)
                current_user_id = user_id 
                window['result'].update(f"Novo usuário criado com ID {user_id}")
                window['nome'].update('')
                window['senha'].update('')

            user_links = obter_links_usuario(cur, current_user_id)
            user_links_text = [f"Link: {user_link[1]}\nData: {user_link[3]}\nMalware: {'Sim' if user_link[4] else 'Não'}\n" for user_link in user_links]
            window['user_links'].update('\n'.join(user_links_text))

    if event == 'Validar Link':
        link = values['link']
        data_criacao = date.today()

        if not link:
            window['result'].update("O campo de link é obrigatório.")
        else:
            async def main():
                global phishing
                phishing = await checkMessageFull(link)

            asyncio.run(main())

            if phishing:
                window['result'].update("Este link é perigoso")
            else:
                window['result'].update("Este link é seguro")


            cur.execute("INSERT INTO link (linkstr, criacao, phishing, id_usuario) VALUES (%s, %s, %s, %s)", (link, data_criacao, phishing, current_user_id))
            conn.commit()


            user_links = obter_links_usuario(cur, current_user_id)
            user_links_text = [f"Link: {user_link[1]}\nData: {user_link[3]}\nRisco: {'Sim' if user_link[4] else 'Não'}\n" for user_link in user_links]
            window['user_links'].update('\n'.join(user_links_text))



cur.close()
conn.close()

from urllib import response
import PySimpleGUI as sg
from flask import request
import requests 
from datetime import datetime
import qrcode

porta = str(open("porta.txt", "r").read())

def get_node_add():
    requests.get(f"http://localhost:{porta}/mine")
    return str(requests.get(f"http://localhost:{porta}/chain").json()["chain"][-1]["transactions"][-1]["recipient"])

def chain():

    data =requests.get(f"http://localhost:{porta}/chain").json()["chain"]
    
    report = ""

    for blocos in data:
        setor0 = (f'\n')
        setor1 =(f"""---Informação do Bloco {blocos["index"]}---
        previous_hash: {blocos["previous_hash"]}
        proof: {blocos["proof"]}
        Data: {datetime.utcfromtimestamp(blocos["timestamp"]).strftime('%Y-%m-%d %H:%M:%S')}
        """)
        report += setor0
        report +=setor1
        for trans in blocos["transactions"]:
            if trans["sender"] == "0":
                senderinfo = "Blockchain - Recompensa de mineração"
            else:
                senderinfo = trans["sender"]
            
            setor2 = (f"""\nTransações no Bloco:
        Valor: {trans["amount"]} 
        De: {senderinfo} 
        Para: {trans["recipient"]}  
        """)
            report += setor2
    

    coluna1 = [[sg.Text(report)]]    
    
    layout = [

        [sg.Text("Corrente de transações", key="new")],
        [sg.Column(coluna1, scrollable=True,  vertical_scroll_only=True)]

        ]
    
    window = sg.Window("transações", layout, modal=True)
    choice = None
    
    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        
    window.close()

def minerar():


    requests.get(f"http://localhost:{porta}/mine")

    layout = [[sg.Text("Novo bloco minerado, 1 moeda foi adicionado à sua carteira", key="new")]]
    window = sg.Window("Minerar Bloco", layout, modal=True)
    choice = None
    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        
    window.close()


def fazer_transacao():
    response = ""

    layout = [
    [sg.Text('Fazer uma transação: ')],
    [sg.Text('ID da carteira: ', size =(15, 1)), sg.InputText()],
    [sg.Text('Valor:', size =(15, 1)), sg.InputText()],
    [sg.Submit(), sg.Cancel()]
]
    window = sg.Window("transação", layout, modal=True)

    event, values = window.read()
        
    rep = str(get_node_add())
        
    response = requests.post(f"http://localhost:{porta}/transactions/new", json={"sender":rep,"recipient":values[0],"amount":values[1]})
        
    window.close()
    
    sg.Popup(response.json()["message"]) 


def add_node():

    ip_valido = (5000 <= int(porta) < 6000)

    layout = [
    [sg.Text('Porta do Node: ')],
    #[sg.Text('endereço: ', size =(15, 1)), sg.InputText()],
    [sg.Text('porta: ', size =(15, 1)), sg.InputText()],
    [sg.Submit(), sg.Cancel()]
]
    window = sg.Window("Adicionar Node", layout, modal=True)
    

    event, values = window.read()
    window.close()

    if ip_valido:
        

        link = f"localhost:{values[0]}"

        response = requests.post(f"http://localhost:{porta}/nodes/register", json={"nodes":[link]})

        sg.Popup(response.json()["message"]) 
        
    else:
        sg.Popup("A porta não é valida")


def ping_node():
    
    response = requests.get(f"http://localhost:{porta}/nodes/resolve")

    layout = [[sg.Text(response.json()["message"], key="new")]]
    window = sg.Window("ping", layout, modal=True)

    choice = None
    
    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        
    window.close()

def qrcode_criar(input_data):
    qr = qrcode.QRCode(
        version=1,
        box_size=6,
        border=3)
    
    qr.add_data(input_data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    img.save('qrcode001.png')

    return "qrcode001.png"


geral = [
    
    [sg.Text("A minha conta")],
    [sg.Text(f"porta {str(porta)}")],
    [sg.Text("Node address:")],
    [sg.InputText(str(get_node_add()),use_readonly_for_disable=True, disabled=True, key='-IN-')],
    [sg.Image(qrcode_criar(str(get_node_add())))]
]

ops = [

    [sg.Text("Opções:")],
    [sg.Button("Minerar novo bloco")],
    [sg.Button("Ver transações")],
    [sg.Button("Fazer uma transação")],
    [sg.Button("Adicionar Node")],
    [sg.Button("Ping Nodes")],
    [sg.Button("Sair")]
]

layout0 = [
    
    [sg.Column(geral),
     sg.VSeperator(),
     sg.Column(ops),]
]


window = sg.Window("BlockChain", layout0)

while True:
    event, values = window.read()

    if event == "Sair" or event == sg.WIN_CLOSED:
        break


    if event == "Ver transações":
        chain()

    if event == "Minerar novo bloco":
        minerar()
    
    if event == "Fazer uma transação":
        fazer_transacao()

    if event == "Adicionar Node":
        add_node()
    
    if event == "Ping Nodes":
        ping_node()

window.close()

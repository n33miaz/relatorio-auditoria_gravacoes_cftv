import os
import requests
from datetime import datetime

CLIENTE = ""
CAMINHO_BASE = r"D:\Intelbras\LocalRecording" 
TECNOLOGIA = "IntelBras"

API_URL = "http://10.201.1.1:5000/report" # Endereço IPv4 (centralizador)

def gerar_dados_relatorio():
    if not os.path.exists(CAMINHO_BASE):
        return {"cliente": CLIENTE, "tecnologia": TECNOLOGIA, "antiga": "Nenhuma", "recente": "Nenhuma", "qtd": 0}

    datas = []
    try:
        for ano in os.listdir(CAMINHO_BASE):
            ano_path = os.path.join(CAMINHO_BASE, ano)
            if os.path.isdir(ano_path):
                for mes in os.listdir(ano_path):
                    mes_path = os.path.join(ano_path, mes)
                    if os.path.isdir(mes_path):
                        for dia in os.listdir(mes_path):
                            dia_path = os.path.join(mes_path, dia)
                            if os.path.isdir(dia_path):
                                for arq in os.listdir(dia_path):
                                    arq_path = os.path.join(dia_path, arq)
                                    if os.path.isfile(arq_path):
                                        datas.append(datetime.fromtimestamp(os.path.getmtime(arq_path)))
    except Exception as e:
        print(f"Erro ao ler diretórios: {e}")
        return {"cliente": CLIENTE, "tecnologia": TECNOLOGIA, "antiga": "Erro", "recente": "Erro", "qtd": 0}

    if not datas:
        return {"cliente": CLIENTE, "tecnologia": TECNOLOGIA, "antiga": "Nenhuma", "recente": "Nenhuma", "qtd": 0}

    data_antiga = min(datas).strftime('%d/%m/%Y %H:%M:%S')
    data_recente = max(datas).strftime('%d/%m/%Y %H:%M:%S')
    total_dias = len(set([d.date() for d in datas]))

    return {"cliente": CLIENTE, "tecnologia": TECNOLOGIA, "antiga": data_antiga, "recente": data_recente, "qtd": total_dias}

def enviar_relatorio_para_api(dados):
    try:
        response = requests.post(API_URL, json=dados, timeout=10) 
        if response.status_code == 200:
            print(f"Relatório do cliente {CLIENTE} ({TECNOLOGIA}) enviado com sucesso para o servidor.")
        else:
            print(f"Erro ao enviar relatório. Servidor respondeu com: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Falha de comunicação ao tentar enviar relatório para {API_URL}. Erro: {e}")

if __name__ == "__main__":
    dados_do_relatorio = gerar_dados_relatorio()
    enviar_relatorio_para_api(dados_do_relatorio)
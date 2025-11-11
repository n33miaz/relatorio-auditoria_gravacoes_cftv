import os
import requests
from datetime import datetime

CLIENTE = "" 
CAMINHO_BASE = r"F:\iVMS\Videos\RecordFile" 
TECNOLOGIA = "iVMS"

API_URL = "http://10.201.1.1:5000/report" # Endereço IPv4 (centralizador)

def gerar_dados_relatorio():
    datas = []

    if not os.path.exists(CAMINHO_BASE):
        print(f"Erro: O caminho base '{CAMINHO_BASE}' não foi encontrado.")
        return {"cliente": CLIENTE, "tecnologia": TECNOLOGIA, "antiga": "Nenhuma", "recente": "Nenhuma", "qtd": 0}

    try:
        for pasta_data in os.listdir(CAMINHO_BASE):
            caminho_data = os.path.join(CAMINHO_BASE, pasta_data)
            if not os.path.isdir(caminho_data): continue

            for pasta_camera in os.listdir(caminho_data):
                caminho_camera = os.path.join(caminho_data, pasta_camera)
                if not os.path.isdir(caminho_camera): continue

                for arq in os.listdir(caminho_camera):
                    arq_path = os.path.join(caminho_camera, arq)
                    if os.path.isfile(arq_path):
                        try:
                            datas.append(datetime.fromtimestamp(os.path.getmtime(arq_path)))
                        except Exception:
                            continue
    except Exception as e:
        print(f"Erro ao ler diretórios em {CAMINHO_BASE}: {e}")
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
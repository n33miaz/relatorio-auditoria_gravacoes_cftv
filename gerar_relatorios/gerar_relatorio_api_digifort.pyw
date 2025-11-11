import os
import requests
from datetime import datetime

CLIENTE = ""  
CAMINHO_BASE = r"D:\\" 
TECNOLOGIA = "Digifort"

API_URL = "http://10.201.1.1:5000/report" # Endereço IPv4 (centralizador)

def gerar_dados_relatorio():
    datas = []

    if not os.path.exists(CAMINHO_BASE):
        print(f"Erro: O caminho base '{CAMINHO_BASE}' não foi encontrado.")
        return {"cliente": CLIENTE, "tecnologia": TECNOLOGIA, "antiga": "Nenhuma", "recente": "Nenhuma", "qtd": 0}

    for nome_camera in os.listdir(CAMINHO_BASE):
        pasta_dados = os.path.join(CAMINHO_BASE, nome_camera, "Dados")
        
        if not os.path.isdir(pasta_dados):
            continue

        try:
            for nome_arquivo in os.listdir(pasta_dados):
                if nome_arquivo.lower().endswith('.dar'):
                    caminho_arquivo = os.path.join(pasta_dados, nome_arquivo)
                    try:
                        data_modificacao = datetime.fromtimestamp(os.path.getmtime(caminho_arquivo))
                        datas.append(data_modificacao)
                    except FileNotFoundError:
                        continue 
        except PermissionError:
            print(f"Aviso: Sem permissão para acessar a pasta {pasta_dados}")
            continue
        except Exception as e:
            print(f"Erro inesperado ao processar a pasta {pasta_dados}: {e}")
            continue

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
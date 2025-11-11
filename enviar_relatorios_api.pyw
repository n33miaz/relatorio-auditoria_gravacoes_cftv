import os
import smtplib
import requests
import logging
import os
from datetime import datetime
from dotenv import load_dotenv 
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


load_dotenv()

API_URL_GET = "http://127.0.0.1:5000/get_reports"
API_URL_CLEAR = "http://127.0.0.1:5000/clear"

REMETENTE = "suporte1.ti@emailexemplo.com.br"
DESTINATARIOS = ["informatica@emailexemplo.com.br", "cftv@emailexemplo.com.br", "coordenador.cftv@emailexemplo.com.br"]
COPIA = ["gerente.ti@emailexemplo.com.br", "gerente.cftv@emailexemplo.com.br"]

ASSUNTO = "Auditoria Gravações CFTV" 
ASSINATURA_HTML = """
    <div style="margin-top: 25px;">
        <img src="https://i.ibb.co/tMn5RNkz/Assinatura-Neemias1.jpg" alt="Assinatura Neemias Cormino" style="width: 550px; height: auto;" />
    </div>
"""


def setup_logging():
    now = datetime.now()
    log_folder = os.path.join(r"C:\SCRIPTS\1 - RELATORIO DIARIO\CENTRALIZADOR\Logs\centralizador", now.strftime('%Y\\%m\\%d'))
    os.makedirs(log_folder, exist_ok=True)
    
    log_filename = now.strftime('run-enviar_relatorios_api-%Hh%M.log')
    log_file_path = os.path.join(log_folder, log_filename)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file_path, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    logging.info(f"Log desta execução salvo em: {log_file_path}")


def buscar_dados_da_api():
    try:
        response = requests.get(API_URL_GET, timeout=10)
        if response.status_code == 200:
            dados_api = response.json()
            lista_de_dados = [valor['data'] for valor in dados_api.values()]
            return lista_de_dados
        else:
            logging.error(f"Erro ao buscar dados da API. O servidor respondeu com status: {response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        logging.error(f"Não foi possível conectar ao servidor de API em {API_URL_GET}. Erro: {e}")
        return []


def gerar_tabela_html(dados_dict_list):
    html = """
    <html><head><style>
        body { font-family: Arial, sans-serif; font-size: 12px; text-align: center; }
        table { border-collapse: collapse; width: 90%; margin: auto; }
        th { background-color: #28a745; color: white; padding: 8px; border: 1px solid #ddd; font-weight: bold; }
        td { border: 1px solid #ddd; padding: 8px; background-color: #2e2e2e; color: white; }
        .alerta-qtd { color: red; font-weight: bold; }
        .status-ok { color: #28a745; font-weight: bold; }
        .status-atrasado { color: #dc3545; font-weight: bold; }
    </style></head>
    <body>
        <h4 style="text-align: center;">Relatório das Gravações Salvas</h4>
        <table>
            <tr><th>CLIENTE</th><th>TECNOLOGIA</th><th>MAIS ANTIGA</th><th>MAIS RECENTE</th><th>STATUS</th><th>QUANTIDADE</th></tr>
    """
    agora = datetime.now()
    
    dados_ordenados = sorted(dados_dict_list, key=lambda x: x['cliente'])
    
    for item in dados_ordenados:
        cliente = item.get('cliente', 'N/A')
        tecnologia = item.get('tecnologia', 'N/A')
        antiga_str = item.get('antiga', 'N/A')
        recente_str = item.get('recente', 'N/A')
        qtd = item.get('qtd', 0)
        
        qtd_style = "alerta-qtd" if int(qtd) < 30 else ""
        
        status_text = "OK"
        status_class = "status-ok"

        recente_display = recente_str.replace(" ", "<br>")
        antiga_display = antiga_str.replace(" ", "<br>")

        try:
            data_recente_obj = datetime.strptime(recente_str, '%d/%m/%Y %H:%M:%S')
            
            if (agora - data_recente_obj) > timedelta(hours=2):
                status_text = "Atrasado"
                status_class = "status-atrasado"

            recente_display = data_recente_obj.strftime('%d/%m/%Y<br>%Hh%M')
            
            if antiga_str not in ["Nenhuma", "Erro"]:
                data_antiga_obj = datetime.strptime(antiga_str, '%d/%m/%Y %H:%M:%S')
                antiga_display = data_antiga_obj.strftime('%d/%m/%Y<br>%Hh%M')

        except (ValueError, TypeError): 
            status_text = "Inválido"
            status_class = "status-atrasado"
            
        html += f"""
            <tr>
                <td>{cliente}</td>
                <td>{tecnologia}</td>
                <td>{antiga_display}</td>
                <td>{recente_display}</td>
                <td class="{status_class}">{status_text}</td> 
                <td class="{qtd_style}">{qtd}</td>
            </tr>
        """

    html += f"</table>{ASSINATURA_HTML}</body></html>"
    return html


def enviar_email_diario(html):
    msg = MIMEMultipart('alternative')
    msg['From'] = REMETENTE
    msg['To'] = ", ".join(DESTINATARIOS)
    msg['Cc'] = ", ".join(COPIA)
    msg['Subject'] = ASSUNTO
    msg.attach(MIMEText(html, 'html'))
    try:
        AUTH = os.environ.get("VALID")
        if not AUTH:
            logging.critical("ERRO CRÍTICO: A autenticação do e-mail (variável 'VALID') não foi encontrada no arquivo '.env'. O script não pode continuar.")
            return

        with smtplib.SMTP('smtp.office365.com', 587) as servidor:
            servidor.starttls()
            servidor.login(REMETENTE, AUTH) 
            servidor.send_message(msg)
        logging.info(f"Email '{ASSUNTO}' enviado com sucesso para {len(DESTINATARIOS)} destinatários.")
    except Exception as e:
        logging.error(f"Erro ao enviar e-mail '{ASSUNTO}': {e}")


def limpar_dados_api():
    try:
        requests.post(API_URL_CLEAR, timeout=10)
        logging.info("Comando para limpar dados da API enviado com sucesso.")
    except requests.exceptions.RequestException as e:
        logging.warning(f"Não foi possível enviar comando para limpar dados da API. Erro: {e}")


if __name__ == "__main__":
    setup_logging()

    logging.info("Iniciando processo de centralização dos relatórios.")
    dados = buscar_dados_da_api()
    if not dados:
        logging.warning("Nenhum relatório recebido pela API hoje. Nenhum e-mail será enviado.")
    else:
        logging.info(f"Recebidos relatórios de {len(dados)} clientes. Gerando HTML.")
        html = gerar_tabela_html(dados)
        enviar_email_diario(html)
        limpar_dados_api()
    logging.info("Processo de centralização finalizado.")
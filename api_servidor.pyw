import os
import logging
from flask import Flask, request, jsonify
from waitress import serve
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler


LOG_DIR = r"C:\SCRIPTS\1 - RELATORIO DIARIO\CENTRALIZADOR\Logs\servidor"
os.makedirs(LOG_DIR, exist_ok=True)

log_filename = "api_servidor.log"

handler = TimedRotatingFileHandler(
    os.path.join(LOG_DIR, log_filename),
    when="midnight",
    backupCount=30,
    encoding='utf-8'
)
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

app_logger = logging.getLogger()
app_logger.setLevel(logging.INFO)
app_logger.addHandler(handler)


app = Flask(__name__)
reports_data = {}

@app.route('/report', methods=['POST'])
def receive_report():
    data = request.json
    client_name = data.get('cliente')
    
    if not client_name:
        return jsonify({"status": "error", "message": "Nome do cliente ausente"}), 400

    reports_data[client_name] = {
        'data': data,
        'received_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    app_logger.info(f"Relatório recebido de: {client_name}")
    return jsonify({"status": "success", "message": f"Relatório de {client_name} recebido."})

@app.route('/get_reports', methods=['GET'])
def get_reports():
    app_logger.info(f"Script centralizador solicitou os relatórios. Total: {len(reports_data)}.")
    return jsonify(reports_data)

@app.route('/clear', methods=['POST'])
def clear_reports():
    global reports_data
    count = len(reports_data)
    reports_data = {}
    app_logger.info(f"Dados de relatórios ({count} clientes) foram limpos para o novo dia.")
    return jsonify({"status": "success", "message": "Dados limpos."})


if __name__ == '__main__':
    app_logger.info("====== Servidor de API de relatórios INICIADO ======")
    app_logger.info(f"====== Escutando em host 0.0.0.0, porta 5000 ======")
    serve(app, host='0.0.0.0', port=5000) # aceita conexões de qualquer lugar do endereço da rede 
import time
import random
from flask import Flask, Response
from prometheus_client import Counter, Histogram, Gauge, Summary, Info, Enum, generate_latest, CONTENT_TYPE_LATEST

# Cria a aplicação Flask
app = Flask(__name__)

# --- Métricas Personalizadas ---

PEDIDOS_PROCESSADOS = Counter(
    'meuapp_pedidos_processados_total',
    'Total de pedidos processados pela aplicação',
    ['metodo', 'endpoint']
)

DURACAO_PROCESSAMENTO = Histogram(
    'meuapp_duracao_processamento_seconds',
    'Histograma da duração do processamento de um pedido'
)

USUARIOS_ATIVOS = Gauge(
    'meuapp_usuarios_ativos',
    'Número de usuários ativos na aplicação'
)

LATENCIA_SUMARIO = Summary(
    'meuapp_latencia_summary_seconds',
    'Resumo da latência de requisições'
)

INFO_APP = Info(
    'meuapp_info',
    'Informações sobre a aplicação'
)

ESTADO_APP = Enum(
    'meuapp_estado_aplicacao',
    'Estado atual da aplicação',
    states=['inicializando', 'rodando', 'erro']
)

# Inicializa as métricas informativas
INFO_APP.info({'versao': '1.0.0', 'ambiente': 'producao'})
ESTADO_APP.state('rodando')

# --- Endpoints ---

@app.route('/')
def index():
    return "<h1>Olá! Minha API de monitoramento está no ar.</h1>"

@app.route('/login', methods=["GET", "POST"])
def login():
    USUARIOS_ATIVOS.inc()
    return "Usuário logado!"

@app.route('/logout', methods=["GET", "POST"])
def logout():
    USUARIOS_ATIVOS.dec()
    return "Deslogado"

@app.route('/processar_pedido')
def processar_pedido():
    tempo_de_processamento = random.uniform(0.1, 0.5)
    with DURACAO_PROCESSAMENTO.time():
        with LATENCIA_SUMARIO.time():
            time.sleep(tempo_de_processamento)

    PEDIDOS_PROCESSADOS.labels(metodo='GET', endpoint='/processar_pedido').inc()
    return f"<p>Pedido processado em {tempo_de_processamento:.2f} segundos.</p>"

@app.route('/erro')
def erro_simulado():
    ESTADO_APP.state('erro')
    return "<p>Estado da aplicação definido como erro.</p>"

@app.route('/resetar_estado')
def resetar_estado():
    ESTADO_APP.state('rodando')
    return "<p>Estado da aplicação resetado para rodando.</p>"

# ✅ Endpoint /metrics manual
@app.route('/metrics')
def metrics():

    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

# --- Inicia o servidor ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

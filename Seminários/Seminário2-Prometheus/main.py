import time
import random
from flask import Flask, Response
from prometheus_client import Counter, Histogram, Gauge, Summary, Info, Enum
from prometheus_flask_exporter import PrometheusMetrics

# Cria a aplicação Flask
app = Flask(__name__)
metrics = PrometheusMetrics(app)

# --- Métricas Personalizadas ---

# Counter: Total de pedidos processados
PEDIDOS_PROCESSADOS = Counter(
    'meuapp_pedidos_processados_total',
    'Total de pedidos processados pela aplicação',
    ['metodo', 'endpoint']
)

# Histogram: Duração do processamento
DURACAO_PROCESSAMENTO = Histogram(
    'meuapp_duracao_processamento_seconds',
    'Histograma da duração do processamento de um pedido'
)

# Gauge: Número de usuários ativos (pode subir e descer)
USUARIOS_ATIVOS = Gauge(
    'meuapp_usuarios_ativos',
    'Número de usuários ativos na aplicação'
)

# Summary: Métrica de latência (parecido com histogram, mas com percentis)
LATENCIA_SUMARIO = Summary(
    'meuapp_latencia_summary_seconds',
    'Resumo da latência de requisições'
)

# Info: Informações gerais da aplicação
INFO_APP = Info(
    'meuapp_info',
    'Informações sobre a aplicação'
    info=['versão','ambiente']
)

# Enum: Estado da aplicação
ESTADO_APP = Enum(
    'meuapp_estado_aplicacao',
    'Estado atual da aplicação',
    states=['inicializando', 'rodando', 'erro']
)

# Define informações estáticas
INFO_APP.info({'versao': '1.0.0', 'ambiente': 'producao'})

# Define estado inicial
ESTADO_APP.state('rodando')

# --- Endpoints da API ---

@app.route('/')
def index():
    return "<h1>Olá! Minha API de monitoramento está no ar.</h1>"
@app.route("/login", methods=["POST"])
def login():
    # ... lógica de login ...
    USUARIOS_ATIVOS.inc()  # Incrementa 1 usuário ativo
    return "Logado"

@app.route("/logout", methods=["POST"])
def logout():
    # ... lógica de logout ...
    USUARIOS_ATIVOS.dec()  # Decrementa 1 usuário ativo
    return "Deslogado"


@app.route('/processar_pedido')
def processar_pedido():
    # Simula tempo de processamento aleatório
    tempo_de_processamento = random.uniform(0.1, 0.5)
    
    # Medindo com Histogram e Summary
    with DURACAO_PROCESSAMENTO.time():
        with LATENCIA_SUMARIO.time():
            time.sleep(tempo_de_processamento)

    # Incrementa contadores e ajusta gauge
    PEDIDOS_PROCESSADOS.labels(metodo='GET', endpoint='/processar_pedido').inc()
    USUARIOS_ATIVOS.inc()  # Simula aumento de usuários ativos
    USUARIOS_ATIVOS.dec()  # Depois decrementa

    return f"<p>Pedido processado em {tempo_de_processamento:.2f} segundos.</p>"

@app.route('/erro')
def erro_simulado():
    ESTADO_APP.state('erro')  # Altera estado da aplicação
    return "<p>Estado da aplicação definido como erro.</p>"

@app.route('/resetar_estado')
def resetar_estado():
    ESTADO_APP.state('rodando')  # Restaura estado
    return "<p>Estado da aplicação resetado para rodando.</p>"

# O endpoint /metrics é exposto automaticamente

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

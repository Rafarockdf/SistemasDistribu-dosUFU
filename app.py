import time
import random
from flask import Flask, Response
from prometheus_client import Counter, Histogram
from prometheus_flask_exporter import PrometheusMetrics

# Cria a aplicação Flask
app = Flask(__name__)

# Conecta o exportador de métricas à aplicação
# Isso já cria métricas padrão como latência e contagem de requests
metrics = PrometheusMetrics(app)

# --- Métricas Customizadas ---
# Um contador para o total de pedidos processados
PEDIDOS_PROCESSADOS = Counter(
    'meuapp_pedidos_processados_total',
    'Total de pedidos processados pela aplicação',
    ['metodo', 'endpoint'] # Labels para diferenciar as métricas
)

# Um histograma para medir a duração do "processamento" do pedido
DURACAO_PROCESSAMENTO = Histogram(
    'meuapp_duracao_processamento_seconds',
    'Histograma da duração do processamento de um pedido'
)

# --- Endpoints da API ---
@app.route('/')
def index():
    # Endpoint simples para mostrar que a API está no ar
    return "Olá! Minha API de monitoramento está no ar."

@app.route('/processar_pedido')
def processar_pedido():
    # Simula um tempo de processamento aleatório
    tempo_de_processamento = random.uniform(0.1, 0.5)
    with DURACAO_PROCESSAMENTO.time():
        time.sleep(tempo_de_processamento)

    # Incrementa o contador de pedidos processados
    PEDIDOS_PROCESSADOS.labels(metodo='GET', endpoint='/processar_pedido').inc()

    return f"Pedido processado em {tempo_de_processamento:.2f} segundos."

# O endpoint /metrics é exposto automaticamente pela biblioteca `prometheus-flask-exporter`

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
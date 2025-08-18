from kafka import KafkaProducer
import json
import pandas as pd
import requests
from shapely.geometry import shape

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Função coleta cidades (já implementada por você)
def coleta_nomes_cidades():
    """
    Busca a lista de municípios do IBGE e organiza por cidade e estado.
    """
    url_ibge = 'https://servicodados.ibge.gov.br/api/v1/localidades/municipios'
    lista_municipios = []
    r = requests.get(url_ibge)
    if r.status_code == 200:
        lista = r.json()
    else:
        print(f"Erro na requisição: {r.status_code}")
    try:
        for posicao in lista:
            lista_municipios.append({"id":posicao['id'],'Cidade' : posicao['nome'],'Estado' : posicao['microrregiao']['mesorregiao']['UF']['nome']})
        return lista_municipios
    except(TypeError):
        print( f'Erro: {TypeError}')
    return pd.DataFrame(lista_municipios)

# Função coleta centroides
def coleta_lat_lon(id_cidade):
    url = f'https://servicodados.ibge.gov.br/api/v2/malhas/{id_cidade}?formato=application/vnd.geo+json'
    r = requests.get(url)
    if r.status_code == 200:
        geojson = r.json()
        geom = shape(geojson['features'][0]['geometry'])
        centroide = geom.centroid
        return centroide.y, centroide.x
    return None, None

cidades = coleta_nomes_cidades()

for _, row in cidades.iterrows():
    lat, lon = coleta_lat_lon(row["id"])
    msg = {
        "tipo": "CadastrarCidade",
        "payload": {
            "id": row["id"],
            "cidade": row["Cidade"],
            "estado": row["Estado"],
            "lat": lat,
            "lon": lon
        }
    }
    producer.send("cidades_raw", msg)
producer.flush()
print("✅ Mensagens enviadas ao Kafka")

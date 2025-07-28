import os
from google.cloud import bigquery


# Caminho para sua chave .json
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\rafam\OneDrive\Área de Trabalho\TrabalhoFinalSD\ProjetoFinalSD\ExploraçãoInicialDados\pure-lodge-464519-d5-df6ed87935b4.json"

# Cria cliente automaticamente com base na chave
client = bigquery.Client()

# Consulta de teste com dados climáticos públicos
query_estacoes = """
SELECT
    dados.id_municipio AS id_municipio,
    diretorio_id_municipio.nome AS id_municipio_nome,
    dados.id_estacao as id_estacao,
    dados.estacao as estacao,
    dados.data_fundacao as data_fundacao,
    dados.latitude as latitude,
    dados.longitude as longitude,
    dados.altitude as altitude
FROM `basedosdados.br_inmet_bdmep.estacao` AS dados
LEFT JOIN (SELECT DISTINCT id_municipio,nome  FROM `basedosdados.br_bd_diretorios_brasil.municipio`) AS diretorio_id_municipio
    ON dados.id_municipio = diretorio_id_municipio.id_municipio
"""

query_clima = '''

SELECT * FROM `basedosdados.br_inmet_bdmep.microdados` WHERE ano = 2024 LIMIT 1000
'''



df = client.query(query_estacoes).to_dataframe()
print(df)

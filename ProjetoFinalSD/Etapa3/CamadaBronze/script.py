import requests
import pandas as pd
from shapely.geometry import shape
from tqdm import tqdm

def coleta_nomes_cidades():
    """
    Função que busca a nome das cidades e estados do Brasil.
    """
    url_ibge = 'https://servicodados.ibge.gov.br/api/v1/localidades/municipios'
    lista_municipios = []
    r = requests.get(url_ibge)
    if r.status_code == 200:
        lista = r.json()
    else:
        print(f"Erro na requisição: {r.status_code}")
        return []

    try:
        for posicao in lista:
            lista_municipios.append({
                'id': posicao['id'],
                'Cidade': posicao['nome'],
                'Estado': posicao['microrregiao']['mesorregiao']['UF']['nome']
            })
        return lista_municipios
    except TypeError:
        print(f'Erro: {TypeError}')
    return lista_municipios


def coleta_lat_lon_cidades(lista_municipios: pd.DataFrame):
    lista_lat_lon = []

    for _, row in tqdm(lista_municipios.iterrows(),
                       total=len(lista_municipios),
                       desc="Coletando centroides das cidades"):
        codigo = row["id"]
        url = f'https://servicodados.ibge.gov.br/api/v2/malhas/{codigo}?formato=application/vnd.geo+json'
        r = requests.get(url)
        if r.status_code == 200:
            geojson = r.json()
            try:
                geom = shape(geojson['features'][0]['geometry'])
                centroide = geom.centroid
                lista_lat_lon.append({
                    "id": codigo,
                    "lat": centroide.y,   # latitude
                    "lon": centroide.x    # longitude
                })
            except Exception as e:
                print(f"Erro processando {codigo}: {e}")
        else:
            print(f"Erro na requisição {codigo}: {r.status_code}")
    return pd.DataFrame(lista_lat_lon)


# --- Execução ---
cidades = coleta_nomes_cidades()
cidades = pd.DataFrame(cidades)
print(cidades.head())

cidades_lat_lon = coleta_lat_lon_cidades(cidades)
print(cidades_lat_lon.head())

# Junta tudo em um só DataFrame
cidades_completo = cidades.merge(cidades_lat_lon, on="id", how="left")
print(cidades_completo.head())

'''
/* Esse script é reponsável pela coleta de informações iniciais para utilizar na busca dos dados climáticos
 informações essas cidades do brasil, estados, latitude e longitude*/

'''
from geopy.geocoders import Nominatim
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import requests
import pandas as pd
import json
import psycopg2
def coleta_nomes_cidades():
    """
    Função que busca a nome das cidades e estados do brasil.
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
            lista_municipios.append({'Cidade' : posicao['nome'],'Estado' : posicao['microrregiao']['mesorregiao']['UF']['nome']})
        return lista_municipios
    except(TypeError):
        print( f'Erro: {TypeError}')
    return lista_municipios

cidades = coleta_nomes_cidades()
cidades = pd.DataFrame(cidades)
cidades

geolocator = Nominatim(user_agent="meu_app_python_geocoding_123", timeout=10)
resultados = {}

def obter_lat_lon_seguro(endereco):
    """
    Função que busca a geolocalização e trata possíveis erros.
    """
    try:
        localizacao = geolocator.geocode(endereco)
        if localizacao:
            return endereco, (localizacao.latitude, localizacao.longitude)
        else:
            return endereco, (None, None)
    except Exception as e:
        print(e)
        return endereco, (None, None)

enderecos_completos = [f"{row['Cidade']}, {row['Estado']}, Brasil" for index, row in cidades.iterrows()]
enderecos_completos[0]
sql_create = '''

CREATE TABLE IF NOT EXISTS enderecos (
    cidade VARCHAR(100),
    estado VARCHAR(50),
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION
);
'''
futures = []
sql_insert = '''

INSERT INTO enderecos(cidade,estado,latitude,longitude) VALUES (%s, %s, %s, %s);

'''
try:
    conn = psycopg2.connect(
        dbname="DEV_BRONZE",
        user="postgres",
        password="rafa7887",
        host="localhost",
        port="5433")
    print("Conexão bem sucedida! 🎉")
    with conn.cursor() as curs:
        try:
            curs.execute(sql_create)
            conn.commit()
        except:
            print("Não foi possível criar tabela no banco")
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = {executor.submit(obter_lat_lon_seguro, endereco): endereco for endereco in enderecos_completos}

            for future in tqdm(as_completed(futures), total=len(enderecos_completos), desc="Geocodificando Cidades"):
                endereco, coords = future.result()
                resultados[endereco] = coords
                cidade, estado, pais = endereco.split(',', maxsplit=2)
                cidade = cidade.strip()
                estado = estado.strip()
                lat, lon = coords
                try:
                    curs.execute(sql_insert, (cidade, estado, lat, lon))
                except (Exception, psycopg2.DatabaseError) as error:
                    print(f"Erro ao inserir {cidade}: {error}")
            #futures = [executor.submit(obter_lat_lon_seguro, endereco) for endereco in enderecos_completos]
            conn.commit()      
        # Processa os resultados conforme eles ficam prontos, com uma barra de progresso
            for future in tqdm(as_completed(futures), total=len(enderecos_completos), desc="Geocodificando Cidades"):
                endereco, coords = future.result()
                resultados[endereco] = coords
except:
    print("I am unable to connect to the database")
    
finally:
    conn.close()
    
'''


# --- ETAPA 4: Mapear os resultados de volta para o DataFrame ---
# Cria uma série pandas a partir do dicionário de resultados
mapa_coords = pd.Series(resultados)

# Usa o método 'map' que é muito mais rápido que 'apply' para este caso
cidades['coords'] = cidades.apply(lambda row: f"{row['Cidade']}, {row['Estado']}, Brasil", axis=1).map(mapa_coords)

# Expande a tupla de coordenadas em duas colunas
cidades[['lat', 'lon']] = pd.DataFrame(cidades['coords'].tolist(), index=cidades.index)

# Remove a coluna temporária se não for mais necessária


cidades_mg = cidades.drop(columns=['coords'])

print(cidades_mg)'''
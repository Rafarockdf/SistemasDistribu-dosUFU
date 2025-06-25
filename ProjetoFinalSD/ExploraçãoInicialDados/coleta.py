#%%

import requests
import time
import threading
import pandas as pd
#%%
def coleta_nomes_cidades():
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

#%% 
def coleta_dados_api_climatica(cidade):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={cidade},BR&appid=c41811d0e4a94530079d18a69e9a1c5c&units=metric"
    resposta = requests.get(url)
    if resposta.status_code != 200:
        print(f"Erro ao buscar dados de {cidade}: {resposta.status_code} - {resposta.json().get('message')}")
        return None
    return resposta.json()

 #%%    
def main():
    cidades = coleta_nomes_cidades()
    municipios = pd.DataFrame(cidades)
    mask = municipios['Estado'] == 'Minas Gerais'
    bloco = municipios[mask]
    bloco2 = bloco[0:21]
    dados = coleta_dados_api_climatica('Monte Carmelo')
    return dados
 #%%   
main()
# %%

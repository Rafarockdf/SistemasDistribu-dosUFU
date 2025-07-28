import requests
import time
import threading
import socket
import pandas as pd
import json










# --- Funções de Coleta de Dados ---

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
            lista_municipios.append({'Cidade' : posicao['nome'],'Estado' : posicao['microrregiao']['mesorregiao']['UF']['nome']})
        return lista_municipios
    except(TypeError):
        print( f'Erro: {TypeError}')
    return lista_municipios

def coleta_dados_api_climatica(estado):
    """
    Função mock para simular a coleta de dados climáticos de uma API externa.
    """
    print(f"[Thread] Coletando dados climáticos para: {estado}...")
    time.sleep(2)
    return {
        "estado": estado,
        "temperatura_media_celsius": 25.2,
        "umidade_relativa_porcentagem": 50,
        "condicao": "Parcialmente Nublado",
        "data_coleta": time.strftime("%Y-%m-%d %H:%M:%S")
    }

# --- Configurações do Socket Cliente ---
HOST = '127.0.0.1'
PORT = 65432

# --- Função que a Thread Executará ---

def thread_coleta_e_envio(estado_name, cidades_do_estado):
    """
    Função executada por cada thread:
    1. Coleta dados climáticos.
    2. Conecta ao servidor TCP.
    3. Envia os dados coletados.
    """
    print(f"[DEBUG THREAD {estado_name}] Thread iniciada para o estado {estado_name}.") # DEBUG
    max_retries = 3
    retry_delay = 5

    for attempt in range(max_retries):
        try:
            # 1. Coleta os dados da API climática para o estado
            dados_climaticos = coleta_dados_api_climatica(estado_name)
            dados_climaticos['cidades_processadas'] = cidades_do_estado['Cidade'].tolist()
            print(f"[DEBUG THREAD {estado_name}] Dados climáticos coletados para {estado_name}.") # DEBUG

            # 2. Conecta-se ao servidor TCP
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                print(f"[Thread {estado_name}] Tentando conectar a {HOST}:{PORT} (Tentativa {attempt + 1}/{max_retries})...")
                s.connect((HOST, PORT))
                print(f"[Thread {estado_name}] Conectado ao servidor.")

                # 3. Envia os dados para o servidor
                mensagem_json = json.dumps(dados_climaticos) + '\n'
                s.sendall(mensagem_json.encode('utf-8'))
                print(f"[Thread {estado_name}] Dados de {estado_name} enviados.")

                # Opcional: Receber uma confirmação do servidor
                resposta = s.recv(1024).decode('utf-8').strip()
                print(f"[Thread {estado_name}] Resposta do servidor: {resposta}")
                return
        except ConnectionRefusedError:
            print(f"[Thread {estado_name}] Erro: Servidor não está ativo ou não aceitou a conexão em {HOST}:{PORT}. Retentando em {retry_delay}s...")
            time.sleep(retry_delay)
        except Exception as e:
            print(f"[Thread {estado_name}] Ocorreu um erro inesperado: {e}")
            break

    print(f"[Thread {estado_name}] Falha ao conectar ou enviar dados após {max_retries} tentativas.")

# --- Função Principal do Cliente ---

def main():
    print("Iniciando a coleta de cidades do IBGE...")
    cidades_data = coleta_nomes_cidades()
    
    if not cidades_data:
        print("[CLIENTE] Não foi possível coletar dados de cidades. Encerrando.")
        return

    municipios = pd.DataFrame(cidades_data)
    print(f"[CLIENTE] DataFrame de municípios criado. Total de linhas: {len(municipios)}") # DEBUG

    municipios_por_estado = municipios.groupby('Estado')
    print(f"[CLIENTE] DataFrame agrupado por estado. Total de estados únicos: {len(municipios_por_estado)}") # DEBUG

    threads = []
    print("\n--- Iniciando threads de coleta e envio por estado ---")
    for estado_name, cidades_do_estado in municipios_por_estado:
        print(f"[CLIENTE] Criando thread para o estado: {estado_name}") # DEBUG
        thread = threading.Thread(
            target=thread_coleta_e_envio,
            args=(estado_name, cidades_do_estado)
        )
        threads.append(thread)
        thread.start()

    print("\n[CLIENTE] Todas as threads foram iniciadas. Aguardando finalização...") # DEBUG
    for thread in threads:
        thread.join()

    print("\n--- Todas as threads de coleta e envio finalizaram. ---")
    print("Verifique o log do seu servidor (`servidor_clima.py`) para os dados recebidos.")

if __name__ == "__main__":
    main()
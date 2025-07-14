import requests
import time
import threading
import socket
import pandas as pd
import json

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
def coleta_dados_api_climatica(estado):
    print(f"[Thread] Coletando dados climáticos para: {estado}...")
    time.sleep(2) # Simula o tempo que a API levaria para responder
    return {"estado": estado, "temperatura_media": f"{25 + len(estado)}C", "condicao": "Parcialmente Nublado"}

HOST = '127.0.0.1'  # Endereço IP do servidor (localhost para teste)
PORT = 65432        # Porta que o servidor estará escutando

def thread_coleta_e_envio(estado_name, cidades_do_estado):
    try:
        # 1. Coleta os dados da API climática para o estado
        dados_climaticos = coleta_dados_api_climatica(estado_name)
        dados_climaticos['cidades_processadas'] = cidades_do_estado['Cidade'].tolist()

        # 2. Conecta-se ao servidor TCP
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            print(f"[Thread {estado_name}] Tentando conectar a {HOST}:{PORT}...")
            s.connect((HOST, PORT))
            print(f"[Thread {estado_name}] Conectado ao servidor.")

            # 3. Envia os dados para o servidor
            # É crucial serializar os dados (e.g., para JSON) antes de enviar
            # e adicionar um terminador ou cabeçalho para o servidor saber quando a mensagem termina.
            # Aqui, estamos usando um separador simples '\n' (newline).
            mensagem_json = json.dumps(dados_climaticos) + '\n'
            s.sendall(mensagem_json.encode('utf-8'))
            print(f"[Thread {estado_name}] Dados de {estado_name} enviados.")

            # Opcional: Receber uma confirmação do servidor
            resposta = s.recv(1024).decode('utf-8')
            print(f"[Thread {estado_name}] Resposta do servidor: {resposta.strip()}")

    except ConnectionRefusedError:
        print(f"[Thread {estado_name}] Erro: Servidor não está ativo ou não aceitou a conexão em {HOST}:{PORT}.")
    except Exception as e:
        print(f"[Thread {estado_name}] Ocorreu um erro: {e}")

def main():
    cidades_data = coleta_nomes_cidades()
    municipios = pd.DataFrame(cidades_data)

    # Agrupa o DataFrame por 'Estado'
    municipios_por_estado = municipios.groupby('Estado')

    threads = []
    for estado_name, cidades_do_estado in municipios_por_estado:
        print(f"Criando thread para o estado: {estado_name}")
        # Cria uma nova thread para cada estado
        thread = threading.Thread(
            target=thread_coleta_e_envio,
            args=(estado_name, cidades_do_estado)
        )
        threads.append(thread)
        thread.start() # Inicia a thread

    # Espera todas as threads terminarem
    for thread in threads:
        thread.join()

    print("\nTodas as threads de coleta e envio finalizaram.")
    print("Verifique o log do seu servidor para os dados recebidos.")

if __name__ == "__main__":

    HOST = '127.0.0.1'
    PORT = 65432

    def handle_client(conn, addr):
        print(f"Conectado por {addr}")
        try:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                # Decodifica e imprime os dados recebidos
                decoded_data = data.decode('utf-8').strip()
                print(f"Recebido de {addr}: {decoded_data}")
                # Envia uma confirmação de volta
                conn.sendall(b"Dados recebidos com sucesso!\n")
        except Exception as e:
            print(f"Erro no manuseio do cliente {addr}: {e}")
        finally:
            conn.close()
            print(f"Conexão com {addr} fechada.")

    def start_server():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            s.listen()
            print(f"Servidor escutando em {HOST}:{PORT}...")
            while True:
                conn, addr = s.accept()
                # Para lidar com múltiplos clientes, um thread para cada cliente
                client_thread = threading.Thread(target=handle_client, args=(conn, addr))
                client_thread.start()

    start_server()
    print("Iniciando o cliente TCP...")
    print("Lembre-se de iniciar um servidor TCP separado para receber as conexões!")
    main()
import socket
import threading
import json
import time

HOST = '127.0.0.1'  # Endereço IP do servidor (localhost)
PORT = 65432        # Porta que o servidor estará escutando

def handle_client(conn, addr):
    """
    Lida com a comunicação de um cliente conectado.
    Recebe os dados JSON e envia uma confirmação.
    """
    print(f"[Servidor] Conectado por {addr}")
    try:
        # Buffer para dados recebidos. Pode precisar de lógica mais complexa
        # para mensagens grandes ou fragmentadas se o '\n' não for suficiente.
        buffer = b""
        while True:
            data = conn.recv(1024)
            if not data:
                break # Cliente desconectou
            buffer += data

            # Processa as mensagens completas no buffer
            while b'\n' in buffer:
                message, buffer = buffer.split(b'\n', 1)
                try:
                    decoded_data = message.decode('utf-8')
                    # Tenta carregar o JSON
                    json_data = json.loads(decoded_data)
                    print(f"[Servidor] Recebido de {addr}: {json.dumps(json_data, indent=2)}")

                    # Aqui você processaria/armazenaria os dados recebidos
                    # Ex: Salvar em um banco de dados, logar, etc.

                    # Envia uma confirmação de volta ao cliente
                    conn.sendall(b"Dados recebidos com sucesso!\n")
                except json.JSONDecodeError:
                    print(f"[Servidor] Erro ao decodificar JSON de {addr}: {decoded_data}")
                    #conn.sendall(b"Erro: Mensagem JSON inválida.\n")
                except Exception as e:
                    print(f"[Servidor] Erro ao processar dados de {addr}: {e}")
                    conn.sendall(f"Erro interno do servidor: {e}\n".encode('utf-8'))
    except Exception as e:
        print(f"[Servidor] Erro no manuseio do cliente {addr}: {e}")
    finally:
        print(f"[Servidor] Conexão com {addr} fechada.")
        conn.close()

def start_server():
    """
    Inicia o servidor TCP para escutar as conexões dos clientes.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Permite reusar o endereço rapidamente
        s.bind((HOST, PORT))
        s.listen()
        print(f"--- Servidor TCP de Clima escutando em {HOST}:{PORT} ---")
        while True:
            conn, addr = s.accept() # Aceita uma nova conexão de cliente
            # Cria uma nova thread para lidar com cada cliente conectado
            client_thread = threading.Thread(target=handle_client, args=(conn, addr))
            client_thread.start()

if __name__ == "__main__":
    start_server()
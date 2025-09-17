import threading
import time
import random
from queue import PriorityQueue

# Fila para armazenar tuplas (timestamp, process_id, message_content)
# A PriorityQueue garante a ordenação automática baseada no primeiro elemento da tupla (o timestamp)
# e, em caso de empate, no segundo (o process_id), alcançando a ordem total.
class MessageQueue:
    def __init__(self):
        self.queue = PriorityQueue()

    def push(self, timestamp, process_id, message):
        # A tupla inserida na fila de prioridade garante a ordenação
        self.queue.put((timestamp, process_id, message))

    def pop(self):
        if not self.queue.empty():
            return self.queue.get()
        return None

    def is_empty(self):
        return self.queue.empty()

class Process(threading.Thread):
    def __init__(self, process_id, total_processes, all_processes):
        super().__init__()
        self.process_id = process_id
        self.total_processes = total_processes
        self.lamport_clock = 0
        self.all_processes = all_processes
        self.message_queue = MessageQueue()
        self.delivered_messages = [] # Armazena as mensagens já entregues (exibidas)

    def _event(self):
        """ Incrementa o relógio de Lamport para um evento interno. """
        self.lamport_clock += 1
        print(f"Processo {self.process_id}: Evento interno. Relógio: {self.lamport_clock}")

    def send_message(self, message_content):
        """ Envia uma mensagem em broadcast para todos os processos (incluindo ele mesmo). """
        self._event() # Incrementa o relógio antes de enviar
        timestamp = self.lamport_clock
        print(f"Processo {self.process_id}: Enviando '{message_content}' com timestamp {timestamp}")

        for i in range(self.total_processes):
            # Simula a latência de rede variável
            latency = random.uniform(0.1, 1.0)
            # Cria uma closure para capturar as variáveis do loop corretamente
            def delivery(target_process_id, ts, msg):
                time.sleep(latency)
                self.all_processes[target_process_id].receive_message(ts, self.process_id, msg)

            # Usa uma nova thread para a entrega simulada, para não bloquear o remetente
            threading.Thread(target=delivery, args=(i, timestamp, message_content)).start()

    def receive_message(self, timestamp, sender_id, message_content):
        """ Recebe uma mensagem, atualiza o relógio e a coloca na fila. """
        # Atualiza o relógio local conforme o algoritmo de Lamport
        self.lamport_clock = max(self.lamport_clock, timestamp) + 1
        
        # Adiciona a mensagem à fila de prioridade para ordenação
        self.message_queue.push(timestamp, sender_id, message_content)
        
        print(f"Processo {self.process_id}: Recebeu '{message_content}' de P{sender_id} (TS: {timestamp}). Relógio atualizado para {self.lamport_clock}")

    def deliver_messages(self):
        """ Tenta entregar mensagens da fila. """
        while not self.message_queue.is_empty():
            # Pega a mensagem com o menor timestamp (e ID para desempate)
            ts, pid, msg = self.message_queue.pop()
            self.delivered_messages.append(f"(TS:{ts}, P:{pid}) -> {msg}")

    def run(self):
        """ Simulação da execução do processo. """
        # Cada processo envia uma ou duas mensagens em momentos aleatórios
        for _ in range(random.randint(1, 2)):
            time.sleep(random.uniform(0.5, 2))
            message = f"Olá do processo {self.process_id}"
            self.send_message(message)

# --- Configuração e Execução da Simulação (Parte A) ---
if __name__ == "__main__":
    print("--- Parte A: Simulação de Chat com Relógios de Lamport ---")
    NUM_PROCESSES = 3
    processes = []

    # O dicionário 'processes_dict' é necessário para que cada processo tenha uma referência aos outros
    processes_dict = {}
    for i in range(NUM_PROCESSES):
        # A instância é passada para o dicionário antes de ser totalmente inicializada,
        # mas a referência é válida.
        p = Process(i, NUM_PROCESSES, processes_dict)
        processes.append(p)
        processes_dict[i] = p

    # Inicia a execução de todas as threads (processos)
    for p in processes:
        p.start()

    # Espera que todas as threads terminem suas execuções
    for p in processes:
        p.join()

    # Um tempo extra para garantir que todas as mensagens em trânsito sejam recebidas
    print("\nAguardando a entrega final de todas as mensagens...")
    time.sleep(2 * NUM_PROCESSES)

    # Cada processo entrega (ordena e exibe) suas mensagens
    for p in processes:
        p.deliver_messages()

    # Exibindo os resultados
    print("\n--- RESULTADO FINAL DA ORDENAÇÃO ---")
    all_orders = []
    for i in range(NUM_PROCESSES):
        print(f"\nOrdem de entrega final para o Processo {i}:")
        for msg in processes[i].delivered_messages:
            print(msg)
        all_orders.append(processes[i].delivered_messages)

    # Verificação final: todas as listas de mensagens entregues devem ser idênticas
    is_consistent = all(order == all_orders[0] for order in all_orders)
    if is_consistent and all_orders[0]:
        print("\n[SUCESSO] Todos os processos entregaram as mensagens na mesma ordem total.")
    else:
        print("\n[FALHA] A ordem das mensagens não foi consistente entre os processos.")
    print("-" * 50)
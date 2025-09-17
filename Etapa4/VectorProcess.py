import copy

class VectorProcess:
    def __init__(self, process_id, n_processes):
        self.id = process_id
        self.n_processes = n_processes
        # Inicializa o relógio vetorial com zeros
        self.vector_clock = [0] * n_processes

    def local_event(self):
        """ Simula um evento local (ou um envio de mensagem). """
        # Incrementa sua própria entrada no relógio vetorial
        self.vector_clock[self.id] += 1
        print(f"P{self.id}: Evento local. Relógio Vetorial: {self.vector_clock}")
        # Retorna uma cópia do relógio no momento do evento
        return copy.deepcopy(self.vector_clock)

    def send_message(self, target_process):
        """ Simula o envio de uma mensagem. """
        # Um envio é um evento local, então o relógio é incrementado primeiro
        vc_at_send = self.local_event()
        print(f"P{self.id}: Enviando mensagem para P{target_process.id} com Relógio {vc_at_send}")
        target_process.receive_message(self.id, vc_at_send)

    def receive_message(self, sender_id, received_vc):
        """ Simula o recebimento de uma mensagem e atualiza o relógio vetorial. """
        print(f"P{self.id}: Recebeu mensagem de P{sender_id} com Relógio {received_vc}")
        
        # 1. Atualiza o relógio local com o máximo elemento a elemento
        for i in range(self.n_processes):
            self.vector_clock[i] = max(self.vector_clock[i], received_vc[i])
        
        # 2. Incrementa sua própria entrada para o evento de recebimento
        self.vector_clock[self.id] += 1
        print(f"P{self.id}: Relógio Vetorial atualizado após recebimento: {self.vector_clock}")
        
def compare_vectors(vc1, vc2):
    """
    Compara dois relógios vetoriais e determina a relação causal.
    Retorna: "antes", "depois", "concorrente".
    """
    # vc1 aconteceu antes de vc2 se todo elemento de vc1 <= vc2
    # e pelo menos um elemento de vc1 < vc2.
    less_than_equal = all(v1 <= v2 for v1, v2 in zip(vc1, vc2))
    strictly_less_than = any(v1 < v2 for v1, v2 in zip(vc1, vc2))
    
    if less_than_equal and strictly_less_than:
        return "antes"

    # vc2 aconteceu antes de vc1 se todo elemento de vc2 <= vc1
    # e pelo menos um elemento de vc2 < vc1.
    greater_than_equal = all(v1 >= v2 for v1, v2 in zip(vc1, vc2))
    strictly_greater_than = any(v1 > v2 for v1, v2 in zip(vc1, vc2))
    
    if greater_than_equal and strictly_greater_than:
        return "depois"

    # Caso contrário, os eventos são concorrentes.
    return "concorrente"

# --- Execução da Simulação (Parte B) ---
if __name__ == "__main__":
    print("\n\n--- Parte B: Analisador de Causalidade com Relógios Vetoriais ---")
    N = 3 # Número total de processos
    
    # --- Cenário 1: Cadeia Causal (A -> B) ---
    print("\n--- Cenário 1: Demonstração de Causalidade ---")
    procs_c1 = [VectorProcess(i, N) for i in range(N)]
    p0, p1, p2 = procs_c1[0], procs_c1[1], procs_c1[2]

    # Evento A em P0
    print("1. Evento A ocorre em P0.")
    vc_A = p0.local_event()

    # P0 envia mensagem para P1. O recebimento em P1 é o evento B.
    print("\n2. P0 envia mensagem para P1.")
    p0.send_message(p1) # O evento B acontece dentro do método receive_message de p1
    vc_B = copy.deepcopy(p1.vector_clock)
    
    # Análise Causal
    print("\n--- Análise Causal do Cenário 1 ---")
    print(f"Relógio Vetorial do Evento A (P0): {vc_A}")
    print(f"Relógio Vetorial do Evento B (P1): {vc_B}")
    
    relation = compare_vectors(vc_A, vc_B)
    if relation == "antes":
        print("Resultado: Evento A aconteceu antes de Evento B. (CORRETO)")
    else:
        print(f"Resultado: Relação inesperada: {relation}. (INCORRETO)")

    # --- Cenário 2: Eventos Concorrentes (X || Y) ---
    print("\n\n--- Cenário 2: Demonstração de Concorrência ---")
    procs_c2 = [VectorProcess(i, N) for i in range(N)]
    p0, p1, p2 = procs_c2[0], procs_c2[1], procs_c2[2]

    # Evento X em P0
    print("1. Evento X ocorre em P0.")
    vc_X = p0.local_event()

    # Evento Y em P2 (sem comunicação com P0)
    print("\n2. Evento Y ocorre em P2.")
    vc_Y = p2.local_event()

    # Análise Causal
    print("\n--- Análise Causal do Cenário 2 ---")
    print(f"Relógio Vetorial do Evento X (P0): {vc_X}")
    print(f"Relógio Vetorial do Evento Y (P2): {vc_Y}")

    relation = compare_vectors(vc_X, vc_Y)
    if relation == "concorrente":
        print("Resultado: O evento X e o evento Y são concorrentes. (CORRETO)")
    else:
        print(f"Resultado: Relação inesperada: {relation}. (INCORRETO)")
    print("-" * 50)
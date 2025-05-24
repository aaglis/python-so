import threading
import time
import random
import matplotlib.pyplot as plt

class SalaMonitor:
    def __init__(self):
        self.lock = threading.Lock()
        self.cond = threading.Condition(self.lock)
        self.cachorros = 0
        self.gatos = 0
        self.esperando_cachorros = 0
        self.esperando_gatos = 0
        self.ultimo_tipo = None  # 'cachorro' ou 'gato'

    def dogWantsToEnter(self, id, start_wait_callback):
        with self.cond:
            self.esperando_cachorros += 1
            start_wait_callback(id)  # Marca início da espera

            while self.gatos > 0 or (self.ultimo_tipo == 'gato' and self.esperando_gatos > 0):
                self.cond.wait()

            self.esperando_cachorros -= 1
            self.cachorros += 1
            self.ultimo_tipo = 'cachorro'

    def dogLeaves(self, id):
        with self.cond:
            self.cachorros -= 1
            if self.cachorros == 0:
                self.cond.notify_all()

    def catWantsToEnter(self, id, start_wait_callback):
        with self.cond:
            self.esperando_gatos += 1
            start_wait_callback(id)  # Marca início da espera

            while self.cachorros > 0 or (self.ultimo_tipo == 'cachorro' and self.esperando_cachorros > 0):
                self.cond.wait()

            self.esperando_gatos -= 1
            self.gatos += 1
            self.ultimo_tipo = 'gato'

    def catLeaves(self, id):
        with self.cond:
            self.gatos -= 1
            if self.gatos == 0:
                self.cond.notify_all()

class Logger:
    def __init__(self):
        self.log = []
        self.lock = threading.Lock()
        self.start_time = time.time()

    def snapshot(self, dogs, cats):
        with self.lock:
            self.log.append((time.time() - self.start_time, dogs, cats))

# Para armazenar tempos de espera
espera_cachorros = {}
espera_gatos = {}

tempos_espera_cachorros = []
tempos_espera_gatos = []

logger = Logger()
sala = SalaMonitor()

def marca_inicio_espera_cachorro(id):
    espera_cachorros[id] = time.time()

def marca_inicio_espera_gato(id):
    espera_gatos[id] = time.time()

def dog_thread(id):
    time.sleep(random.uniform(0, 0.5))

    # Marca o tempo de início da espera dentro do método que chama dogWantsToEnter
    sala.dogWantsToEnter(id, start_wait_callback=lambda i=id: marca_inicio_espera_cachorro(i))

    # Agora que entrou, calcula o tempo de espera e armazena
    tempo_entrada = time.time()
    inicio_espera = espera_cachorros.pop(id, tempo_entrada)  # Pop para não acumular lixo
    tempos_espera_cachorros.append(tempo_entrada - inicio_espera)

    logger.snapshot(sala.cachorros, sala.gatos)
    time.sleep(random.uniform(0.01, 0.25))
    sala.dogLeaves(id)
    logger.snapshot(sala.cachorros, sala.gatos)

def cat_thread(id):
    time.sleep(random.uniform(0, 0.5))

    sala.catWantsToEnter(id, start_wait_callback=lambda i=id: marca_inicio_espera_gato(i))

    tempo_entrada = time.time()
    inicio_espera = espera_gatos.pop(id, tempo_entrada)
    tempos_espera_gatos.append(tempo_entrada - inicio_espera)

    logger.snapshot(sala.cachorros, sala.gatos)
    time.sleep(random.uniform(0.01, 0.25))
    sala.catLeaves(id)
    logger.snapshot(sala.cachorros, sala.gatos)

def simulate(n_dogs=10, n_cats=10):
    threads = []
    for i in range(n_dogs):
        threads.append(threading.Thread(target=dog_thread, args=(i,)))
    for i in range(n_cats):
        threads.append(threading.Thread(target=cat_thread, args=(i,)))
    random.shuffle(threads)
    for t in threads:
        t.start()
    for t in threads:
        t.join()

def simulate_multiple_rounds(n_dogs=10, n_cats=10, rounds=50):
    for _ in range(rounds):
        simulate(n_dogs, n_cats)

# Rodar simulação
simulate_multiple_rounds(n_dogs=10, n_cats=50, rounds=20)

# Mostrar médias
media_espera_cachorros = sum(tempos_espera_cachorros) / len(tempos_espera_cachorros) if tempos_espera_cachorros else 0
media_espera_gatos = sum(tempos_espera_gatos) / len(tempos_espera_gatos) if tempos_espera_gatos else 0

print(f"Média de espera dos cachorros: {media_espera_cachorros:.4f} segundos")
print(f"Média de espera dos gatos: {media_espera_gatos:.4f} segundos")

# Plot
times, dogs, cats = zip(*logger.log)
plt.figure(figsize=(12, 6))
plt.plot(times, dogs, label="Cachorros na sala", color="blue", linewidth=1)
plt.plot(times, cats, label="Gatos na sala", color="orange", linewidth=1)
plt.xlabel("Tempo (s)")
plt.ylabel("Número de animais na sala")
plt.title("Simulação com alternância garantida e média de espera")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("simulacao_monitor_plot_multiplas_rodadas.png")
plt.show()

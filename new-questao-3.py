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

    def dogWantsToEnter(self, id):
        with self.cond:
            while self.gatos > 0:
                self.cond.wait()
            self.cachorros += 1

    def dogLeaves(self, id):
        with self.cond:
            self.cachorros -= 1
            if self.cachorros == 0:
                self.cond.notify_all()

    def catWantsToEnter(self, id):
        with self.cond:
            while self.cachorros > 0:
                self.cond.wait()
            self.gatos += 1

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

logger = Logger()
sala = SalaMonitor()

def dog_thread(id):
    time.sleep(random.uniform(0, 0.2))
    sala.dogWantsToEnter(id)
    logger.snapshot(sala.cachorros, sala.gatos)
    time.sleep(random.uniform(0.05, 0.1))
    sala.dogLeaves(id)
    logger.snapshot(sala.cachorros, sala.gatos)

def cat_thread(id):
    time.sleep(random.uniform(0, 0.2))
    sala.catWantsToEnter(id)
    logger.snapshot(sala.cachorros, sala.gatos)
    time.sleep(random.uniform(0.05, 0.1))
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

# Simula 50 rodadas de 10 cães e 10 gatos
simulate_multiple_rounds(n_dogs=10, n_cats=50, rounds=50)

# Plot
times, dogs, cats = zip(*logger.log)
plt.figure(figsize=(12, 6))
plt.plot(times, dogs, label="Cachorros na sala", color="blue", linewidth=1)
plt.plot(times, cats, label="Gatos na sala", color="orange", linewidth=1)
plt.xlabel("Tempo (s)")
plt.ylabel("Número de animais na sala")
plt.title("Simulação de acesso à sala com monitor - Múltiplas Rodadas")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("simulacao_monitor_plot_multiplas_rodadas.png")
plt.show()

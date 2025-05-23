
import threading
import time
import random
import matplotlib.pyplot as plt

# Semáforos e variáveis globais
mutex = threading.Semaphore(1)
dogSem = threading.Semaphore(1)
catSem = threading.Semaphore(1)

dogsInRoom = 0
catsInRoom = 0

# Medições de tempo de espera
wait_times_dogs = []
wait_times_cats = []

# Locks para proteger acesso a listas de medição
time_lock = threading.Lock()

# Simulação de entrada e saída de cães
def dog(id):
    global dogsInRoom
    arrive_time = time.time()
    dogSem.acquire()
    mutex.acquire()
    if dogsInRoom == 0:
        catSem.acquire()
    dogsInRoom += 1
    mutex.release()
    dogSem.release()

    # Medir tempo de espera
    enter_time = time.time()
    with time_lock:
        wait_times_dogs.append(enter_time - arrive_time)

    time.sleep(random.uniform(0.1, 0.5))  # Tempo na sala

    mutex.acquire()
    dogsInRoom -= 1
    if dogsInRoom == 0:
        catSem.release()
    mutex.release()

# Simulação de entrada e saída de gatos
def cat(id):
    global catsInRoom
    arrive_time = time.time()
    catSem.acquire()
    mutex.acquire()
    if catsInRoom == 0:
        dogSem.acquire()
    catsInRoom += 1
    mutex.release()
    catSem.release()

    # Medir tempo de espera
    enter_time = time.time()
    with time_lock:
        wait_times_cats.append(enter_time - arrive_time)

    time.sleep(random.uniform(0.1, 0.5))  # Tempo na sala

    mutex.acquire()
    catsInRoom -= 1
    if catsInRoom == 0:
        dogSem.release()
    mutex.release()

# Função para simular vários cães e gatos
def simulate(num_animals=100):
    threads = []
    for i in range(num_animals):
        if random.choice([True, False]):
            t = threading.Thread(target=dog, args=(i,))
        else:
            t = threading.Thread(target=cat, args=(i,))
        threads.append(t)
        t.start()
        time.sleep(random.uniform(0.01, 0.05))  # Chegadas escalonadas

    for t in threads:
        t.join()

simulate()

# Gráficos
plt.figure(figsize=(10, 5))
plt.plot(wait_times_dogs, label="Cães - tempo de espera")
plt.plot(wait_times_cats, label="Gatos - tempo de espera")
plt.xlabel("Número de entrada")
plt.ylabel("Tempo de espera (s)")
plt.title("Tempo de espera de cães e gatos")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

import threading
import time
import random
from collections import deque
import matplotlib.pyplot as plt

# Estado compartilhado
room_state = "empty"  # "dogs", "cats", or "empty"
dogs_in_room = 0
cats_in_room = 0
dog_waiting = 0
cat_waiting = 0

# Estatísticas
stats = {
    "dogs_entered": 0,
    "cats_entered": 0,
    "dog_waits": 0,
    "cat_waits": 0,
    "dog_starvation": 0,
    "cat_starvation": 0,
    "contentions": 0,
}

# Locks e semáforos
mutex = threading.Lock()
dog_queue = threading.Semaphore(0)
cat_queue = threading.Semaphore(0)

# Constante de starvation
STARVATION_THRESHOLD = 2.0

# Coleta de dados ao longo do tempo
log_time = []
log_dogs_in_room = []
log_cats_in_room = []
log_dog_waiting = []
log_cat_waiting = []
log_dogs_entered = []
log_cats_entered = []
log_contentions = []
log_starvations = []

def dogWantsToEnter():
    global dogs_in_room, room_state, dog_waiting
    with mutex:
        start_wait = time.time()
        if room_state == "cats" or cat_waiting > 0:
            dog_waiting += 1
            stats["dog_waits"] += 1
            stats["contentions"] += 1
            mutex.release()
            dog_queue.acquire()
            mutex.acquire()
            dog_waiting -= 1
        wait_time = time.time() - start_wait
        if wait_time > STARVATION_THRESHOLD:
            stats["dog_starvation"] += 1
        if room_state == "empty":
            room_state = "dogs"
        dogs_in_room += 1
        stats["dogs_entered"] += 1

def catWantsToEnter():
    global cats_in_room, room_state, cat_waiting
    with mutex:
        start_wait = time.time()
        if room_state == "dogs" or dog_waiting > 0:
            cat_waiting += 1
            stats["cat_waits"] += 1
            stats["contentions"] += 1
            mutex.release()
            cat_queue.acquire()
            mutex.acquire()
            cat_waiting -= 1
        wait_time = time.time() - start_wait
        if wait_time > STARVATION_THRESHOLD:
            stats["cat_starvation"] += 1
        if room_state == "empty":
            room_state = "cats"
        cats_in_room += 1
        stats["cats_entered"] += 1

def dogLeaves():
    global dogs_in_room, room_state
    with mutex:
        dogs_in_room -= 1
        if dogs_in_room == 0:
            if cat_waiting > 0:
                room_state = "cats"
                for _ in range(cat_waiting):
                    cat_queue.release()
            else:
                room_state = "empty"

def catLeaves():
    global cats_in_room, room_state
    with mutex:
        cats_in_room -= 1
        if cats_in_room == 0:
            if dog_waiting > 0:
                room_state = "dogs"
                for _ in range(dog_waiting):
                    dog_queue.release()
            else:
                room_state = "empty"

def dog_thread():
    while True:
        time.sleep(random.uniform(0.01, 0.2))
        dogWantsToEnter()
        time.sleep(random.uniform(0.01, 0.1))
        dogLeaves()

def cat_thread():
    while True:
        time.sleep(random.uniform(0.01, 0.2))
        catWantsToEnter()
        time.sleep(random.uniform(0.01, 0.1))
        catLeaves()

def monitor_thread():
    start = time.time()
    while time.time() - start < 20:
        with mutex:
            log_time.append(time.time() - start)
            log_dogs_in_room.append(dogs_in_room)
            log_cats_in_room.append(cats_in_room)
            log_dog_waiting.append(dog_waiting)
            log_cat_waiting.append(cat_waiting)
            log_dogs_entered.append(stats["dogs_entered"])
            log_cats_entered.append(stats["cats_entered"])
            log_contentions.append(stats["contentions"])
            log_starvations.append(stats["dog_starvation"] + stats["cat_starvation"])
        time.sleep(0.5)

# Iniciar simulação
threads = []

for _ in range(5):
    t = threading.Thread(target=dog_thread, daemon=True)
    t.start()
    threads.append(t)

for _ in range(5):
    t = threading.Thread(target=cat_thread, daemon=True)
    t.start()
    threads.append(t)

monitor = threading.Thread(target=monitor_thread)
monitor.start()
monitor.join()

# Plotar gráficos
import matplotlib.pyplot as plt

plt.figure(figsize=(12, 10))

plt.subplot(2, 2, 1)
plt.plot(log_time, log_dogs_in_room, label='Dogs in Room')
plt.plot(log_time, log_cats_in_room, label='Cats in Room')
plt.title('Animais na sala')
plt.xlabel('Tempo (s)')
plt.ylabel('Quantidade')
plt.legend()

plt.subplot(2, 2, 2)
plt.plot(log_time, log_dog_waiting, label='Dogs Waiting')
plt.plot(log_time, log_cat_waiting, label='Cats Waiting')
plt.title('Animais esperando')
plt.xlabel('Tempo (s)')
plt.ylabel('Quantidade')
plt.legend()

plt.subplot(2, 2, 3)
plt.plot(log_time, log_dogs_entered, label='Dogs Entered')
plt.plot(log_time, log_cats_entered, label='Cats Entered')
plt.title('Acúmulo de entradas')
plt.xlabel('Tempo (s)')
plt.ylabel('Total')
plt.legend()

plt.subplot(2, 2, 4)
plt.plot(log_time, log_contentions, label='Contenções')
plt.plot(log_time, log_starvations, label='Starvations')
plt.title('Conflitos e Starvation')
plt.xlabel('Tempo (s)')
plt.ylabel('Total')
plt.legend()

plt.tight_layout()
plt.show()

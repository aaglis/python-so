import threading
import time
import random

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

def dogWantsToEnter():
    global dogs_in_room, room_state, dog_waiting
    with mutex:
        if room_state == "cats" or cat_waiting > 0:
            dog_waiting += 1
            stats["dog_waits"] += 1
            stats["contentions"] += 1
            mutex.release()
            dog_queue.acquire()
            mutex.acquire()
            dog_waiting -= 1
        if room_state == "empty":
            room_state = "dogs"
        dogs_in_room += 1
        stats["dogs_entered"] += 1

def catWantsToEnter():
    global cats_in_room, room_state, cat_waiting
    with mutex:
        if room_state == "dogs" or dog_waiting > 0:
            cat_waiting += 1
            stats["cat_waits"] += 1
            stats["contentions"] += 1
            mutex.release()
            cat_queue.acquire()
            mutex.acquire()
            cat_waiting -= 1
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
    while running[0]:
        time.sleep(random.uniform(0.01, 0.2))
        dogWantsToEnter()
        time.sleep(random.uniform(0.01, 0.1))
        dogLeaves()

def cat_thread():
    while running[0]:
        time.sleep(random.uniform(0.01, 0.2))
        catWantsToEnter()
        time.sleep(random.uniform(0.01, 0.1))
        catLeaves()

# Início da simulação
running = [True]
threads = [threading.Thread(target=dog_thread) for _ in range(5)] + \
          [threading.Thread(target=cat_thread) for _ in range(5)]

for t in threads:
    t.start()

# Executar por 60 segundos
time.sleep(10)
running[0] = False

# Esperar threads finalizarem
for t in threads:
    t.join(timeout=1)

print("\n=== Estatísticas da Simulação ===")
for key, value in stats.items():
    print(f"{key}: {value}")

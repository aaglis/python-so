import matplotlib.pyplot as plt
import csv

data = []
labels = []

with open('relatorio_entrada_saida_animais.csv', 'r', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile)
    next(reader)  # Pula o cabeçalho

    for row in reader:
        animal = row[0]
        id_ = int(row[1])
        duracao = float(row[4])  # duração em segundos
        labels.append(f"{animal} {id_}")
        data.append(duracao)

# Plotar gráfico
plt.figure(figsize=(12, 6))
plt.bar(labels, data, color='skyblue')
plt.xticks(rotation=45, ha='right')
plt.title('Tempo de permanência de cada animal na sala')
plt.xlabel('Animal (ID)')
plt.ylabel('Duração (segundos)')
plt.tight_layout()
plt.show()

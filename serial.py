from collections import defaultdict
from datetime import datetime
import pandas as pd
import time

inicio = time.time()

df = pd.read_csv("reviews.csv")

soma = defaultdict(float)
contagem = defaultdict(int)

total = len(df)

for i, (_, row) in enumerate(df.iterrows(), start=1):

    produto = row["ProductId"]

    data = datetime.fromtimestamp(int(row["Time"]))
    chave_mes = f"{data.year}-{data.month:02d}"

    chave = (produto, chave_mes)

    score = float(row["Score"])

    soma[chave] += score
    contagem[chave] += 1

    x = 0.0

    for _ in range(1000):
        x += (score * score) / 5
        x = x ** 0.5
        x = x * x
        x += score

    if i % 10000 == 0:
        percentual = (i / total) * 100
        print(f"{i:,}/{total:,} ({percentual:.1f}%)")

fim = time.time()

tempo_total = fim - inicio

print("\n===================================")
print("PROCESSAMENTO CONCLUÍDO")
print("===================================")
print(f"Registros processados: {total:,}")
print(f"Tempo total: {tempo_total:.2f} segundos")
print(f"Tempo total: {tempo_total/60:.2f} minutos")

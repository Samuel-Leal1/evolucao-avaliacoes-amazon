"""
serial.py
---------
Solução SERIAL para calcular a evolução mensal da média de avaliações
do dataset Amazon Fine Food Reviews.

Disciplina: Programação Paralela
Dataset:    https://www.kaggle.com/datasets/snap/amazon-fine-food-reviews
"""

from collections import defaultdict
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
import time

RESULTADOS_DIR = "resultados"

# ─────────────────────────────────────────────
# 1. PROCESSAMENTO SERIAL
# ─────────────────────────────────────────────
inicio = time.time()

df = pd.read_csv("reviews.csv")

soma     = defaultdict(float)
contagem = defaultdict(int)
total    = len(df)

for i, (_, row) in enumerate(df.iterrows(), start=1):

    produto      = row["ProductId"]
    data         = datetime.fromtimestamp(int(row["Time"]))
    chave_mes    = f"{data.year}-{data.month:02d}"
    chave        = (produto, chave_mes)
    score        = float(row["Score"])

    soma[chave]     += score
    contagem[chave] += 1

    # Carga computacional artificial para simular processamento pesado
    x = 0.0
    for _ in range(1000):
        x += (score * score) / 5
        x  = x ** 0.5
        x  = x * x
        x += score

    if i % 10000 == 0:
        percentual = (i / total) * 100
        print(f"{i:,}/{total:,} ({percentual:.1f}%)")

fim         = time.time()
tempo_total = fim - inicio

print("\n===================================")
print("PROCESSAMENTO CONCLUÍDO")
print("===================================")
print(f"Registros processados: {total:,}")
print(f"Tempo total: {tempo_total:.2f} segundos")
print(f"Tempo total: {tempo_total/60:.2f} minutos")

# Salva tempo para uso no benchmark
os.makedirs(RESULTADOS_DIR, exist_ok=True)
with open(f"{RESULTADOS_DIR}/tempo_serial.txt", "w") as f:
    f.write(str(tempo_total))

# ─────────────────────────────────────────────
# 2. MONTAR RESULTADO
# ─────────────────────────────────────────────

# Agrupa apenas por mês (ignora produto) para a curva de evolução geral
soma_mes     = defaultdict(float)
contagem_mes = defaultdict(int)

for (produto, mes), s in soma.items():
    soma_mes[mes]     += s
    contagem_mes[mes] += contagem[(produto, mes)]

linhas = []
for mes in soma_mes:
    linhas.append({
        "AnoMes":        mes,
        "MediaNota":     soma_mes[mes] / contagem_mes[mes],
        "QtdAvaliacoes": contagem_mes[mes],
    })

resultado = (
    pd.DataFrame(linhas)
    .sort_values("AnoMes")
    .reset_index(drop=True)
)

# Salva CSV para uso no benchmark
resultado.to_csv(f"{RESULTADOS_DIR}/resultado_serial.csv", index=False)

# ─────────────────────────────────────────────
# 3. GRÁFICO — EVOLUÇÃO MENSAL
# ─────────────────────────────────────────────
datas       = pd.to_datetime(resultado["AnoMes"])
medias      = resultado["MediaNota"]
quantidades = resultado["QtdAvaliacoes"]

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True)
fig.suptitle(
    f"Evolução Mensal das Avaliações — Amazon Fine Food Reviews\n"
    f"Solução Serial  |  {total:,} registros  |  Tempo: {tempo_total:.2f}s ({tempo_total/60:.2f} min)",
    fontsize=13,
    fontweight="bold",
)

# --- Gráfico 1: Média mensal das notas ---
ax1.plot(datas, medias, color="#2196F3", linewidth=1.5, label="Média mensal")
ax1.axhline(
    y=medias.mean(),
    color="#F44336",
    linestyle="--",
    linewidth=1,
    label=f"Média geral: {medias.mean():.2f}",
)
ax1.set_ylabel("Média das Notas (1–5)", fontsize=11)
ax1.set_ylim(1, 5.5)
ax1.legend(fontsize=10)
ax1.grid(True, alpha=0.3)
ax1.set_title("Média Mensal das Notas", fontsize=11)

# --- Gráfico 2: Volume de avaliações por mês ---
ax2.bar(datas, quantidades, color="#4CAF50", alpha=0.7, width=20, label="Avaliações/mês")
ax2.set_ylabel("Qtd. de Avaliações", fontsize=11)
ax2.set_xlabel("Período (Mês/Ano)", fontsize=11)
ax2.legend(fontsize=10)
ax2.grid(True, alpha=0.3, axis="y")
ax2.set_title("Volume Mensal de Avaliações", fontsize=11)

ax2.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax2.xaxis.set_major_locator(mdates.YearLocator())
plt.xticks(rotation=45)

plt.tight_layout()

os.makedirs(f"{RESULTADOS_DIR}/graficos", exist_ok=True)
caminho = f"{RESULTADOS_DIR}/graficos/evolucao_serial.png"
plt.savefig(caminho, dpi=150, bbox_inches="tight")
print(f"\nGráfico salvo em: {caminho}")

plt.show()
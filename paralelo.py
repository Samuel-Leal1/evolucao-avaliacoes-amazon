"""
paralelo.py
-----------
Solução PARALELA para calcular a evolução mensal da média de avaliações
do dataset Amazon Fine Food Reviews.

Segue o padrão Map → Reduce:
  - MAP:    cada worker processa sua fatia do dataset com o mesmo loop pesado do serial
  - REDUCE: os resultados parciais são combinados para gerar a média final por mês

Testado com 2, 4, 8 e 12 workers.

Disciplina: Programação Paralela
Dataset:    https://www.kaggle.com/datasets/snap/amazon-fine-food-reviews
"""

from collections import defaultdict
from datetime import datetime
import multiprocessing
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
import time
import matplotlib
matplotlib.use("Agg")  

RESULTADOS_DIR = "resultados"


# ─────────────────────────────────────────────
# FASE MAP — executada por cada worker
# ─────────────────────────────────────────────
def processar_fatia(fatia: pd.DataFrame) -> dict:
    """
    Recebe uma fatia do dataset e executa o mesmo loop pesado da solução serial.
    Retorna um dicionário com soma e contagem por (produto, mes).
    """
    soma     = defaultdict(float)
    contagem = defaultdict(int)

    for _, row in fatia.iterrows():
        produto   = row["ProductId"]
        data      = datetime.fromtimestamp(int(row["Time"]))
        chave_mes = f"{data.year}-{data.month:02d}"
        chave     = (produto, chave_mes)
        score     = float(row["Score"])

        soma[chave]     += score
        contagem[chave] += 1

        # Mesma carga computacional artificial do serial
        x = 0.0
        for _ in range(1000):
            x += (score * score) / 5
            x  = x ** 0.5
            x  = x * x
            x += score

    return {"soma": dict(soma), "contagem": dict(contagem)}


# ─────────────────────────────────────────────
# FASE REDUCE — combina resultados dos workers
# ─────────────────────────────────────────────
def reduzir(resultados_parciais: list) -> pd.DataFrame:
    """
    Combina os dicionários parciais de todos os workers.
    Calcula a média final por mês (agrupando todos os produtos).
    """
    soma_total     = defaultdict(float)
    contagem_total = defaultdict(int)

    for parcial in resultados_parciais:
        for chave, s in parcial["soma"].items():
            soma_total[chave]     += s
            contagem_total[chave] += parcial["contagem"][chave]

    # Agrega por mês (ignora produto) para a curva de evolução geral
    soma_mes     = defaultdict(float)
    contagem_mes = defaultdict(int)

    for (produto, mes), s in soma_total.items():
        soma_mes[mes]     += s
        contagem_mes[mes] += contagem_total[(produto, mes)]

    linhas = []
    for mes in soma_mes:
        linhas.append({
            "AnoMes":        mes,
            "MediaNota":     soma_mes[mes] / contagem_mes[mes],
            "QtdAvaliacoes": contagem_mes[mes],
        })

    return (
        pd.DataFrame(linhas)
        .sort_values("AnoMes")
        .reset_index(drop=True)
    )


# ─────────────────────────────────────────────
# EXECUTAR COM N WORKERS
# ─────────────────────────────────────────────
def executar_paralelo(df: pd.DataFrame, n_workers: int) -> tuple:
    """
    Divide o dataframe em n_workers fatias iguais,
    processa cada fatia em um processo separado (MAP),
    e combina os resultados (REDUCE).

    Retorna (resultado_df, tempo_segundos)
    """
    print(f"\n[workers={n_workers}] Dividindo dataset em {n_workers} fatias...")
    fatias = [df.iloc[i::n_workers].copy() for i in range(n_workers)]

    print(f"[workers={n_workers}] Iniciando fase MAP com {n_workers} processos...")
    inicio = time.time()

    with multiprocessing.Pool(processes=n_workers) as pool:
        resultados_parciais = pool.map(processar_fatia, fatias)

    print(f"[workers={n_workers}] Fase MAP concluída. Iniciando REDUCE...")
    resultado = reduzir(resultados_parciais)

    fim   = time.time()
    tempo = fim - inicio

    print(f"[workers={n_workers}] Concluído em {tempo:.2f}s ({tempo/60:.2f} min)")
    return resultado, tempo


# ─────────────────────────────────────────────
# GRÁFICO — EVOLUÇÃO MENSAL (resultado da análise)
# ─────────────────────────────────────────────
def gerar_grafico_evolucao(resultado: pd.DataFrame, n_workers: int, tempo: float):
    datas       = pd.to_datetime(resultado["AnoMes"])
    medias      = resultado["MediaNota"]
    quantidades = resultado["QtdAvaliacoes"]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True)
    fig.suptitle(
        f"Evolução Mensal das Avaliações — Amazon Fine Food Reviews\n"
        f"Solução Paralela ({n_workers} workers)  |  "
        f"{resultado['QtdAvaliacoes'].sum():,} registros  |  "
        f"Tempo: {tempo:.2f}s ({tempo/60:.2f} min)",
        fontsize=13, fontweight="bold",
    )

    ax1.plot(datas, medias, color="#9C27B0", linewidth=1.5, label="Média mensal")
    ax1.axhline(y=medias.mean(), color="#F44336", linestyle="--", linewidth=1,
                label=f"Média geral: {medias.mean():.2f}")
    ax1.set_ylabel("Média das Notas (1–5)", fontsize=11)
    ax1.set_ylim(1, 5.5)
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    ax1.set_title("Média Mensal das Notas", fontsize=11)

    ax2.bar(datas, quantidades, color="#FF9800", alpha=0.7, width=20, label="Avaliações/mês")
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
    caminho = f"{RESULTADOS_DIR}/graficos/evolucao_paralelo_{n_workers}w.png"
    plt.savefig(caminho, dpi=150, bbox_inches="tight")
    print(f"Gráfico salvo em: {caminho}")
    plt.show()


# ─────────────────────────────────────────────
# GRÁFICO — SPEEDUP E EFICIÊNCIA
# ─────────────────────────────────────────────
def gerar_graficos_desempenho(tempo_serial: float, tempos_paralelos: dict):
    """
    Gera 4 gráficos de desempenho:
      1. Tempo de execução por número de workers
      2. Speedup real vs. ideal
      3. Eficiência
      4. Lei de Amdahl
    """
    workers  = sorted(tempos_paralelos.keys())
    tempos   = [tempos_paralelos[w] for w in workers]
    speedups = [tempo_serial / tempos_paralelos[w] for w in workers]
    efics    = [speedups[i] / workers[i] * 100 for i in range(len(workers))]

    # Lei de Amdahl — estima fração paralela com base nos speedups medidos
    # f = fração paralelizável (estimada pelo melhor speedup obtido)
    melhor_speedup = max(speedups)
    melhor_n       = workers[speedups.index(melhor_speedup)]
    f_estimado     = (1 - 1/melhor_speedup) / (1 - 1/melhor_n) if melhor_n > 1 else 0.9
    f_estimado     = min(f_estimado, 0.99)

    ns_amdahl    = list(range(1, 33))
    amdahl_ideal = [1 / ((1 - f_estimado) + f_estimado / n) for n in ns_amdahl]

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(
        "Métricas de Desempenho — Serial vs. Paralelo\nAmazon Fine Food Reviews",
        fontsize=14, fontweight="bold"
    )

    # --- Gráfico 1: Tempo de execução ---
    ax = axes[0, 0]
    todos_workers = [1] + workers
    todos_tempos  = [tempo_serial] + tempos
    ax.bar([str(w) for w in todos_workers], todos_tempos,
           color=["#F44336"] + ["#2196F3"] * len(workers), alpha=0.85)
    ax.set_title("Tempo de Execução", fontsize=12)
    ax.set_xlabel("Número de Workers")
    ax.set_ylabel("Tempo (segundos)")
    ax.grid(True, alpha=0.3, axis="y")
    for i, (w, t) in enumerate(zip(todos_workers, todos_tempos)):
        ax.text(i, t + 1, f"{t:.1f}s", ha="center", fontsize=9)

    # --- Gráfico 2: Speedup real vs. ideal ---
    ax = axes[0, 1]
    ax.plot(workers, speedups, "o-", color="#2196F3", linewidth=2,
            markersize=8, label="Speedup real")
    ax.plot(workers, workers, "--", color="#9E9E9E", linewidth=1.5,
            label="Speedup ideal (linear)")
    ax.set_title("Speedup", fontsize=12)
    ax.set_xlabel("Número de Workers")
    ax.set_ylabel("Speedup (vezes mais rápido)")
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    for w, s in zip(workers, speedups):
        ax.annotate(f"{s:.2f}x", (w, s), textcoords="offset points",
                    xytext=(5, 5), fontsize=9)

    # --- Gráfico 3: Eficiência ---
    ax = axes[1, 0]
    ax.plot(workers, efics, "s-", color="#4CAF50", linewidth=2,
            markersize=8, label="Eficiência real")
    ax.axhline(y=100, color="#9E9E9E", linestyle="--", linewidth=1.5,
               label="Eficiência ideal (100%)")
    ax.set_title("Eficiência", fontsize=12)
    ax.set_xlabel("Número de Workers")
    ax.set_ylabel("Eficiência (%)")
    ax.set_ylim(0, 115)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    for w, e in zip(workers, efics):
        ax.annotate(f"{e:.1f}%", (w, e), textcoords="offset points",
                    xytext=(5, 5), fontsize=9)

    # --- Gráfico 4: Lei de Amdahl ---
    ax = axes[1, 1]
    ax.plot(ns_amdahl, amdahl_ideal, "-", color="#FF9800", linewidth=2,
            label=f"Amdahl (f={f_estimado:.2f})")
    ax.plot(workers, speedups, "o", color="#2196F3", markersize=8,
            label="Speedup real medido")
    ax.set_title("Lei de Amdahl", fontsize=12)
    ax.set_xlabel("Número de Workers")
    ax.set_ylabel("Speedup teórico máximo")
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    caminho = f"{RESULTADOS_DIR}/graficos/desempenho_comparativo.png"
    plt.savefig(caminho, dpi=150, bbox_inches="tight")
    print(f"Gráfico de desempenho salvo em: {caminho}")
    plt.show()


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    print("=" * 60)
    print("  SOLUÇÃO PARALELA — Amazon Fine Food Reviews")
    print("=" * 60)

    # Carrega o tempo serial salvo pelo serial.py
    tempo_serial_path = f"{RESULTADOS_DIR}/tempo_serial.txt"
    if not os.path.exists(tempo_serial_path):
        print(f"\n[AVISO] Arquivo '{tempo_serial_path}' não encontrado.")
        print("        Usando tempo serial informado manualmente: 271.50s")
        tempo_serial = 271.50
    else:
        with open(tempo_serial_path) as f:
            tempo_serial = float(f.read().strip())
    print(f"\nTempo serial de referência: {tempo_serial:.2f}s")

    # Carrega dataset
    print("\nCarregando dataset...")
    df = pd.read_csv("reviews.csv")
    df = df.dropna(subset=["Score", "Time", "ProductId"])
    print(f"{len(df):,} avaliações carregadas.")

    # Executa com 2, 4, 8 e 12 workers
    configuracoes = [2, 4, 8, 12]
    tempos_paralelos = {}

    for n_workers in configuracoes:
        resultado, tempo = executar_paralelo(df, n_workers)
        tempos_paralelos[n_workers] = tempo
        gerar_grafico_evolucao(resultado, n_workers, tempo)

        # Salva resultado
        os.makedirs(RESULTADOS_DIR, exist_ok=True)
        resultado.to_csv(
            f"{RESULTADOS_DIR}/resultado_paralelo_{n_workers}w.csv", index=False
        )

    # Resumo final
    print("\n" + "=" * 60)
    print("  RESUMO DE DESEMPENHO")
    print("=" * 60)
    print(f"  {'Workers':<10} {'Tempo (s)':<15} {'Speedup':<12} {'Eficiência'}")
    print(f"  {'-'*10} {'-'*15} {'-'*12} {'-'*12}")
    print(f"  {'1 (serial)':<10} {tempo_serial:<15.2f} {'1.00x':<12} {'100.0%'}")
    for w in configuracoes:
        t = tempos_paralelos[w]
        s = tempo_serial / t
        e = s / w * 100
        print(f"  {w:<10} {t:<15.2f} {s:<12.2f} {e:.1f}%")
    print("=" * 60)

    # Salva tempos paralelos
    with open(f"{RESULTADOS_DIR}/tempos_paralelos.txt", "w") as f:
        for w, t in tempos_paralelos.items():
            f.write(f"{w},{t}\n")

    # Gera gráficos de desempenho
    gerar_graficos_desempenho(tempo_serial, tempos_paralelos)


if __name__ == "__main__":
    main()
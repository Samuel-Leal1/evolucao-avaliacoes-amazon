"""
serial.py
---------
Solução SERIAL para calcular a evolução mensal da média de avaliações
do dataset Amazon Fine Food Reviews.

Disciplina: Programação Paralela
Dataset:    https://www.kaggle.com/datasets/snap/amazon-fine-food-reviews
"""

import time
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os

# ─────────────────────────────────────────────
# CONFIGURAÇÕES
# ─────────────────────────────────────────────
DATASET_PATH = "data/Reviews.csv"
RESULTADOS_DIR = "resultados"
COLUNAS_USADAS = ["ProductId", "Score", "Time"]


# ─────────────────────────────────────────────
# 1. CARREGAR OS DADOS
# ─────────────────────────────────────────────
def carregar_dados(path: str) -> pd.DataFrame:
    """
    Carrega o dataset e mantém apenas as colunas necessárias.
    """
    print(f"[1/4] Carregando dataset: {path}")
    df = pd.read_csv(path, usecols=COLUNAS_USADAS)
    print(f"      {len(df):,} avaliações carregadas.")
    return df


# ─────────────────────────────────────────────
# 2. PRÉ-PROCESSAMENTO
# ─────────────────────────────────────────────
def preprocessar(df: pd.DataFrame) -> pd.DataFrame:
    """
    Converte o timestamp Unix para o formato Ano-Mês (período mensal).
    Remove linhas com valores nulos em Score ou Time.
    """
    print("[2/4] Pré-processando dados...")

    # Remove nulos
    df = df.dropna(subset=["Score", "Time"])

    # Converte timestamp Unix → datetime → período mensal (ex: 2005-03)
    df["AnoMes"] = pd.to_datetime(df["Time"], unit="s").dt.to_period("M")

    print(f"      Período: {df['AnoMes'].min()} até {df['AnoMes'].max()}")
    return df


# ─────────────────────────────────────────────
# 3. PROCESSAMENTO SERIAL — CÁLCULO DA MÉDIA MENSAL
# ─────────────────────────────────────────────
def calcular_media_mensal_serial(df: pd.DataFrame) -> pd.DataFrame:
    """
    Percorre todas as 568.454 avaliações sequencialmente.
    Para cada mês, calcula a média geral das notas.

    Retorna um DataFrame com colunas: AnoMes, MediaNota, QtdAvaliacoes
    """
    print("[3/4] Calculando média mensal (modo SERIAL)...")

    inicio = time.time()

    # Agrupa por AnoMes e calcula média e contagem — processamento sequencial
    resultado = (
        df.groupby("AnoMes")["Score"]
        .agg(MediaNota="mean", QtdAvaliacoes="count")
        .reset_index()
        .sort_values("AnoMes")
    )

    fim = time.time()
    tempo_total = fim - inicio

    print(f"      Concluído em {tempo_total:.4f} segundos.")
    print(f"      {len(resultado)} meses calculados.")

    # Salva o tempo para uso no benchmark
    resultado.attrs["tempo_serial"] = tempo_total

    return resultado


# ─────────────────────────────────────────────
# 4. GERAR GRÁFICO — EVOLUÇÃO MENSAL
# ─────────────────────────────────────────────
def gerar_grafico(resultado: pd.DataFrame, salvar: bool = True):
    """
    Plota a curva de evolução mensal da média das avaliações.
    """
    print("[4/4] Gerando gráfico...")

    # Converte período para datetime para o matplotlib
    datas = resultado["AnoMes"].dt.to_timestamp()
    medias = resultado["MediaNota"]
    quantidades = resultado["QtdAvaliacoes"]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True)
    fig.suptitle(
        "Evolução Mensal das Avaliações — Amazon Fine Food Reviews\n(Solução Serial)",
        fontsize=14,
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
    ax1.set_ylim(1, 5.2)
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

    # Formata eixo X
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax2.xaxis.set_major_locator(mdates.YearLocator())
    plt.xticks(rotation=45)

    plt.tight_layout()

    if salvar:
        os.makedirs(f"{RESULTADOS_DIR}/graficos", exist_ok=True)
        caminho = f"{RESULTADOS_DIR}/graficos/evolucao_serial.png"
        plt.savefig(caminho, dpi=150, bbox_inches="tight")
        print(f"      Gráfico salvo em: {caminho}")

    plt.show()


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    print("=" * 55)
    print("  SOLUÇÃO SERIAL — Amazon Fine Food Reviews")
    print("=" * 55)

    # Verifica se o dataset existe
    if not os.path.exists(DATASET_PATH):
        print(f"\n[ERRO] Dataset não encontrado em '{DATASET_PATH}'.")
        print("       Baixe o arquivo Reviews.csv em:")
        print("       https://www.kaggle.com/datasets/snap/amazon-fine-food-reviews")
        print("       e coloque-o na pasta 'data/'.\n")
        return

    # Pipeline serial
    df = carregar_dados(DATASET_PATH)
    df = preprocessar(df)
    resultado = calcular_media_mensal_serial(df)
    gerar_grafico(resultado)

    # Resumo final
    tempo = resultado.attrs["tempo_serial"]
    print()
    print("=" * 55)
    print(f"  Tempo total (serial): {tempo:.4f} segundos")
    print(f"  Meses analisados:     {len(resultado)}")
    print(f"  Avaliações totais:    {resultado['QtdAvaliacoes'].sum():,}")
    print(f"  Média geral:          {resultado['MediaNota'].mean():.4f}")
    print("=" * 55)

    # Salva resultado em CSV para uso no benchmark
    os.makedirs(RESULTADOS_DIR, exist_ok=True)
    resultado.to_csv(f"{RESULTADOS_DIR}/resultado_serial.csv", index=False)
    print(f"\n  Resultado salvo em: {RESULTADOS_DIR}/resultado_serial.csv")


if __name__ == "__main__":
    main()

# 📊 evolucao-avaliacoes-amazon

Análise serial e paralela da evolução temporal de avaliações de produtos alimentícios da Amazon (2002–2012), com medição de speedup e eficiência usando multiprocessing em Python.

---

## 📌 Descrição do Projeto

Este projeto tem como objetivo comparar o desempenho de uma **solução serial** e uma **solução paralela** para calcular a evolução média das avaliações de produtos ao longo do tempo, utilizando o dataset público **Amazon Fine Food Reviews**.

O problema consiste em, para cada um dos 74.258 produtos presentes no dataset, calcular a **média mensal das notas** atribuídas pelos consumidores ao longo de todo o período disponível (outubro de 1999 a outubro de 2012), produzindo uma curva de evolução de reputação para cada produto.

Este trabalho foi desenvolvido como projeto prático da disciplina de **Programação Paralela**.

---

## 🗃️ Base de Dados

| Atributo | Valor |
|---|---|
| **Nome** | Amazon Fine Food Reviews |
| **Fonte** | [Kaggle](https://www.kaggle.com/datasets/snap/amazon-fine-food-reviews) / [Stanford SNAP](https://snap.stanford.edu/data/web-FineFoods.html) |
| **Total de avaliações** | 568.454 |
| **Total de usuários** | 256.059 |
| **Total de produtos** | 74.258 |
| **Período coberto** | Outubro de 1999 – Outubro de 2012 |
| **Origem** | McAuley e Leskovec, Stanford University, WWW 2013 |

### Colunas disponíveis

| Coluna | Tipo | Descrição |
|---|---|---|
| `ProductId` | Categórico | Identificador único do produto |
| `UserId` | Categórico | Identificador único do usuário |
| `ProfileName` | Texto | Nome do perfil do avaliador |
| `HelpfulnessNumerator` | Numérico | Votos que consideraram a avaliação útil |
| `HelpfulnessDenominator` | Numérico | Total de votos recebidos pela avaliação |
| `Score` | Numérico (1–5) | Nota atribuída ao produto |
| `Time` | Timestamp Unix | Data exata da avaliação |
| `Summary` | Texto | Título curto da avaliação |
| `Text` | Texto | Texto completo da avaliação |

---

## ⚙️ O que o programa faz

Para cada produto, o processamento segue os seguintes passos:

1. Filtrar todas as avaliações do produto
2. Converter o timestamp Unix para ano/mês
3. Agrupar as avaliações por mês
4. Calcular a média das notas em cada mês
5. Armazenar a série temporal resultante

### Solução Serial
Os 74.258 produtos são processados **um por vez**, de forma sequencial.

### Solução Paralela
Os produtos são **divididos entre múltiplos workers** com `multiprocessing.Pool`, de forma que vários produtos sejam processados simultaneamente. Cada produto é completamente independente dos demais, o que caracteriza um problema *embarrassingly parallel*.

---

## 📐 Métricas avaliadas

- **Tempo de execução** — serial vs. paralelo com 2, 4 e 8 workers
- **Speedup** — `Tempo serial ÷ Tempo paralelo`
- **Eficiência** — `Speedup ÷ Número de workers`
- **Lei de Amdahl** — limite teórico do ganho com base na fração paralelizável

---

## 🛠️ Tecnologias utilizadas

- Python 3.x
- Pandas
- Multiprocessing (biblioteca nativa do Python)
- Matplotlib / Seaborn (gráficos)
- Jupyter Notebook (exploração dos dados)

---

## 📁 Estrutura do repositório

```
evolucao-avaliacoes-amazon/
│
├── data/
│   └── Reviews.csv               # Dataset (baixar do Kaggle)
│
├── src/
│   ├── serial.py                 # Solução serial
│   ├── paralelo.py               # Solução paralela com multiprocessing
│   └── benchmark.py              # Medição de tempo, speedup e gráficos
│
├── notebooks/
│   └── exploracao.ipynb          # Análise exploratória do dataset
│
├── resultados/
│   └── graficos/                 # Gráficos gerados pelo benchmark
│
├── requirements.txt
└── README.md
```

---

## 🚀 Como executar

**1. Clone o repositório**
```bash
git clone https://github.com/seu-usuario/evolucao-avaliacoes-amazon.git
cd evolucao-avaliacoes-amazon
```

**2. Instale as dependências**
```bash
pip install -r requirements.txt
```

**3. Baixe o dataset**

Acesse [kaggle.com/datasets/snap/amazon-fine-food-reviews](https://www.kaggle.com/datasets/snap/amazon-fine-food-reviews), baixe o arquivo `Reviews.csv` e coloque-o na pasta `data/`.

**4. Execute o benchmark**
```bash
python src/benchmark.py
```

---

## 📚 Referência

> J. McAuley and J. Leskovec. *From amateurs to connoisseurs: modeling the evolution of user expertise through online reviews*. WWW, 2013.

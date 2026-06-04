## 📌 Descrição do Projeto

Este projeto tem como objetivo comparar o desempenho de uma **solução serial** e uma **solução paralela** para calcular a evolução média das avaliações de produtos ao longo do tempo, utilizando o dataset público **Amazon Fine Food Reviews**.

O problema consiste em calcular a **média mensal das notas** de todos os produtos ao longo de todo o período disponível (outubro de 1999 a outubro de 2012), produzindo uma curva de evolução de reputação para cada produto. Para isso, as **568.454 avaliações** são processadas seguindo o padrão **Map → Reduce**: na fase Map, os dados são divididos entre workers que calculam médias parciais em paralelo; na fase Reduce, os resultados parciais são combinados para gerar a evolução final por produto.

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

O processamento segue os seguintes passos:

1. Carregar as 568.454 avaliações do dataset
2. Converter o timestamp Unix para ano/mês
3. Agrupar as avaliações por produto e por mês
4. Calcular a média das notas em cada mês para cada produto
5. Armazenar a série temporal resultante por produto

### Solução Serial
As 568.454 avaliações são processadas **de uma vez**, de forma sequencial, calculando diretamente a média mensal por produto.

### Solução Paralela
A solução paralela segue o padrão clássico **Map → Reduce**:

**Fase MAP** — as 568.454 avaliações são divididas em fatias iguais entre os workers. Cada worker processa sua fatia de forma independente e calcula médias parciais por produto por mês.

```
Worker 1 → avaliações 1 a 142.113       → médias parciais
Worker 2 → avaliações 142.114 a 284.226 → médias parciais
Worker 3 → avaliações 284.227 a 426.339 → médias parciais
Worker 4 → avaliações 426.340 a 568.454 → médias parciais
```

**Fase REDUCE** — os resultados parciais de todos os workers são combinados para produzir a evolução mensal final de cada produto.

```
médias parciais do worker 1 ┐
médias parciais do worker 2 ├→ REDUCE → evolução final por produto
médias parciais do worker 3 │
médias parciais do worker 4 ┘
```

---

## 📐 Métricas avaliadas

- **Tempo de execução** — serial vs. paralelo com 2, 4 e 8 workers
- **Speedup** — `Tempo serial ÷ Tempo paralelo`
- **Eficiência** — `Speedup ÷ Número de workers`
- **Lei de Amdahl** — limite teórico do ganho com base na fração paralelizável

---

## ⏱️ Resultados medidos

Medições realizadas com processamento linha a linha (loop Python puro + carga computacional artificial por registro) sobre **568.454 avaliações reais**.

### Solução Serial — tempo medido

| Métrica | Valor |
|---|---|
| **Registros processados** | 568.454 |
| **Tempo de execução (s)** | 271,50 segundos |
| **Tempo de execução (min)** | 4,52 minutos |

> Medição realizada com processamento linha a linha (loop Python puro + carga computacional artificial por registro). Os resultados da solução paralela serão adicionados após a execução do `benchmark.py`.

<img width="212" height="89" alt="image" src="https://github.com/user-attachments/assets/eb085790-06c6-4927-8dac-cc0b6799e62a" />

### Tempos de execução

| Workers | Tempo (s) | Tempo (min) |
|---|---|---|
| 1 (serial) | 271,50s | 4,52 min |
| 2 | 58,64s | 0,98 min |
| 4 | 30,57s | 0,51 min |
| 8 | 22,41s | 0,37 min |
| 12 | 22,29s | 0,37 min |

### Speedup e Eficiência

| Workers | Speedup | Eficiência |
|---|---|---|
| 1 (serial) | 1,00x | 100,0% |
| 2 | 4,63x | 231,5% |
| 4 | 8,88x | 222,0% |
| 8 | 12,11x | 151,4% |
| 12 | 12,18x | 101,5% |

> O speedup superlinear com 2 e 4 workers é explicado pelo melhor aproveitamento do cache da CPU com fatias menores. O platô entre 8 e 12 workers reflete o limite físico de núcleos da máquina utilizada, ilustrando na prática a **Lei de Amdahl**. A solução paralela com 8 workers reduziu o tempo de execução em **91,8%** em relação à solução serial.

<img width="2077" height="1475" alt="desempenho_comparativo" src="https://github.com/user-attachments/assets/d5c02a18-7ab1-4fd0-8c11-39edc3512d6c" />

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
├── scripts/
│   ├── serial.py                 # Solução serial
│   ├── paralelo.py               # Solução paralela com multiprocessing
│
├── evidencias/
│   ├── serial.png
│   ├── serial.png
│   ├── serial.png
│
└── README.md
```


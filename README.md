# Simulação de Portefólio ETF

## Visão geral
Script interativo em Python que simula a evolução de um portefólio com aportes anuais e rendimentos anuais (personalizados ou baseados no histórico do S&P500). Suporta duas estratégias de retirada:

1. **Valor Fixo** (com opção de “dobrar retiradas” acima de um teto)  
2. **4% Anual (líquido)**, a partir do momento em que atinge o target  

## Requisitos
- Python 3.8+  
- Bibliotecas: `numpy`, `pandas`

## Como executar
Execute o script no terminal:

```bash
python Simulacao_Interativa_2.py
````
Ou colar e correr num compiler como o https://www.online-python.com/

## Fluxo de perguntas (passo a passo)

### 1) Tipo de simulação

* `1` — Retornos personalizados (média/desvio)
* `2` — Histórico real do S\&P500

### 2) Estratégia de retirada

* `1` — Valor fixo
* `2` — 4% Anual (líquido)

### 3) Perguntas comuns (sempre feitas)

* Quantos anos quer simular?
* Capital inicial (€)
* Contribuição mensal inicial (14/ano) (€)
* Crescimento anual das contribuições (ex: 0.02 para 2%)
* Target para começar a retirar dinheiro (€)
* Limite mínimo para poder retirar (€)

  * Protege o capital: se o saldo ficar abaixo deste limite, não há retirada naquele ano.

### 4) Perguntas específicas por estratégia

* **Se escolher 1 — Valor fixo:**

  * Valor para dobrar retiradas (€)

    * Se o saldo atingir este teto, o valor líquido anual de retirada é dobrado naquele ano.
  * Valor líquido anual inicial para retirar (€)

    * Base do valor líquido desejado; pode crescer conforme `withdrawal_growth_rate` definido na função (padrão 0%).

* **Se escolher 2 — 4% Anual (líquido):**

  * Nada adicional é perguntado aqui.
  * Ao atingir o target, retira-se 4% líquido do saldo de início do ano de retirada. O valor acompanha o crescimento do portefólio.

### 5) Impostos e progressão de contribuições

* Taxa de imposto sobre mais‑valias (ex: 0.198 para 19.8%)

  * O imposto incide sobre as mais‑valias na retirada; o script calcula o bruto necessário para atingir o líquido desejado.
* De quanto em quanto tempo aumentar contribuição anual (anos)

  * Intervalo (em anos) para subir a contribuição mensal.
* Aumento do valor mensal (€)

  * Quanto a contribuição mensal aumenta a cada intervalo.
* Limite máximo da contribuição mensal (€)

  * Teto para a contribuição mensal após os aumentos.

### 6) Parâmetros adicionais (apenas para “Retornos personalizados”)

* Média de retorno anual esperado (ex: 0.07 para 7%)
* Desvio padrão do retorno (ex: 0.15 para 15%)

## Como interpretar os resultados

Após a execução, o script imprime:

* `Fase de retirada inicia no ano: X`
* Uma tabela anual com colunas principais:

  * Ano, Fase, Saldo início (€), Contribuição (€), Retirada (€), Retirada líquida (€), Crescimento (%), Saldo final (€)
* `Total retirado ao longo dos anos (valor líquido): … €`

**Notas:**

* “Crescimento (%)” já considera a taxa de gestão anual subtraída dos retornos.
* Na estratégia 2 (4% Anual), o valor líquido de retirada é sempre 4% do saldo (respeitando o limite mínimo).
* Na estratégia 1, o “dobrar retiradas” aplica-se quando o saldo atinge o teto definido.

## Observações

* Pode definir um limite máximo para a contribuição mensal, útil quando há aumentos periódicos.
* Para reprodutibilidade de retornos personalizados, a função `simulation` aceita `seed`, embora não haja pergunta para isso na interface interativa.

```

Se quiseres, posso também fazer **uma versão ainda mais curta**, com tudo em poucas secções, ideal para um README minimalista. Quer que eu faça?
```

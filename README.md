# ETF Portfolio Simulation

## Overview
Interactive Python script that simulates the evolution of a portfolio with annual contributions and annual returns (customized or based on historical S&P500 data). Supports two withdrawal strategies:

1. **Fixed Amount** (with an option to “double withdrawals” above a set cap)  
2. **4% Annual (net)**, starting once the target is reached  

## Requirements
- Python 3.8+  
- Libraries: `numpy`, `pandas`

## How to run
Run the script in the terminal:

```bash
python Simulacao_Interativa_2.py
````

Or copy and run it in an online compiler like [https://www.online-python.com/](https://www.online-python.com/)

## Question Flow (Step by Step)

### 1) Type of simulation

* `1` — Custom returns (mean/std deviation)
* `2` — Historical S\&P500 data

### 2) Withdrawal strategy

* `1` — Fixed amount
* `2` — 4% Annual (net)

### 3) Common questions (always asked)

* How many years do you want to simulate?
* Initial capital (€)
* Initial monthly contribution (14/year) (€)
* Annual contribution growth (e.g., 0.02 for 2%)
* Target to start withdrawing money (€)
* Minimum threshold to allow withdrawals (€)

  * Protects capital: if the balance falls below this threshold, no withdrawal occurs that year.

### 4) Strategy-specific questions

* **If you choose 1 — Fixed amount:**

  * Amount to double withdrawals (€)

    * If the balance reaches this cap, the annual net withdrawal is doubled that year.
  * Initial annual net withdrawal (€)

    * Base of the desired net withdrawal; may grow according to the `withdrawal_growth_rate` defined in the function (default 0%).

* **If you choose 2 — 4% Annual (net):**

  * No additional questions are asked here.
  * Once the target is reached, withdraw 4% net of the starting balance of the withdrawal year. The amount grows with the portfolio.

### 5) Taxes and contribution progression

* Capital gains tax rate (e.g., 0.198 for 19.8%)

  * The tax applies to capital gains on withdrawals; the script calculates the gross amount needed to achieve the desired net.
* Contribution increase interval (years)

  * Interval (in years) to increase monthly contributions.
* Monthly contribution increase (€)

  * How much the monthly contribution increases at each interval.
* Maximum monthly contribution (€)

  * Cap for the monthly contribution after increases.

### 6) Additional parameters (only for “Custom returns”)

* Expected annual return (e.g., 0.07 for 7%)
* Standard deviation of returns (e.g., 0.15 for 15%)

## How to interpret results

After running the script, it prints:

* `Withdrawal phase starts in year: X`
* An annual table with main columns:

  * Year, Phase, Starting balance (€), Contribution (€), Withdrawal (€), Net withdrawal (€), Growth (%), Ending balance (€)
* `Total withdrawn over the years (net): … €`

**Notes:**

* “Growth (%)” already accounts for the annual management fee deducted from returns.
* In strategy 2 (4% Annual), the net withdrawal is always 4% of the balance (respecting the minimum threshold).
* In strategy 1, the “double withdrawals” rule applies when the balance reaches the defined cap.

## Observations

* You can set a maximum limit for the monthly contribution, useful when there are periodic increases.
* For reproducibility of custom returns, the `simulation` function accepts a `seed`, although this is not asked in the interactive interface.


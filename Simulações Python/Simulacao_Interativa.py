import numpy as np
import pandas as pd

def simulation(
    mode,
    total_years=55,
    initial_portfolio=20000,
    initial_monthly_contribution=200,
    contribution_multiplier=14,
    contribution_growth_rate=0.00,
    mean_return=0.07,
    std_return=0.15,
    management_fee=0.005,
    target_portfolio=400000,
    min_threshold=300000,
    upper_threshold=600000,
    withdrawal_base=20000,
    withdrawal_growth_rate=0.00,
    tax_rate_withdrawal=0.198,
    continue_contributions_during_withdrawal=False,
    contribution_step_up_interval=5,
    contribution_step_up_amount=100,
    max_monthly_contribution=None,
    seed=None
):
    # Histórico real do S&P500 (1969–2024)
    sp500_returns = [
        26.29, 25.02, -18.11, 28.71, 18.40, 31.49, -4.38, 21.83, 11.96, 1.38, 13.69,
        32.39, 16.00, 2.11, 15.06, 26.46, -37.00, 5.49, 15.79, 4.91, 10.88, 28.68,
        -22.10, -11.89, -9.10, 21.04, 28.58, 33.36, 22.96, 37.58, 1.32, 10.08, 7.62,
        30.47, -3.10, 31.69, 16.61, 5.25, 18.67, 31.73, 6.27, 22.56, 21.55, -4.91,
        32.42, 18.44, 6.56, -7.18, 23.84, 37.20, -26.47, -14.66, 18.98, 14.31, 4.01
    ]

    if seed is not None:
        np.random.seed(seed)

    portfolio = initial_portfolio
    phase = "Acumulação"
    current_withdrawal_net = withdrawal_base
    results = []
    withdrawal_start_year = None
    total_withdrawn = 0
    total_contributions = 0

    for year in range(1, total_years + 1):
        data = {}
        data["Ano"] = year
        data["Fase"] = phase
        data["Saldo inicio (€)"] = round(portfolio)

        # Aportes
        increment_periods = (year - 1) // contribution_step_up_interval
        adjusted_monthly_contribution = initial_monthly_contribution + (contribution_step_up_amount * increment_periods)
        if max_monthly_contribution is not None:
            adjusted_monthly_contribution = min(adjusted_monthly_contribution, max_monthly_contribution)

        annual_contribution = adjusted_monthly_contribution * contribution_multiplier
        annual_contribution *= (1 + contribution_growth_rate) ** (year - 1)

        # Transição para retirada
        if phase == "Acumulação" and portfolio >= target_portfolio:
            phase = "Retirada"
            withdrawal_start_year = year
            current_withdrawal_net = withdrawal_base
            data["Fase"] = phase

        if phase == "Acumulação":
            data["Contribuição (€)"] = round(annual_contribution)
            data["Retirada (€)"] = 0
            data["Retirada líquida (€)"] = 0
            portfolio += annual_contribution
            total_contributions += annual_contribution

            if mode == 1:
                annual_return = np.random.normal(loc=mean_return, scale=std_return)
            else:
                annual_return = sp500_returns[(year - 1) % len(sp500_returns)] / 100

            effective_return = annual_return - management_fee
            portfolio *= (1 + effective_return)
            data["Crescimento (%)"] = f"{round(effective_return*100)} %"

        else:  # fase de retirada
            this_contribution = annual_contribution if continue_contributions_during_withdrawal else 0
            data["Contribuição (€)"] = round(this_contribution)

            if continue_contributions_during_withdrawal:
                portfolio += this_contribution
                total_contributions += this_contribution

            if portfolio < min_threshold:
                data["Retirada (€)"] = 0
                data["Retirada líquida (€)"] = 0
            else:
                desired_net = current_withdrawal_net
                if portfolio >= upper_threshold:
                    desired_net *= 2

                capital_ratio = min(1.0, total_contributions / portfolio) if portfolio > 0 else 1.0
                gross_withdrawal = desired_net / (1 - tax_rate_withdrawal * (1 - capital_ratio))
                capital_withdrawn = gross_withdrawal * capital_ratio
                gain_withdrawn = gross_withdrawal - capital_withdrawn
                tax_paid = gain_withdrawn * tax_rate_withdrawal
                net_withdrawal = gross_withdrawal - tax_paid

                portfolio -= gross_withdrawal
                total_withdrawn += net_withdrawal
                data["Retirada (€)"] = round(gross_withdrawal)
                data["Retirada líquida (€)"] = round(net_withdrawal)

                current_withdrawal_net *= (1 + withdrawal_growth_rate)

            if mode == 1:
                annual_return = np.random.normal(loc=mean_return, scale=std_return)
            else:
                annual_return = sp500_returns[(year - 1) % len(sp500_returns)] / 100

            effective_return = annual_return - management_fee
            portfolio *= (1 + effective_return)
            data["Crescimento (%)"] = f"{round(effective_return*100)} %"

        data["Saldo final (€)"] = round(portfolio)
        results.append(data)

    df = pd.DataFrame(results)
    pd.options.display.float_format = '{:,.0f}'.format
    return df, withdrawal_start_year, round(total_withdrawn)


# ============================
# Interface interativa
# ============================

print("""
Escolha o tipo de simulação:
1 - Retornos personalizados (média em %/desvio)
2 - Histórico real do S&P500
""")
mode = int(input("Opção: "))

total_years = int(input("Quantos anos quer simular? "))
initial_portfolio = float(input("Capital inicial (€): "))
initial_monthly_contribution = float(input("Contribuição mensal inicial (14/ano) (€): "))
contribution_growth_rate = float(input("Crescimento anual das contribuições (ex: 0.02 para 2%): "))
target_portfolio = float(input("Target para começar a retirar dinheiro (€): "))
min_threshold = float(input("Limite mínimo para poder retirar (serve para proteger o capital no caso de queda) (€): "))
upper_threshold = float(input("Valor para dobrar retiradas (serve para aproveitar ao máximo o crescimento do portfolio) (€): "))
withdrawal_base = float(input("Valor líquido anual inicial para retirar (€): "))
tax_rate_withdrawal = float(input("Taxa de imposto sobre mais-valias (ex: 0.198 para 19.8%): "))
continue_contributions = input("Continuar a contribuir durante a fase de retirada? (s/n): ").lower() == "s"
contribution_step_up_interval = int(input("De quanto em quanto tempo aumentar contribuição anual (anos): "))
contribution_step_up_amount = float(input("Aumento do valor mensal (€): "))
max_monthly_contribution = float(input("Limite máximo da contribuição mensal (€): "))

if mode == 1:
    mean_return = float(input("Média de retorno anual esperado (ex: 0.07 para 7%): "))
    std_return = float(input("Desvio padrão do retorno (ex: 0.15 para 15%): "))
else:
    mean_return, std_return = 0, 0

df_results, start_withdrawal, total_withdrawn = simulation(
    mode,
    total_years=total_years,
    initial_portfolio=initial_portfolio,
    initial_monthly_contribution=initial_monthly_contribution,
    contribution_growth_rate=contribution_growth_rate,
    mean_return=mean_return,
    std_return=std_return,
    target_portfolio=target_portfolio,
    min_threshold=min_threshold,
    upper_threshold=upper_threshold,
    withdrawal_base=withdrawal_base,
    tax_rate_withdrawal=tax_rate_withdrawal,
    continue_contributions_during_withdrawal=continue_contributions,
    contribution_step_up_interval=contribution_step_up_interval,
    contribution_step_up_amount=contribution_step_up_amount,
    max_monthly_contribution=max_monthly_contribution
)

print("\n================ RESULTADOS ================\n")
print("Fase de retirada inicia no ano:", start_withdrawal)
print(df_results.to_string(index=False))
print(f"\nTotal retirado ao longo dos anos (valor líquido): {total_withdrawn} €")

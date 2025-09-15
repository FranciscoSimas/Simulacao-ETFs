import numpy as np
import pandas as pd

def monte_carlo_simulation_modified(
    total_years=55,
    initial_portfolio=20000,
    initial_monthly_contribution=400,
    contribution_multiplier=14,
    contribution_growth_rate=0.00,
    management_fee=0.005,
    target_portfolio=500000,
    min_threshold=200000,
    upper_threshold=1000000,
    withdrawal_base=15000,  # líquido
    withdrawal_growth_rate=0.00,
    tax_rate_withdrawal=0.198,
    continue_contributions_during_withdrawal=False,
    contribution_step_down_interval=5,
    contribution_step_down_amount=50,
    min_monthly_contribution=200,
):
    # Retornos reais do S&P500 (1969–2024), em percentagem total anual (total return)
    sp500_returns = [
        26.29, 25.02, -18.11, 28.71, 18.40, 31.49, -4.38, 21.83, 11.96, 1.38, 13.69,
        32.39, 16.00, 2.11, 15.06, 26.46, -37.00, 5.49, 15.79, 4.91, 10.88, 28.68,
        -22.10, -11.89, -9.10, 21.04, 28.58, 33.36, 22.96, 37.58, 1.32, 10.08, 7.62,
        30.47, -3.10, 31.69, 16.61, 5.25, 18.67, 31.73, 6.27, 22.56, 21.55, -4.91,
        32.42, 18.44, 6.56, -7.18, 23.84, 37.20, -26.47, -14.66, 18.98, 14.31, 4.01
    ]

    portfolio = initial_portfolio
    phase = "Acumulação"
    current_withdrawal_net = withdrawal_base  # líquido
    results = []
    withdrawal_start_year = None
    total_withdrawn = 0.0
    total_contributions = 0.0
    negative_years = 0

    for year in range(1, total_years + 1):
        data = {}
        data["Ano"] = year
        data["Fase"] = phase
        data["Saldo inicio (€)"] = portfolio

        # Aporte anual ajustado com decrescimento
        decrement_periods = (year - 1) // contribution_step_down_interval
        adjusted_monthly_contribution = max(
            initial_monthly_contribution - (contribution_step_down_amount * decrement_periods),
            min_monthly_contribution
        )
        annual_contribution = adjusted_monthly_contribution * contribution_multiplier
        annual_contribution *= (1 + contribution_growth_rate) ** (year - 1)

        # Muda para fase de retirada
        if phase == "Acumulação" and portfolio >= target_portfolio:
            phase = "Retirada"
            withdrawal_start_year = year
            current_withdrawal_net = withdrawal_base
            data["Fase"] = phase

        if phase == "Acumulação":
            data["Contribuição (€)"] = annual_contribution
            data["Retirada (€)"] = 0.0
            data["Retirada Real após imposto (€)"] = 0.0
            portfolio += annual_contribution
            total_contributions += annual_contribution

            # Retorno histórico fixo
            annual_return = sp500_returns[year-1] / 100
            effective_return = annual_return - management_fee

            portfolio *= (1 + effective_return)
            data["Crescimento anual (%)"] = f"{effective_return * 100:.2f} %"

        else:
            this_contribution = annual_contribution if continue_contributions_during_withdrawal else 0.0
            data["Contribuição (€)"] = this_contribution

            if portfolio < min_threshold:
                data["Retirada (€)"] = 0.0
                data["Retirada Real após imposto (€)"] = 0.0
                if continue_contributions_during_withdrawal:
                    portfolio += this_contribution
                    total_contributions += this_contribution

                # Retorno histórico fixo
                annual_return = sp500_returns[year-1] / 100
                effective_return = annual_return - management_fee

                portfolio *= (1 + effective_return)
                data["Crescimento anual (%)"] = f"{effective_return * 100:.2f} %"

            else:
                if continue_contributions_during_withdrawal:
                    portfolio += this_contribution
                    total_contributions += this_contribution

                # Define valor líquido desejado e calcula retirada bruta
                desired_net = current_withdrawal_net
                if portfolio >= upper_threshold:
                    desired_net *= 2

                capital_ratio = min(1.0, total_contributions / portfolio) if portfolio > 0 else 1.0
                gross_withdrawal = desired_net / (1 - tax_rate_withdrawal * (1 - capital_ratio))

                capital_withdrawn = gross_withdrawal * capital_ratio
                gain_withdrawn = gross_withdrawal - capital_withdrawn
                tax_paid = gain_withdrawn * tax_rate_withdrawal
                net_withdrawal = gross_withdrawal - tax_paid

                data["Retirada (€)"] = gross_withdrawal
                data["Retirada Real após imposto (€)"] = net_withdrawal

                portfolio -= gross_withdrawal
                total_withdrawn += net_withdrawal

                # Retorno histórico fixo
                annual_return = sp500_returns[year-1] / 100
                effective_return = annual_return - management_fee

                portfolio *= (1 + effective_return)
                data["Crescimento anual (%)"] = f"{effective_return * 100:.2f} %"

                current_withdrawal_net *= (1 + withdrawal_growth_rate)

        data["Saldo final (€)"] = portfolio
        results.append(data)

    df = pd.DataFrame(results)
    pd.options.display.float_format = '{:,.2f}'.format
    return df, withdrawal_start_year, total_withdrawn


# Exemplo de uso
df_results, start_withdrawal, total_withdrawn = monte_carlo_simulation_modified()

print("Fase de retirada inicia no ano:", start_withdrawal)
print(df_results.to_string(index=False))
print(f"\nTotal retirado ao longo dos anos (valor líquido): {total_withdrawn:.2f} €")

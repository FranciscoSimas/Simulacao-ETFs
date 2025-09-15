import numpy as np
import pandas as pd

def monte_carlo_simulation_modified(
    total_years=55,
    initial_portfolio=2500,
    initial_monthly_contribution=200,
    contribution_multiplier=14,
    contribution_growth_rate=0.00,
    mean_return=0.12,
    std_return=0.00,
    management_fee=0.005,
    target_portfolio=400000,
    min_threshold=100000,
    upper_threshold=550000,
    withdrawal_base=30000,  # líquido
    withdrawal_growth_rate=0.00,
    tax_rate_withdrawal=0.198,
    continue_contributions_during_withdrawal=False,
    contribution_step_down_interval=5,
    contribution_step_down_amount=50,
    min_monthly_contribution=200,
    seed=None
):
    if seed is not None:
        np.random.seed(seed)

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

            annual_return = np.random.normal(loc=mean_return, scale=std_return)
            effective_return = annual_return - management_fee

            if effective_return < 0:
                if negative_years < 12:
                    negative_years += 1
                else:
                    effective_return = 0.0

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

                annual_return = np.random.normal(loc=mean_return, scale=std_return)
                effective_return = annual_return - management_fee

                if effective_return < 0:
                    if negative_years < 12:
                        negative_years += 1
                    else:
                        effective_return = 0.0

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

                annual_return = np.random.normal(loc=mean_return, scale=std_return)
                effective_return = annual_return - management_fee

                if effective_return < 0:
                    if negative_years < 12:
                        negative_years += 1
                    else:
                        effective_return = 0.0

                portfolio *= (1 + effective_return)
                data["Crescimento anual (%)"] = f"{effective_return * 100:.2f} %"

                current_withdrawal_net *= (1 + withdrawal_growth_rate)

        data["Saldo final (€)"] = portfolio
        results.append(data)

    df = pd.DataFrame(results)
    pd.options.display.float_format = '{:,.2f}'.format
    return df, withdrawal_start_year, total_withdrawn


# Exemplo de uso
df_results, start_withdrawal, total_withdrawn = monte_carlo_simulation_modified(
    total_years=55,
    initial_portfolio=2500,
    initial_monthly_contribution=400,
    contribution_multiplier=14,
    contribution_growth_rate=0.00,
    mean_return=0.105,
    std_return=0.00,
    management_fee=0.005,
    target_portfolio=400000,
    min_threshold=400000,
    upper_threshold=550000,
    withdrawal_base=30000,  # líquido
    withdrawal_growth_rate=0.00,
    tax_rate_withdrawal=0.198,
    continue_contributions_during_withdrawal=False,
    contribution_step_down_interval=15,
    contribution_step_down_amount=200,
    min_monthly_contribution=200,
    seed=None
)

print("Fase de retirada inicia no ano:", start_withdrawal)
print(df_results.to_string(index=False))
print(f"\nTotal retirado ao longo dos anos (valor líquido): {total_withdrawn:.2f} €")
import numpy as np
import pandas as pd

def format_number_pt(value, decimals=2):
    try:
        return f"{value:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except (TypeError, ValueError):
        return str(value)

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
    withdrawal_strategy=1,  # 1 = Valor fixo, 2 = 4% anual líquido
    seed=None,
    returns_input_frequency="annual"  # "annual" or "monthly" for custom returns
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
    total_withdrawn = 0.0
    total_contributions = 0.0

    # Preparar fatores mensais
    def annual_to_monthly_rate(r_annual: float) -> float:
        return (1.0 + r_annual) ** (1.0 / 12.0) - 1.0

    # Converter comissão de gestão anual para equivalente mensal (como fator negativo)
    monthly_fee_rate = (1.0 - management_fee) ** (1.0 / 12.0) - 1.0  # valor negativo

    months_total = total_years * 12
    year = 1
    month_in_year = 1

    # Valores anuais agregados
    year_start_balance = portfolio
    year_contrib = 0.0
    year_withdraw_gross = 0.0
    year_withdraw_net = 0.0
    year_growth_factor = 1.0

    # Definir contribuição mensal para o ano 1
    increment_periods = (year - 1) // contribution_step_up_interval
    adjusted_monthly_contribution = initial_monthly_contribution + (contribution_step_up_amount * increment_periods)
    if max_monthly_contribution is not None:
        adjusted_monthly_contribution = min(adjusted_monthly_contribution, max_monthly_contribution)
    adjusted_monthly_contribution *= (1 + contribution_growth_rate) ** (year - 1)
    monthly_contribution = adjusted_monthly_contribution * (contribution_multiplier / 12.0)

    for m in range(1, months_total + 1):
        # Transição para retirada quando atingir target (verificado mensalmente)
        if phase == "Acumulação" and portfolio >= target_portfolio:
            phase = "Retirada"
            withdrawal_start_year = year if withdrawal_start_year is None else withdrawal_start_year
            current_withdrawal_net = withdrawal_base

        # Contribuições mensais
        this_contribution = monthly_contribution if (phase == "Acumulação" or continue_contributions_during_withdrawal) else 0.0
        if this_contribution > 0:
            portfolio += this_contribution
            total_contributions += this_contribution
            year_contrib += this_contribution

        # Retirada apenas uma vez por ano (no 1º mês do ano civil)
        if phase == "Retirada" and month_in_year == 1:
            if portfolio >= min_threshold:
                if withdrawal_strategy == 1:
                    desired_net = current_withdrawal_net * (2.0 if portfolio >= upper_threshold else 1.0)
                else:
                    desired_net = 0.04 * portfolio

                capital_ratio = min(1.0, total_contributions / portfolio) if portfolio > 0 else 1.0
                gross_withdrawal = desired_net / (1 - tax_rate_withdrawal * (1 - capital_ratio))
                capital_withdrawn = gross_withdrawal * capital_ratio
                gain_withdrawn = gross_withdrawal - capital_withdrawn
                tax_paid = gain_withdrawn * tax_rate_withdrawal
                net_withdrawal = gross_withdrawal - tax_paid

                portfolio -= gross_withdrawal
                total_withdrawn += net_withdrawal
                year_withdraw_gross += gross_withdrawal
                year_withdraw_net += net_withdrawal

                if withdrawal_strategy == 1:
                    current_withdrawal_net *= (1 + withdrawal_growth_rate)
            else:
                # Sem retirada este ano porque ficou abaixo do mínimo
                pass

        # Retornos mensais
        if mode == 1:
            if returns_input_frequency == "monthly":
                monthly_return = np.random.normal(loc=mean_return, scale=std_return)
            else:  # annual input -> converter para mensal e sortear em base mensal
                monthly_mean = annual_to_monthly_rate(mean_return)
                monthly_std = std_return / np.sqrt(12.0)
                monthly_return = np.random.normal(loc=monthly_mean, scale=monthly_std)
        else:
            annual_r = sp500_returns[(year - 1) % len(sp500_returns)] / 100.0
            monthly_return = annual_to_monthly_rate(annual_r)

        # Aplicar comissão mensal como fator
        monthly_effective_factor = (1.0 + monthly_return) * (1.0 + monthly_fee_rate)
        portfolio *= monthly_effective_factor
        year_growth_factor *= monthly_effective_factor

        # Fecho do ano: criar linha agregada
        if month_in_year == 12:
            data = {}
            data["Ano"] = year
            data["Fase"] = phase
            data["Saldo inicio (€)"] = round(year_start_balance, 2)
            data["Contribuição (€)"] = round(year_contrib, 2)
            data["Retirada (€)"] = round(year_withdraw_gross, 2)
            data["Retirada líquida (€)"] = round(year_withdraw_net, 2)
            effective_annual_growth = year_growth_factor - 1.0
            data["Crescimento (%)"] = f"{format_number_pt(effective_annual_growth * 100, 2)} %"
            data["Saldo final (€)"] = round(portfolio, 2)
            results.append(data)

            # Preparar próximo ano
            year += 1
            month_in_year = 0
            year_start_balance = portfolio
            year_contrib = 0.0
            year_withdraw_gross = 0.0
            year_withdraw_net = 0.0
            year_growth_factor = 1.0

            # Atualizar contribuição mensal do novo ano
            increment_periods = (year - 1) // contribution_step_up_interval
            adjusted_monthly_contribution = initial_monthly_contribution + (contribution_step_up_amount * increment_periods)
            if max_monthly_contribution is not None:
                adjusted_monthly_contribution = min(adjusted_monthly_contribution, max_monthly_contribution)
            adjusted_monthly_contribution *= (1 + contribution_growth_rate) ** (year - 1)
            monthly_contribution = adjusted_monthly_contribution * (contribution_multiplier / 12.0)

        month_in_year += 1

    df = pd.DataFrame(results)

    # Exibir floats com 2 casas, milhar com "." e decimal com ","
    pd.options.display.float_format = lambda x: format_number_pt(x, 2)

    return df, withdrawal_start_year, round(total_withdrawn, 2)


# ============================
# Interface interativa
# ============================

print("""
Escolha o tipo de simulação:
1 - Retornos personalizados (média em %/desvio)
2 - Histórico real do S&P500
""")
mode = int(input("Opção: "))

print("""
Escolha a estratégia de retirada:
1 - Valor fixo
2 - 4% Anual (líquido)
""")
withdrawal_strategy = int(input("Opção: "))

total_years = int(input("Quantos anos quer simular? "))
initial_portfolio = float(input("Capital inicial (€): "))
initial_monthly_contribution = float(input("Contribuição mensal inicial (14/ano) (€): "))
contribution_growth_rate = float(input("Crescimento anual das contribuições (ex: 0.02 para 2%): "))
target_portfolio = float(input("Target para começar a retirar dinheiro (€): "))
min_threshold = float(input("Limite mínimo para poder retirar (serve para proteger o capital no caso de queda) (€): "))

# Inputs específicos para a estratégia de valor fixo
if withdrawal_strategy == 1:
    upper_threshold = float(input("Valor para dobrar retiradas (serve para aproveitar ao máximo o crescimento do portfolio) (€): "))
    withdrawal_base = float(input("Valor líquido anual inicial para retirar (€): "))
else:
    upper_threshold = 0.0
    withdrawal_base = 0.0

tax_rate_withdrawal = float(input("Taxa de imposto sobre mais-valias (ex: 0.198 para 19.8%): "))

contribution_step_up_interval = int(input("De quanto em quanto tempo aumentar contribuição anual (anos): "))
contribution_step_up_amount = float(input("Aumento do valor mensal (€): "))
max_monthly_contribution = float(input("Limite máximo da contribuição mensal (€): "))

if mode == 1:
    print("""
Pretende inserir retornos ANUAIS ou MENSAIS?
1 - Anuais (ex: média 0.07 = 7% ao ano)
2 - Mensais (ex: média 0.006 = 0.6% ao mês)
""")
    ret_freq_opt = int(input("Opção: "))
    if ret_freq_opt == 2:
        returns_input_frequency = "monthly"
        mean_return = float(input("Média de retorno MENSAL esperada (ex: 0.006 para 0.6%): "))
        std_return = float(input("Desvio padrão do retorno MENSAL (ex: 0.03 para 3%): "))
    else:
        returns_input_frequency = "annual"
        mean_return = float(input("Média de retorno ANUAL esperada (ex: 0.07 para 7%): "))
        std_return = float(input("Desvio padrão do retorno ANUAL (ex: 0.15 para 15%): "))
else:
    mean_return, std_return = 0, 0
    returns_input_frequency = "annual"

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
    continue_contributions_during_withdrawal=False,  # sempre não
    contribution_step_up_interval=contribution_step_up_interval,
    contribution_step_up_amount=contribution_step_up_amount,
    max_monthly_contribution=max_monthly_contribution,
    withdrawal_strategy=withdrawal_strategy,
    returns_input_frequency=returns_input_frequency
)

print("\n================ RESULTADOS ================\n")
print("Fase de retirada inicia no ano:", start_withdrawal)
print(df_results.to_string(index=False))
print(f"\nTotal retirado ao longo dos anos (valor líquido): {format_number_pt(total_withdrawn, 2)} €")
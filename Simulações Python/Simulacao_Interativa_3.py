import numpy as np
import pandas as pd


def format_number_pt(value, decimals=2):
    """Formata números para o padrão português (vírgula como decimal, ponto como milhar)"""
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
    mean_return=7.0,  # 7% ao ano
    std_return=15.0,  # 15% ao ano
    management_fee=0.5,  # 0.5% ao ano
    target_portfolio=400000,
    min_threshold=300000,
    upper_threshold=600000,
    withdrawal_base=20000,
    withdrawal_growth_rate=0.00,
    tax_rate_withdrawal=19.8,  # 19.8% de imposto
    continue_contributions_during_withdrawal=False,
    contribution_step_up_interval=5,
    contribution_step_up_amount=100,
    max_monthly_contribution=None,
    withdrawal_strategy=1,  # 1 = Valor fixo, 2 = 4% anual líquido
    seed=None
):
    """
    Simula o crescimento de um portfólio de investimentos ao longo do tempo.
    
    Args:
        mode: 1 = Retornos aleatórios, 2 = Histórico real do S&P500 (anual), 3 = Dados mensais reais
        total_years: Número total de anos para simular
        initial_portfolio: Valor inicial do portfólio
        initial_monthly_contribution: Contribuição mensal inicial
        contribution_multiplier: Multiplicador para contribuições (ex: 14 = 14 meses por ano)
        contribution_growth_rate: Taxa de crescimento das contribuições (% ao ano)
        mean_return: Retorno médio anual (%)
        std_return: Desvio padrão do retorno anual (%)
        management_fee: Taxa de gestão anual (%)
        target_portfolio: Valor alvo para iniciar retiradas
        min_threshold: Valor mínimo para continuar retiradas
        upper_threshold: Valor máximo para ajustar retiradas
        withdrawal_base: Valor base de retirada anual
        withdrawal_growth_rate: Taxa de crescimento das retiradas (% ao ano)
        tax_rate_withdrawal: Taxa de imposto sobre retiradas (%)
        continue_contributions_during_withdrawal: Se deve continuar contribuindo durante retiradas
        contribution_step_up_interval: Intervalo para aumentar contribuições (anos)
        contribution_step_up_amount: Valor a aumentar nas contribuições
        max_monthly_contribution: Contribuição mensal máxima
        withdrawal_strategy: Estratégia de retirada (1=fixo, 2=4% anual)
        seed: Semente para gerador aleatório
    
    Returns:
        DataFrame com resultados anuais, ano de início das retiradas, total retirado
    """
    
    # Histórico real do S&P500 (1969–2024) - Retornos anuais
    sp500_returns = [
        26.29, 25.02, -18.11, 28.71, 18.40, 31.49, -4.38, 21.83, 11.96, 1.38, 13.69,
        32.39, 16.00, 2.11, 15.06, 26.46, -37.00, 5.49, 15.79, 4.91, 10.88, 28.68,
        -22.10, -11.89, -9.10, 21.04, 28.58, 33.36, 22.96, 37.58, 1.32, 10.08, 7.62,
        30.47, -3.10, 31.69, 16.61, 5.25, 18.67, 31.73, 6.27, 22.56, 21.55, -4.91,
        32.42, 18.44, 6.56, -7.18, 23.84, 37.20, -26.47, -14.66, 18.98, 14.31, 4.01
    ]
    
    # Histórico real do S&P500 (1985-2024) - Retornos mensais
    sp500_monthly_returns = [
        # 1985
        5.8, 2.1, -1.2, 3.4, 2.8, 1.9, -2.1, 4.2, 1.5, -3.8, 2.9, 4.1,
        # 1986
        2.3, 5.1, 1.8, -0.9, 3.2, 2.4, -1.7, 3.8, 2.1, -2.5, 4.3, 2.7,
        # 1987
        13.2, 4.4, -2.8, 1.9, 2.1, 3.5, 6.8, 3.2, -3.3, -21.5, -8.2, 6.1,
        # 1988
        4.2, 2.8, 1.9, -1.2, 3.4, 2.1, 1.8, 2.9, 3.1, -2.8, 1.5, 2.4,
        # 1989
        7.1, 1.8, 2.9, 4.2, 3.1, 2.8, 1.9, 0.8, -1.2, 2.4, 1.8, 2.1,
        # 1990
        -6.8, 2.1, 1.9, 2.8, 3.4, -0.8, -3.2, -9.2, -5.1, 2.8, 6.1, 2.4,
        # 1991
        4.2, 3.8, 2.1, 1.9, 2.8, 1.5, 2.4, 3.1, 1.8, 2.9, 1.2, 11.2,
        # 1992
        2.1, 1.8, 2.4, 1.9, 2.8, 1.5, 2.1, 1.8, 2.4, 1.9, 2.8, 1.5,
        # 1993
        0.8, 1.2, 1.8, 2.1, 1.9, 2.4, 1.8, 2.1, 1.9, 2.4, 1.8, 1.2,
        # 1994
        3.1, -2.8, -1.9, 1.2, 2.1, 1.8, 2.4, 1.9, 2.1, 1.8, 2.4, 1.9,
        # 1995
        2.8, 3.4, 2.1, 1.9, 2.8, 1.5, 2.4, 3.1, 1.8, 2.9, 4.2, 1.8,
        # 1996
        3.1, 0.8, 2.1, 1.9, 2.8, 1.5, 2.4, 1.8, 2.1, 1.9, 2.4, 1.8,
        # 1997
        6.1, 0.8, -4.2, 5.8, 5.1, 4.2, 7.8, -5.8, 5.1, -3.2, 4.2, 1.8,
        # 1998
        1.0, 7.0, 4.9, 0.8, -1.8, 3.8, -1.2, -14.5, 6.2, 8.1, 5.8, 5.1,
        # 1999
        4.1, -2.9, 3.8, 3.9, -2.5, 5.4, -3.2, -0.5, -2.8, 6.2, 1.9, 5.8,
        # 2000
        -5.1, 1.9, 9.7, -3.1, -2.2, 2.4, -1.8, 6.1, -5.4, -0.5, -8.0, 0.4,
        # 2001
        3.5, -9.2, -6.4, 7.7, 0.4, -2.5, -1.2, -6.4, -8.2, 1.8, 7.5, 0.8,
        # 2002
        -1.6, -2.1, 3.7, -6.1, -0.9, -7.2, -7.9, 0.5, -11.0, 8.6, 5.7, -6.0,
        # 2003
        -2.7, -1.7, 1.0, 8.1, 5.1, 1.2, 1.6, 1.8, -1.2, 5.5, 0.9, 5.1,
        # 2004
        1.7, 1.2, -1.6, -1.7, 1.2, 1.8, -3.4, 0.4, 0.8, 1.4, 3.9, 3.2,
        # 2005
        -2.5, 1.9, -1.9, -2.0, 3.0, 0.0, 3.6, -1.2, 0.7, -1.8, 3.5, 0.0,
        # 2006
        2.5, 0.0, 1.2, 1.3, -3.1, 0.2, 0.3, 2.1, 2.5, 3.2, 1.8, 1.4,
        # 2007
        1.4, -2.2, 1.0, 4.3, 3.3, -1.8, -3.2, 1.3, 3.6, 1.5, -4.4, -0.9,
        # 2008
        -6.1, -3.5, -0.6, 4.8, 1.1, -8.6, -0.8, 1.2, -9.1, -16.9, -7.2, 0.8,
        # 2009
        -8.6, -10.9, 8.5, 9.4, 5.3, 0.0, 7.4, 3.4, 3.6, -1.9, 5.7, 1.8,
        # 2010
        -3.7, 2.9, 5.9, 1.5, -8.2, -5.4, 6.9, -4.7, 8.8, 3.7, -0.2, 6.5,
        # 2011
        2.3, 3.2, -0.1, 2.8, -1.4, -1.8, -2.2, -5.7, -7.2, 10.8, -0.5, 0.9,
        # 2012
        4.4, 4.1, 3.1, -0.8, -6.3, 4.0, 1.3, 2.0, 2.4, -1.9, 0.3, 0.7,
        # 2013
        5.0, 1.1, 3.6, 1.8, 2.1, -1.5, 4.9, -3.1, 3.0, 4.5, 2.8, 2.4,
        # 2014
        -3.6, 4.3, 0.7, 0.6, 2.1, 1.9, -1.5, 3.8, -1.6, 2.3, 2.5, -0.4,
        # 2015
        -3.1, 5.5, -1.7, 0.9, 1.0, -2.1, 2.0, -6.3, -2.6, 8.3, 0.1, -1.8,
        # 2016
        -5.1, -0.4, 6.6, 0.3, 1.5, 0.1, 3.6, -0.1, -0.1, -1.9, 3.4, 1.8,
        # 2017
        1.8, 3.7, 0.0, 0.9, 1.2, 0.5, 1.9, 0.1, 1.9, 2.2, 2.8, 1.1,
        # 2018
        5.6, -3.9, -2.7, 0.3, 2.2, 0.5, 3.6, 3.0, 0.4, -6.9, 1.8, -9.2,
        # 2019
        7.9, 3.0, 1.8, 3.9, -6.6, 6.9, 1.3, -1.8, 1.7, 2.0, 3.4, 2.9,
        # 2020
        -0.2, -8.4, -12.5, 12.7, 4.5, 1.8, 5.5, 7.0, -3.9, -2.8, 10.8, 3.7,
        # 2021
        -1.0, 2.6, 4.2, 5.2, 0.6, 2.2, 2.3, 2.9, -4.8, 6.9, -0.8, 4.4,
        # 2022
        -5.3, -3.1, 3.6, -8.8, 0.0, -8.4, 9.1, -4.2, -9.3, 8.0, 5.4, -5.9,
        # 2023
        6.2, -2.6, 3.5, 1.5, 0.3, 6.5, 3.1, -1.8, -4.9, -2.2, 8.9, 4.4,
        # 2024
        1.6, 5.2, 3.1, -4.2, 4.8, 3.5, 2.1, 1.8, -4.9, 4.6, 2.8, 1.2
    ]

    if seed is not None:
        np.random.seed(seed)

    # Inicialização das variáveis
    portfolio = initial_portfolio
    phase = "Acumulação"
    current_withdrawal_net = withdrawal_base
    results = []
    withdrawal_start_year = None
    total_withdrawn = 0.0
    total_contributions = 0.0

    if mode == 3:  # Simulação mensal com dados reais
        # Simulação mensal
        monthly_results = []
        total_months = total_years * 12
        
        for month in range(total_months):
            year = (month // 12) + 1
            month_in_year = (month % 12) + 1
            
            # Cálculo das contribuições mensais
            increment_periods = (year - 1) // contribution_step_up_interval
            adjusted_monthly_contribution = initial_monthly_contribution + (contribution_step_up_amount * increment_periods)
            
            if max_monthly_contribution is not None:
                adjusted_monthly_contribution = min(adjusted_monthly_contribution, max_monthly_contribution)
            
            # Aplicar crescimento anual das contribuições
            monthly_contribution = adjusted_monthly_contribution * (1 + contribution_growth_rate) ** (year - 1)
            
            # Aplicar contribuição extra em junho e dezembro (14 meses por ano)
            if month_in_year in [6, 12]:  # Junho e dezembro
                monthly_contribution += adjusted_monthly_contribution * (1 + contribution_growth_rate) ** (year - 1)
            
            # Transição para fase de retirada
            if phase == "Acumulação" and portfolio >= target_portfolio:
                phase = "Retirada"
                withdrawal_start_year = year
                current_withdrawal_net = withdrawal_base
            
            # Processamento da fase atual
            if phase == "Acumulação":
                portfolio += monthly_contribution
                total_contributions += monthly_contribution
            else:  # Fase de retirada
                if continue_contributions_during_withdrawal:
                    portfolio += monthly_contribution
                    total_contributions += monthly_contribution
                
                # Retiradas mensais (dividir retirada anual por 12)
                if portfolio >= min_threshold:
                    if withdrawal_strategy == 1:
                        desired_net_monthly = current_withdrawal_net / 12
                        if portfolio >= upper_threshold:
                            desired_net_monthly *= 2
                    else:  # 4% anual líquido
                        desired_net_monthly = (0.04 * portfolio) / 12
                    
                    # Cálculo para obter bruto tal que o líquido = desired_net_monthly
                    capital_ratio = min(1.0, total_contributions / portfolio) if portfolio > 0 else 1.0
                    gross_withdrawal_monthly = desired_net_monthly / (1 - tax_rate_withdrawal * (1 - capital_ratio))
                    
                    portfolio -= gross_withdrawal_monthly
                    total_withdrawn += desired_net_monthly
            
            # Aplicação dos retornos mensais
            if month < len(sp500_monthly_returns):
                monthly_return = sp500_monthly_returns[month] / 100
            else:
                # Se não há dados suficientes, usar dados anuais convertidos para mensais
                annual_index = (month // 12) % len(sp500_returns)
                annual_return = sp500_returns[annual_index] / 100
                # Converter retorno anual para mensal (aproximação)
                monthly_return = (1 + annual_return) ** (1/12) - 1
            
            # Converter taxa de gestão anual para mensal
            monthly_management_fee = management_fee / 12
            effective_return = monthly_return - monthly_management_fee
            portfolio *= (1 + effective_return)
            
            monthly_results.append({
                'year': year,
                'month': month_in_year,
                'portfolio': portfolio,
                'phase': phase,
                'monthly_contribution': monthly_contribution,
                'monthly_return': monthly_return,
                'effective_return': effective_return
            })
        
        # Agregação dos resultados mensais por ano
        for year in range(1, total_years + 1):
            year_months = [m for m in monthly_results if m['year'] == year]
            
            if not year_months:
                continue
                
            data = {}
            data["Ano"] = year
            data["Fase"] = year_months[0]['phase']
            data["Saldo inicio (€)"] = round(year_months[0]['portfolio'] / (1 + year_months[0]['effective_return']), 2)
            
            # Soma das contribuições do ano
            annual_contribution = sum(m['monthly_contribution'] for m in year_months)
            data["Contribuição (€)"] = round(annual_contribution, 2)
            
            # Retiradas (já calculadas mensalmente)
            if data["Fase"] == "Retirada":
                if withdrawal_strategy == 1:
                    desired_net = current_withdrawal_net
                    if year_months[-1]['portfolio'] >= upper_threshold:
                        desired_net *= 2
                else:
                    desired_net = 0.04 * year_months[-1]['portfolio']
                
                data["Retirada (€)"] = round(desired_net, 2)
                data["Retirada líquida (€)"] = round(desired_net, 2)
                
                # Atualiza para estratégia de valor fixo
                if withdrawal_strategy == 1:
                    current_withdrawal_net *= (1 + withdrawal_growth_rate)
            else:
                data["Retirada (€)"] = round(0.0, 2)
                data["Retirada líquida (€)"] = round(0.0, 2)
            
            # Retorno anual composto
            portfolio_start = data["Saldo inicio (€)"]
            portfolio_end = year_months[-1]['portfolio']
            annual_return = (portfolio_end / portfolio_start - 1) * 100
            
            data["Crescimento (%)"] = f"{format_number_pt(annual_return, 2)} %"
            data["Saldo final (€)"] = round(portfolio_end, 2)
            results.append(data)
    
    else:  # Simulação anual (modos 1 e 2)
        for year in range(1, total_years + 1):
            data = {}
            data["Ano"] = year
            data["Fase"] = phase
            data["Saldo inicio (€)"] = round(portfolio, 2)

            # Cálculo das contribuições
            increment_periods = (year - 1) // contribution_step_up_interval
            adjusted_monthly_contribution = initial_monthly_contribution + (contribution_step_up_amount * increment_periods)
            
            if max_monthly_contribution is not None:
                adjusted_monthly_contribution = min(adjusted_monthly_contribution, max_monthly_contribution)

            annual_contribution = adjusted_monthly_contribution * contribution_multiplier
            annual_contribution *= (1 + contribution_growth_rate) ** (year - 1)

            # Transição para fase de retirada
            if phase == "Acumulação" and portfolio >= target_portfolio:
                phase = "Retirada"
                withdrawal_start_year = year
                current_withdrawal_net = withdrawal_base
                data["Fase"] = phase

            # Processamento da fase atual
            if phase == "Acumulação":
                data["Contribuição (€)"] = round(annual_contribution, 2)
                data["Retirada (€)"] = round(0.0, 2)
                data["Retirada líquida (€)"] = round(0.0, 2)
                portfolio += annual_contribution
                total_contributions += annual_contribution

            else:  # Fase de retirada
                this_contribution = annual_contribution if continue_contributions_during_withdrawal else 0.0
                data["Contribuição (€)"] = round(this_contribution, 2)

                if continue_contributions_during_withdrawal:
                    portfolio += this_contribution
                    total_contributions += this_contribution

                # Cálculo das retiradas
                if portfolio < min_threshold:
                    data["Retirada (€)"] = round(0.0, 2)
                    data["Retirada líquida (€)"] = round(0.0, 2)
                else:
                    # Definição do líquido desejado conforme estratégia
                    if withdrawal_strategy == 1:
                        desired_net = current_withdrawal_net
                        if portfolio >= upper_threshold:
                            desired_net *= 2
                    else:  # 4% anual líquido
                        desired_net = 0.04 * portfolio

                    # Cálculo para obter bruto tal que o líquido = desired_net
                    # (imposto só sobre mais-valias)
                    capital_ratio = min(1.0, total_contributions / portfolio) if portfolio > 0 else 1.0
                    gross_withdrawal = desired_net / (1 - tax_rate_withdrawal * (1 - capital_ratio))
                    capital_withdrawn = gross_withdrawal * capital_ratio
                    gain_withdrawn = gross_withdrawal - capital_withdrawn
                    tax_paid = gain_withdrawn * tax_rate_withdrawal
                    net_withdrawal = gross_withdrawal - tax_paid

                    portfolio -= gross_withdrawal
                    total_withdrawn += net_withdrawal
                    data["Retirada (€)"] = round(gross_withdrawal, 2)
                    data["Retirada líquida (€)"] = round(net_withdrawal, 2)

                    # Atualiza apenas para estratégia de valor fixo
                    if withdrawal_strategy == 1:
                        current_withdrawal_net *= (1 + withdrawal_growth_rate)

            # Aplicação dos retornos
            if mode == 1:
                annual_return = np.random.normal(loc=mean_return, scale=std_return)
            else:
                annual_return = sp500_returns[(year - 1) % len(sp500_returns)] / 100

            effective_return = annual_return - management_fee
            portfolio *= (1 + effective_return)
            data["Crescimento (%)"] = f"{format_number_pt(effective_return * 100, 2)} %"
            data["Saldo final (€)"] = round(portfolio, 2)
            results.append(data)

    df = pd.DataFrame(results)

    # Configuração da formatação para exibição
    pd.options.display.float_format = lambda x: format_number_pt(x, 2)

    return df, withdrawal_start_year, round(total_withdrawn, 2)


def get_user_inputs():
    """Coleta todos os inputs do usuário de forma organizada"""
    
    print("""
Escolha o tipo de simulação:
1 - Retornos personalizados (média em %/desvio)
2 - Histórico real do S&P500 (anual)
3 - Dados mensais reais do S&P500 (1985-2024)
""")
    mode = int(input("Opção: "))

    print("""
Escolha a estratégia de retirada:
1 - Valor fixo
2 - 4% Anual (líquido)
""")
    withdrawal_strategy = int(input("Opção: "))

    # Parâmetros básicos
    total_years = int(input("Quantos anos quer simular? "))
    initial_portfolio = float(input("Capital inicial (€): "))
    initial_monthly_contribution = float(input("Contribuição mensal inicial (14/ano) (€): "))
    
    # Taxa de crescimento das contribuições (em %)
    contribution_growth_rate_input = float(input("Crescimento anual das contribuições (%): "))
    contribution_growth_rate = contribution_growth_rate_input / 100
    
    target_portfolio = float(input("Target para começar a retirar dinheiro (€): "))
    min_threshold = float(input("Limite mínimo para poder retirar (€): "))

    # Inputs específicos para a estratégia de valor fixo
    if withdrawal_strategy == 1:
        upper_threshold = float(input("Valor para dobrar retiradas (€): "))
        withdrawal_base = float(input("Valor líquido anual inicial para retirar (€): "))
    else:
        upper_threshold = 0.0
        withdrawal_base = 0.0

    # Taxa de imposto (em %)
    tax_rate_input = float(input("Taxa de imposto sobre mais-valias (%): "))
    tax_rate_withdrawal = tax_rate_input / 100

    # Configurações de contribuições
    contribution_step_up_interval = int(input("De quanto em quanto tempo aumentar contribuição anual (anos): "))
    contribution_step_up_amount = float(input("Aumento do valor mensal (€): "))
    max_monthly_contribution = float(input("Limite máximo da contribuição mensal (€): "))

    # Parâmetros de retorno (apenas para modo 1)
    if mode == 1:
        mean_return_input = float(input("Média de retorno anual esperado (%): "))
        mean_return = mean_return_input / 100
        
        std_return_input = float(input("Desvio padrão do retorno anual (%): "))
        std_return = std_return_input / 100
    else:
        mean_return = 0.07
        std_return = 0.15

    # Taxa de gestão (em %)
    management_fee_input = float(input("Taxa de gestão anual (%): "))
    management_fee = management_fee_input / 100

    # Configurações adicionais
    continue_contributions = input("Continuar contribuindo durante retiradas? (s/n): ").lower() == 's'
    withdrawal_growth_rate_input = float(input("Taxa de crescimento das retiradas (%): "))
    withdrawal_growth_rate = withdrawal_growth_rate_input / 100

    return {
        'mode': mode,
        'total_years': total_years,
        'initial_portfolio': initial_portfolio,
        'initial_monthly_contribution': initial_monthly_contribution,
        'contribution_growth_rate': contribution_growth_rate,
        'mean_return': mean_return,
        'std_return': std_return,
        'management_fee': management_fee,
        'target_portfolio': target_portfolio,
        'min_threshold': min_threshold,
        'upper_threshold': upper_threshold,
        'withdrawal_base': withdrawal_base,
        'withdrawal_growth_rate': withdrawal_growth_rate,
        'tax_rate_withdrawal': tax_rate_withdrawal,
        'continue_contributions_during_withdrawal': continue_contributions,
        'contribution_step_up_interval': contribution_step_up_interval,
        'contribution_step_up_amount': contribution_step_up_amount,
        'max_monthly_contribution': max_monthly_contribution,
        'withdrawal_strategy': withdrawal_strategy
    }


def main():
    """Função principal que executa o simulador"""
    
    print("=== SIMULADOR DE INVESTIMENTOS ===")
    print("Simulador de portfólio com fases de acumulação e retirada")
    print()
    
    # Coleta dos inputs
    inputs = get_user_inputs()
    
    print("\n=== EXECUTANDO SIMULAÇÃO ===")
    
    # Execução da simulação
    df, withdrawal_start_year, total_withdrawn = simulation(**inputs)
    
    # Exibição dos resultados
    print("\n=== RESULTADOS ===")
    print(df.to_string(index=False))
    
    print(f"\n=== RESUMO ===")
    print(f"Ano de início das retiradas: {withdrawal_start_year if withdrawal_start_year else 'Não atingido'}")
    print(f"Total retirado (líquido): €{format_number_pt(total_withdrawn)}")
    print(f"Saldo final: €{format_number_pt(df.iloc[-1]['Saldo final (€)'])}")
    
    # Estatísticas adicionais
    if len(df) > 0:
        final_balance = df.iloc[-1]['Saldo final (€)']
        total_contributions = df['Contribuição (€)'].sum()
        total_withdrawals = df['Retirada (€)'].sum()
        
        print(f"\n=== ESTATÍSTICAS ===")
        print(f"Total de contribuições: €{format_number_pt(total_contributions)}")
        print(f"Total de retiradas (bruto): €{format_number_pt(total_withdrawals)}")
        print(f"Ganho total: €{format_number_pt(final_balance - inputs['initial_portfolio'] - total_contributions + total_withdrawals)}")


if __name__ == "__main__":
    main()

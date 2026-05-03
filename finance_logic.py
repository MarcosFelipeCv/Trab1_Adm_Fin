import yfinance as yf
import pandas as pd

    
def pegar_valor(df, nomes_possiveis):
    """Busca em uma lista de chaves possíveis para evitar erros entre mercados."""
    if isinstance(nomes_possiveis, str):
        nomes_possiveis = [nomes_possiveis]
    try:
        for nome in nomes_possiveis:
            if nome in df.index:
                return df.loc[nome].iloc[0]
        return None
    except Exception:
        return None


def dividir(numerador, denominador):
    """
    Evita erro de divisão por zero ou valores inexistentes.
    """
    try:
        if numerador is None or denominador is None or denominador == 0:
            return None
        return numerador / denominador
    except Exception:
        return None


def formatar_percentual(valor):
    if valor is None:
        return None
    try:
        return f"{valor:.2%}"
    except Exception:
        return None


def formatar_numero(valor):
    if valor is None:
        return None
    try:
        return round(valor, 2)
    except Exception:
        return None
    
def formatar_grande_numero(valor):
    """Converte números gigantes em formato legível (Mi, Bi, Tri)."""
    if valor is None:
        return None
    try:
        abs_valor = abs(valor)
        prefixo = "R$ "
        if abs_valor >= 1_000_000_000_000:
            return f"{prefixo}{valor / 1_000_000_000_000:.2f} Tri"
        elif abs_valor >= 1_000_000_000:
            return f"{prefixo}{valor / 1_000_000_000:.2f} Bi"
        elif abs_valor >= 1_000_000:
            return f"{prefixo}{valor / 1_000_000:.2f} Mi"
        else:
            return f"{prefixo}{valor:,.2f}"
    except Exception:
        return valor


def get_financial_indexes(ticker_symbol):
    try:
        empresa = yf.Ticker(ticker_symbol)

        dre = empresa.financials
        balanco = empresa.balance_sheet
        fluxo_caixa = empresa.cashflow
        info = empresa.info

        if dre is None or balanco is None or dre.empty or balanco.empty:
            return None

        # =========================
        # DRE
        # =========================
        lucro_liquido = pegar_valor(dre, "Net Income")
        receita_total = pegar_valor(dre, "Total Revenue")
        lucro_bruto = pegar_valor(dre, "Gross Profit")
        ebit = pegar_valor(dre, "EBIT")
        ebitda = pegar_valor(dre, "EBITDA")

        # =========================
        # BALANÇO PATRIMONIAL
        # =========================
        ativo_total = pegar_valor(balanco, "Total Assets")
        patrimonio_liquido = pegar_valor(balanco, "Stockholders Equity")
        ativo_circulante = pegar_valor(balanco, ["Current Assets", "Total Current Assets"])
        passivo_circulante = pegar_valor(balanco, ["Current Liabilities", "Total Current Liabilities"])
        passivo_total = pegar_valor(balanco, "Total Liabilities Net Minority Interest")
        divida_total = pegar_valor(balanco, "Total Debt")
        caixa = pegar_valor(balanco, "Cash And Cash Equivalents")
        estoques = pegar_valor(balanco, "Inventory")

        # =========================
        # FLUXO DE CAIXA
        # =========================
        fluxo_operacional = pegar_valor(fluxo_caixa, "Operating Cash Flow")
        capex = pegar_valor(fluxo_caixa, "Capital Expenditure")

        # =========================
        # LIQUIDEZ
        # =========================
        liq_corrente = dividir(ativo_circulante, passivo_circulante)

        if ativo_circulante is not None and estoques is not None:
            liq_seca = dividir(ativo_circulante - estoques, passivo_circulante)
        else:
            liq_seca = None

        if ativo_circulante is not None and passivo_circulante is not None:
            capital_giro = ativo_circulante - passivo_circulante
        else:
            capital_giro = None

        # =========================
        # RENTABILIDADE
        # =========================
        margem_bruta = dividir(lucro_bruto, receita_total)
        margem_operacional = dividir(ebit, receita_total)
        margem_liquida = dividir(lucro_liquido, receita_total)

        roa = dividir(lucro_liquido, ativo_total)
        roe = dividir(lucro_liquido, patrimonio_liquido)

        # =========================
        # ANÁLISE DUPONT
        # ROE = Margem Líquida x Giro do Ativo x Multiplicador do PL
        # =========================
        giro_ativo = dividir(receita_total, ativo_total)
        multiplicador_pl = dividir(ativo_total, patrimonio_liquido)

        if margem_liquida is not None and giro_ativo is not None and multiplicador_pl is not None:
            roe_dupont = margem_liquida * giro_ativo * multiplicador_pl
        else:
            roe_dupont = None

        # =========================
        # ENDIVIDAMENTO
        # =========================
        endividamento_geral = dividir(passivo_total, ativo_total)
        divida_patrimonio = dividir(divida_total, patrimonio_liquido)

        if divida_total is not None and caixa is not None:
            divida_liquida = divida_total - caixa
        else:
            divida_liquida = None

        divida_liquida_patrimonio = dividir(divida_liquida, patrimonio_liquido)

        # =========================
        # FLUXO DE CAIXA
        # No Yahoo, CapEx costuma vir negativo.
        # Por isso, FCF = fluxo_operacional + capex
        # =========================
        if fluxo_operacional is not None and capex is not None:
            fluxo_caixa_livre = fluxo_operacional + capex
        else:
            fluxo_caixa_livre = None

        margem_fcf = dividir(fluxo_caixa_livre, receita_total)

        # =========================
        # INDICADORES DE MERCADO
        # =========================
        preco_atual = info.get("currentPrice")
        div_rate = info.get("dividendRate")
        valor_mercado = info.get("marketCap")
        lpa = info.get("trailingEps")
        vpa = info.get("bookValue")
        beta = info.get("beta")

        pl = dividir(preco_atual, lpa)
        pvp = dividir(preco_atual, vpa)

        #calculo do Dividend Yield com múltiplas tentativas para garantir precisão e compatibilidade entre mercados
        # 1. Tenta calcular: Dividend Rate / Preço Atual
        dividend_yield = dividir(div_rate, preco_atual)

        # 2. Se não houver 'dividendRate', busca o campo pronto da API
        if dividend_yield is None:
            dividend_yield = info.get("dividendYield") or info.get("trailingAnnualDividendYield")

        # 3. Trava de Segurança: Se o valor vier como 7.96 (em vez de 0.0796), normaliza
        if dividend_yield and dividend_yield > 1.0:
            dividend_yield = dividir(dividend_yield, 100)

        return {
            "ticker": ticker_symbol,
            "nome": info.get("longName", ticker_symbol),
            "setor": info.get("sector", "N/A"),
            "industria": info.get("industry", "N/A"),

            # Liquidez
            "liq_corrente": formatar_numero(liq_corrente),
            "liq_seca": formatar_numero(liq_seca),
            "capital_giro": formatar_grande_numero(capital_giro),

            # Rentabilidade
            "margem_bruta": formatar_percentual(margem_bruta),
            "margem_operacional": formatar_percentual(margem_operacional),
            "margem_liquida": formatar_percentual(margem_liquida),
            "roa": formatar_percentual(roa),
            "roe": formatar_percentual(roe),

            # DuPont
            "giro_ativo": formatar_numero(giro_ativo),
            "multiplicador_pl": formatar_numero(multiplicador_pl),
            "roe_dupont": formatar_percentual(roe_dupont),

            # Endividamento
            "endividamento_geral": formatar_percentual(endividamento_geral),
            "divida_patrimonio": formatar_numero(divida_patrimonio),
            "divida_liquida": formatar_grande_numero(divida_liquida),
            "divida_liquida_patrimonio": formatar_numero(divida_liquida_patrimonio),

            # Fluxo de caixa
            "fluxo_operacional": formatar_grande_numero(fluxo_operacional),
            "capex": formatar_grande_numero(capex),
            "fluxo_caixa_livre": formatar_grande_numero(fluxo_caixa_livre),
            "margem_fcf": formatar_percentual(margem_fcf),

            # Mercado
            "preco_atual": preco_atual,
            "valor_mercado": formatar_grande_numero(valor_mercado),
            "lpa": lpa,
            "vpa": vpa,
            "pl": formatar_numero(pl),
            "pvp": formatar_numero(pvp),
            "dividend_yield": formatar_percentual(dividend_yield),
            "beta": beta,
        }

    except Exception as e:
        print(f"Erro ao processar {ticker_symbol}: {e}")
        return None


def get_financial_analysis(ticker):
    """Compatibilidade: invoca get_financial_indexes."""
    return get_financial_indexes(ticker)

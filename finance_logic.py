import yfinance as yf
import pandas as pd

def get_financial_indexes(ticker_symbol):
    try:
        empresa = yf.Ticker(ticker_symbol)
        
        # Obtendo demonstrativos (último ano disponível)
        dre = empresa.financials
        balanco = empresa.balance_sheet
        
        if dre.empty or balanco.empty:
            return None

        # Extração de valores (iloc[0] pega o ano mais recente)
        # Usamos .get() ou try-except pois nomes de colunas podem variar levemente
        lucro_liquido = dre.loc['Net Income'].iloc[0]
        receita_total = dre.loc['Total Revenue'].iloc[0]
        ativo_total = balanco.loc['Total Assets'].iloc[0]
        patrimonio_liquido = balanco.loc['Stockholders Equity'].iloc[0]
        ativo_circulante = balanco.loc['Current Assets'].iloc[0]
        passivo_circulante = balanco.loc['Current Liabilities'].iloc[0]

        # --- CÁLCULOS (Capítulo 2) ---
        
        # 1. Liquidez
        liq_corrente = ativo_circulante / passivo_circulante
        
        # 2. Análise DuPont (Rentabilidade)
        margem_liquida = lucro_liquido / receita_total
        giro_ativo = receita_total / ativo_total
        multiplicador_pl = ativo_total / patrimonio_liquido
        
        roe = margem_liquida * giro_ativo * multiplicador_pl
        roa = margem_liquida * giro_ativo

        return {
            "nome": empresa.info.get('longName', ticker_symbol),
            "setor": empresa.info.get('sector', 'N/A'),
            "liq_corrente": round(liq_corrente, 2),
            "margem_liquida": f"{margem_liquida:.2%}",
            "giro_ativo": round(giro_ativo, 2),
            "multiplicador_pl": round(multiplicador_pl, 2),
            "roa": f"{roa:.2%}",
            "roe": f"{roe:.2%}"
        }
    except Exception as e:
        print(f"Erro ao processar {ticker_symbol}: {e}")
        return None
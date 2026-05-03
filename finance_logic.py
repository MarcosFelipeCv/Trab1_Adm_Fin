import yfinance as yf
import pandas as pd

def get_financial_analysis(ticker):
    try:
        empresa = yf.Ticker(ticker)
        # Tenta pegar os dados anuais
        dre = empresa.financials
        balanco = empresa.balance_sheet
        info = empresa.info

        if dre.empty or balanco.empty:
            return None

        # Função de ajuda para buscar chaves alternativas (Normalização)
        def safe_fetch(df, keys):
            for k in keys:
                if k in df.index:
                    val = df.loc[k].iloc[0]
                    return val if pd.notnull(val) else 0
            return 0

        # --- CAPTURA DE DADOS ---
        lucro = safe_fetch(dre, ['Net Income', 'Net Income Common Stockholders'])
        receita = safe_fetch(dre, ['Total Revenue', 'Operating Revenue'])
        ativos = safe_fetch(balanco, ['Total Assets'])
        patrimonio = safe_fetch(balanco, ['Stockholders Equity', 'Total Stockholders Equity'])
        
        # --- LÓGICA DE SETOR (BANCOS VS INDÚSTRIA) ---
        setor = info.get('sector', 'N/A')
        is_financial = "Financial" in setor

        if is_financial:
            liq_corrente = "N/A (Bancos não usam Ativo Circulante)"
        else:
            a_circ = safe_fetch(balanco, ['Current Assets', 'Total Current Assets'])
            p_circ = safe_fetch(balanco, ['Current Liabilities', 'Total Current Liabilities'])
            liq_corrente = round(a_circ / p_circ, 2) if p_circ > 0 else 0

        # --- CÁLCULOS DUPONT (CAPÍTULO 2) ---
        margem_liq = lucro / receita if receita > 0 else 0
        giro_ativo = receita / ativos if ativos > 0 else 0
        mult_pl = ativos / patrimonio if patrimonio > 0 else 0
        roe = margem_liq * giro_ativo * mult_pl

        return {
            "nome": info.get('longName', ticker),
            "setor": setor,
            "pais": info.get('country', 'N/A'),
            "moeda": info.get('financialCurrency', 'N/A'),
            "liq_corrente": liq_corrente,
            "margem_liquida": f"{margem_liq:.2%}",
            "giro_ativo": round(giro_ativo, 2),
            "mult_pl": round(mult_pl, 2),
            "roe": f"{roe:.2%}"
        }
    except Exception as e:
        print(f"Erro técnico ao processar {ticker}: {e}")
        return None
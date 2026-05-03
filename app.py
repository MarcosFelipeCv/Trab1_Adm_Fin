from flask import Flask, render_template, request, session, jsonify
from finance_logic import get_financial_analysis
import time
import requests
import re

app = Flask(__name__)
app.secret_key = "ufmg_si_financeira_key"


def normalizar_ticker(ticker):
    ticker = ticker.strip().upper()

    # Se já veio com sufixo ou símbolo especial, mantém.
    # Exemplos: PETR4.SA, MSFT, AAPL, EURUSD=X
    if "." in ticker or "=" in ticker or "-" in ticker:
        return ticker

    # Padrão comum de ações brasileiras:
    # 4 letras + 1 ou 2 números
    # Exemplos: PETR4, VALE3, ITUB4, BBDC4, TAEE11
    if re.match(r"^[A-Z]{4}[0-9]{1,2}$", ticker):
        return ticker + ".SA"

    # Caso contrário, mantém como internacional
    # Exemplos: MSFT, AAPL, NVDA, PTPI
    return ticker


@app.route("/", methods=["GET", "POST"])
def index():
    resultado = None
    erro = None

    if request.method == "POST":
        agora = time.time()
        ultima = session.get("last_req", 0)

        if agora - ultima < 3:
            erro = "Aguarde 3 segundos entre as análises."
            return render_template("index.html", erro=erro)

        session["last_req"] = agora

        ticker_digitado = request.form.get("ticker", "").strip().upper()

        if not ticker_digitado:
            erro = "Digite um ticker válido. Exemplo: ITUB4.SA, PETR4, MSFT ou AAPL"
        else:
            ticker = normalizar_ticker(ticker_digitado)

            resultado = get_financial_analysis(ticker)

            if not resultado:
                erro = (
                    f"Não foi possível obter dados financeiros para {ticker}. "
                    "Verifique se é uma ação válida e se possui demonstrativos financeiros disponíveis no Yahoo Finance."
                )

    return render_template("index.html", resultado=resultado, erro=erro)


@app.route("/search_proxy")
def search_proxy():
    q = request.args.get("q", "").strip()

    if not q or len(q) < 2:
        return jsonify([])

    try:
        url = "https://query1.finance.yahoo.com/v1/finance/search"
        headers = {"User-Agent": "Mozilla/5.0"}
        params = {"q": q}

        r = requests.get(url, headers=headers, params=params, timeout=10)
        r.raise_for_status()

        quotes = r.json().get("quotes", [])

        # Mantém só resultados que parecem ativos negociáveis.
        # Evita moedas, índices e resultados estranhos demais.
        filtrados = []
        for item in quotes:
            symbol = item.get("symbol")
            quote_type = item.get("quoteType")

            if not symbol:
                continue

            if quote_type in ["EQUITY", "ETF"]:
                filtrados.append(item)

        return jsonify(filtrados)

    except Exception as e:
        print(f"Erro no search_proxy: {e}")
        return jsonify([])


if __name__ == "__main__":
    app.run(debug=True)
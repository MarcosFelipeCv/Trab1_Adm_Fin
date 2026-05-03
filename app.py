from flask import Flask, render_template, request, session, jsonify
from finance_logic import get_financial_analysis
import time
import requests

app = Flask(__name__)
app.secret_key = 'ufmg_si_financeira_key'

# Rota Principal
@app.route('/', methods=['GET', 'POST'])
def index():
    resultado = None
    erro = None
    
    if request.method == 'POST':
        # 1. Rate Limit (Trava de 3 segundos)
        agora = time.time()
        ultima = session.get('last_req', 0)
        if agora - ultima < 3:
            return render_template('index.html', erro="Aguarde 3 segundos entre as análises.")
        
        session['last_req'] = agora
        ticker = request.form.get('ticker').strip().upper()
        
        resultado = get_financial_analysis(ticker)
        if not resultado:
            erro = f"Não foi possível obter dados para {ticker}. Verifique o ticker ou tente novamente mais tarde."

    return render_template('index.html', resultado=resultado, erro=erro)

# Proxy de Busca (Para o Autocomplete funcionar sem erro de CORS)
@app.route('/search_proxy')
def search_proxy():
    q = request.args.get('q')
    if not q or len(q) < 2: return jsonify([])
    
    url = f"https://query1.finance.yahoo.com/v1/finance/search?q={q}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    r = requests.get(url, headers=headers)
    return jsonify(r.json().get('quotes', []))

if __name__ == '__main__':
    app.run(debug=True)
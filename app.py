from flask import Flask, render_template, request
from finance_logic import get_financial_indexes

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    resultado = None
    erro = None
    
    if request.method == 'POST':
        ticker = request.form.get('ticker').upper()
        # Garante o sufixo .SA para empresas brasileiras se o usuário esquecer
        if not ticker.endswith('.SA') and len(ticker) <= 6:
            ticker += '.SA'
            
        resultado = get_financial_indexes(ticker)
        if not resultado:
            erro = "Não foi possível encontrar dados para este ticker. Verifique se ele está correto (ex: ITUB4.SA)."

    return render_template('index.html', resultado=resultado, erro=erro)

if __name__ == '__main__':
    app.run(debug=True)
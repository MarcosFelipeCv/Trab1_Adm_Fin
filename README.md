Analisador Financeiro - UFMG
Projeto acadêmico para a disciplina de Administração Financeira (Sistemas de Informação). O sistema extrai dados reais do Yahoo Finance para calcular índices fundamentais do Capítulo 2, como Liquidez, DuPont e Rentabilidade.

Alunos: 
Marcos Felipe Flores Cavalieri - 2020054692
Bianca Gabriela Franco e Silva - 2020092756

 Como Rodar
1. Requisitos
Python instalado em sua máquina.

Conexão ativa com a internet (necessária para que o sistema busque os dados reais das empresas).

2. Instalação
No terminal, dentro da pasta principal do projeto, execute os comandos abaixo para garantir que o instalador de pacotes esteja atualizado e todas as bibliotecas necessárias sejam configuradas:

Comando para atualizar o instalador:
python -m pip install --upgrade pip

Comando para instalar as dependências:
pip install -r requirements.txt

3. Execução
Inicie o servidor local com o comando:
python app.py

4. Acesso
Abra o seu navegador e acesse o seguinte endereço:
http://127.0.0.1:5000

Observações de Uso
Busca Inteligente: Ao começar a digitar o nome de uma empresa, o sistema sugere automaticamente o ticker oficial via autocomplete.

Resiliência Contábil (Bancos): O sistema detecta automaticamente se a empresa é uma instituição financeira e ajusta a exibição dos índices, tratando a ausência da conta de "Ativo Circulante".
s
Normalização de Dados: O código implementa uma lógica para corrigir a heterogeneidade de dados da API, evitando erros de escala em indicadores como o Dividend Yield.

Trava de Segurança: Existe um limite de 3 segundos entre análises consecutivas para evitar sobrecarga e bloqueios temporários na API de dados.

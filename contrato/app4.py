from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'

# Função para conectar ao banco de dados
def conectar_banco():
    conn = sqlite3.connect('contrato.db')
    conn.row_factory = sqlite3.Row
    return conn

# Função para criar as tabelas no banco de dados
def criar_tabelas():
    conn = conectar_banco()
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       usuario TEXT NOT NULL,
                       senha TEXT NOT NULL)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS contratos
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       data_contrato TEXT NOT NULL,
                       data_vencimento TEXT NOT NULL,
                       numero INTEGER,
                       pdf BLOB,
                       nome_empresa TEXT,
                       cnpj TEXT,
                       assinado_por TEXT,
                       setor TEXT,
                       quem_adicionou TEXT)''')

    conn.commit()
    conn.close()

# Rota de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        senha = request.form['senha']

        conn = conectar_banco()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM usuarios WHERE usuario = ? AND senha = ?', (usuario, senha))
        usuario = cursor.fetchone()

        conn.close()

        if usuario:
            # Credenciais corretas, redirecionar para a página de envio de contrato
            return redirect(url_for('enviar_contrato'))
        else:
            flash('Usuário ou senha inválidos', 'error')

    return render_template('login.html')

# Rota para envio de contrato
@app.route('/enviar_contrato', methods=['GET', 'POST'])
def enviar_contrato():
    if request.method == 'POST':
        data_contrato = request.form['data_contrato']
        data_vencimento = request.form['data_vencimento']
        numero = request.form['numero']
        pdf = request.files['pdf']
        nome_empresa = request.form['nome_empresa']
        cnpj = request.form['cnpj']
        assinado_por = request.form['assinado_por']
        setor = request.form['setor']
        quem_adicionou = request.form['quem_adicionou']

        conn = conectar_banco()
        cursor = conn.cursor()

        cursor.execute('''INSERT INTO contratos (data_contrato, data_vencimento, numero, pdf, nome_empresa, cnpj, assinado_por, setor, quem_adicionou)
                  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (data_contrato, data_vencimento, numero, pdf.read(), nome_empresa, cnpj, assinado_por, setor, quem_adicionou))



        conn.commit()
        conn.close()

        flash('Contrato enviado com sucesso!', 'success')

    return render_template('enviar_contrato.html')

# Rota para listar contratos
@app.route('/listar_contratos')
def listar_contratos():
    conn = conectar_banco()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM contratos')
    contratos = cursor.fetchall()

    conn.close()

    return render_template('listar_contratos.html', contratos=contratos)

# Rota para baixar o PDF de um contrato
@app.route('/download_pdf/<int:contrato_id>')
def download_pdf(contrato_id):
    conn = conectar_banco()
    cursor = conn.cursor()

    cursor.execute('SELECT pdf FROM contratos WHERE id = ?', (contrato_id,))
    pdf_data = cursor.fetchone()[0]

    conn.close()

    return app.response_class(pdf_data, mimetype='application/pdf',
                              headers={'Content-Disposition': 'attachment; filename=contrato.pdf'})

# Rota inicial
@app.route('/')
def index():
    return redirect(url_for('login'))

if __name__ == '__main__':
    criar_tabelas()
    app.run(debug=True, host='192.168.1.67', port=5005)

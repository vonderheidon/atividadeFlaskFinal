from flask import Flask, render_template, request, redirect, url_for, flash, session
import dao

app = Flask(__name__)
app.secret_key = '123chave'


@app.route('/', methods=['GET', 'POST'])
def index():
    if 'usuario_logado' in session:
        return redirect(url_for('listar_produtos'))

    if request.method == 'POST':
        login = request.form['login']
        senha = request.form['senha']
        if dao.verificarLogin(login, senha):
            session['usuario_logado'] = login
            return redirect(url_for('listar_produtos'))
        else:
            flash("Login ou senha incorretos.")

    return render_template('index.html')

@app.route('/listarUsuarios')
def listar_usuarios():
    if 'usuario_logado' not in session:
        flash("Você precisa estar logado para acessar esta página.")
        return redirect(url_for('index'))

    login = session['usuario_logado']
    usuario = dao.buscarUsuarioPorLogin(login)

    if usuario is None:
        flash("Usuário não encontrado.")
        return redirect(url_for('index'))

    tipo_usuario = usuario[2]

    if tipo_usuario != 'super':
        flash("Você não tem permissão para acessar esta página.")
        return redirect(url_for('listar_produtos'))

    usuarios = dao.buscarUsuarios()
    return render_template('listarUsuarios.html', usuarios=usuarios)


@app.route('/editar/<login>', methods=['GET', 'POST'])
def editar_usuario(login):
    if 'usuario_logado' not in session:
        flash("Você precisa estar logado para acessar esta página.")
        return redirect(url_for('index'))

    if request.method == 'POST':
        novo_tipo = request.form['tipo']
        dao.atualizarTipoUsuario(login, novo_tipo)
        flash("Usuário atualizado com sucesso.")
        return redirect(url_for('listar_usuarios'))

    usuario = dao.buscarUsuarioPorLogin(login)
    if usuario:
        return render_template('editarUsuario.html', usuario=usuario)
    else:
        flash("Usuário não encontrado.")
        return redirect(url_for('listar_usuarios'))


@app.route('/listarProdutos')
def listar_produtos():
    if 'usuario_logado' not in session:
        flash("Você precisa estar logado para acessar esta página.")
        return redirect(url_for('index'))

    loginuser = session['usuario_logado']
    usuario = dao.buscarUsuarioPorLogin(loginuser)

    if not usuario:
        flash("Usuário não encontrado.")
        return redirect(url_for('index'))

    tipo_usuario = usuario[2]
    produtos = dao.buscarProdutos()

    return render_template('listarProdutos.html', produtos=produtos, tipo_usuario=tipo_usuario)


@app.route('/adicionarProduto', methods=['GET', 'POST'])
def adicionar_produto():
    if 'usuario_logado' not in session:
        flash("Você precisa estar logado para acessar esta página.")
        return redirect(url_for('index'))

    loginuser = session['usuario_logado']

    usuario = dao.buscarUsuarioPorLogin(loginuser)
    if not usuario:
        flash("Usuário não encontrado.")
        return redirect(url_for('index'))

    tipo_usuario = usuario[2]
    num_produtos = dao.contarProdutos(loginuser)

    if tipo_usuario == 'normal' and num_produtos >= 3:
        flash("Você não pode adicionar mais produtos. O limite de 3 produtos foi atingido.")
        return redirect(url_for('listar_produtos'))

    if request.method == 'POST':
        nome = request.form['nome']
        qtde = request.form['qtde']
        preco = request.form['preco']

        dao.adicionarProduto(nome, loginuser, qtde, preco)
        flash("Produto adicionado com sucesso.")
        return redirect(url_for('listar_produtos'))

    return render_template('adicionarProduto.html')


@app.route('/detalhesProduto/<int:id>')
def detalhes_produto(id):
    if 'usuario_logado' not in session:
        flash("Você precisa estar logado para acessar esta página.")
        return redirect(url_for('index'))

    produto = dao.buscarProdutoPorId(id)
    if produto:
        return render_template('detalhesProduto.html', produto=produto)
    else:
        flash("Produto não encontrado.")
        return redirect(url_for('listar_produtos'))


@app.route('/editarProduto/<int:id>', methods=['GET', 'POST'])
def editar_produto(id):
    if 'usuario_logado' not in session:
        flash("Você precisa estar logado para acessar esta página.")
        return redirect(url_for('index'))

    if request.method == 'POST':
        nome = request.form['nome']
        qtde = request.form['qtde']
        preco = request.form['preco']
        dao.atualizarProduto(id, nome, qtde, preco)
        flash("Produto atualizado com sucesso.")
        return redirect(url_for('listar_produtos'))

    produto = dao.buscarProdutoPorId(id)
    if produto:
        return render_template('editarProduto.html', produto=produto)
    else:
        flash("Produto não encontrado.")
        return redirect(url_for('listar_produtos'))


@app.route('/excluirProduto/<int:id>', methods=['GET'])
def excluir_produto(id):
    if 'usuario_logado' not in session:
        flash("Você precisa estar logado para acessar esta página.")
        return redirect(url_for('index'))

    dao.excluirProduto(id)
    flash("Produto excluído com sucesso.")
    return redirect(url_for('listar_produtos'))


@app.route('/logout')
def logout():
    session.pop('usuario_logado', None)
    flash("Você foi desconectado.")
    return redirect(url_for('index'))


@app.route('/cadastrarUsuario', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        login = request.form['login']
        senha = request.form['senha']
        tipo_usuario = 'super' if request.form.get('super') else 'normal'

        if dao.verificarSeLoginExiste(login):
            flash("Este login já está em uso. Tente outro.")
        else:
            dao.criarUsuario(login, senha, tipo_usuario)
            flash("Cadastro realizado com sucesso. Faça login para continuar.")
            return redirect(url_for('index'))

    return render_template('cadastrarUsuario.html')

if __name__ == '__main__':
    app.run(debug=True)

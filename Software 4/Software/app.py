from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from core.database import Database
import json
from models.estoque import Estoque
from models.galpao import Galpao
from models.produto import Produto
from models.movimentacao import Movimentacao
from models.pedidocliente import PedidoCliente
from models.fornecedor import Fornecedor
from models.cliente import Cliente
from models.funcionario import Funcionario
from models.endereco import Endereco
from models.empilhadeira import Empilhadeira


app = Flask(__name__)
app.secret_key = "chave_secreta"

# ---------------- FUNÇÕES AUXILIARES ---------------- #

def to_int(value, default=0):
    try:
        return int(value)
    except:
        return default

def to_float(value, default=0.0):
    try:
        return float(value)
    except:
        return default

# ------------- LANDINGPAGE ------------- #

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/home')
def home():
    return render_template('home.html')

# ---------------- LOGIN OBRIGATÓRIO ---------------- #

def login_obrigatorio(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if "usuario_logado" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrap

# ---------------- INDEX ---------------- #

@app.route("/dashboard")
@login_obrigatorio
def dashboard():
    conexao = Database.connect()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS total FROM fornecedor")
    total_fornecedores = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM cliente")
    total_clientes = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM galpao")
    total_galpoes = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM produto")
    total_produtos = cursor.fetchone()["total"]

    cursor.close()
    conexao.close()

    return render_template(
        "dashboard.html",
        total_fornecedores=total_fornecedores,
        total_clientes=total_clientes,
        total_galpoes=total_galpoes,
        total_produtos=total_produtos
    )
# ---------------- LOGIN ---------------- #

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")

        conexao = Database.connect()
        cursor = conexao.cursor(dictionary=True)

        try:
            sql = "SELECT * FROM usuario WHERE email = %s"
            cursor.execute(sql, (email,))
            usuario = cursor.fetchone()

            if usuario and check_password_hash(usuario["senha"], senha):
                session["usuario_logado"] = usuario["email"]
                session["empresa_id"] = usuario["empresa_id"]

                flash("Login realizado!", "sucesso")
                return redirect(url_for("dashboard"))
            else:
                flash("Email ou senha inválidos!", "erro")

        finally:
            cursor.close()
            conexao.close()

    return render_template("login.html")

# ---------------- LOGOUT ---------------- #

@app.route('/logout')
def logout():
    session.clear()
    flash("Você saiu da conta.", "sucesso")
    return redirect(url_for('login'))

# ---------------- CADASTRO DE EMPRESA ---------------- #

@app.route("/cadastro", methods=["GET", "POST"])
def cadastro_emp():
 
    if request.method == "POST":
 
        nome = request.form.get("nome")
        cpf = request.form.get("cnpj")
        email = request.form.get("email")
        telefone = request.form.get("telefone")
        senha = generate_password_hash(request.form.get("senha"))
 
        conexao = Database.connect()
        cursor = conexao.cursor()
 
        try:
 
            # salva empresa
            cursor.execute("""
                INSERT INTO empresa (nome, cnpj)
                VALUES (%s, %s)
            """, (nome, cpf))
 
            empresa_id = cursor.lastrowid
 
            # salva usuário
            cursor.execute("""
                INSERT INTO usuario
                (nome, telefone, email, senha, empresa_id, tipo)
                VALUES (%s, %s, %s, %s, %s, 'admin')
            """, (
                nome,
                telefone,
                email,
                senha,
                empresa_id
            ))
 
            conexao.commit()
 
            flash("Cadastro realizado com sucesso!", "sucesso")
            return redirect(url_for("login"))
 
        except Exception as e:
            conexao.rollback()
            print("ERRO:", e)
            flash(f"Erro ao cadastrar: {e}", "erro")
 
        finally:
            cursor.close()
            conexao.close()
 
    return render_template("cadastro.html")
# ---------------- ESTOQUE ---------------- #

@app.route("/estoque")
@login_obrigatorio
def estoque():
    produtos = Estoque.resumo_geral()
    return render_template("estoque.html", produtos=produtos, galpao=None)

@app.route("/estoque/<int:galpao_id>")
@login_obrigatorio
def estoque_galpao(galpao_id):
    produtos = Estoque.find_by_galpao(galpao_id)
    galpao = Galpao.find_by_id(galpao_id)
    fornecedores = Fornecedor.find_all()

    return render_template(
        "estoque.html",
        produtos=produtos,
        galpao=galpao,
        fornecedores=fornecedores
    )

@app.route("/estoque/movimentar", methods=["POST"])
@login_obrigatorio
def movimentar_estoque():
    galpao_id = to_int(request.form.get("galpao_id"))
    try:
        produto_id = to_int(request.form.get("produto_id"))
        quantidade = to_int(request.form.get("quantidade"))
        tipo = request.form.get("tipo")

        Estoque.movimentar(produto_id, galpao_id, quantidade, tipo)
        flash("Movimentação realizada com sucesso!", "sucesso")

    except Exception as e:
        flash(f"Erro: {e}", "erro")

    return redirect(url_for("estoque", galpao_id=galpao_id))

# ---------------- INFO GALPAO ---------------- #

@app.route("/info_galpao/<int:galpao_id>")
@login_obrigatorio
def info_galpao(galpao_id):
    galpao = Galpao.find_by_id(galpao_id)
    funcionarios = Funcionario.find_by_galpao(galpao_id)
    empilhadeiras = Empilhadeira.find_by_galpao(galpao_id)

    return render_template(
        "info_galpao.html",
        galpao=galpao,
        funcionarios=funcionarios,
        empilhadeiras=empilhadeiras
    )

@app.route("/galpao/atualizar/<int:galpao_id>", methods=["POST"])
@login_obrigatorio
def atualizar_galpao(galpao_id):
    try:
        caixas_por_nivel      = to_int(request.form.get("caixas_por_nivel"))
        niveis_por_prateleira = to_int(request.form.get("niveis_por_prateleira"))
        total_prateleiras     = to_int(request.form.get("total_prateleiras"))
        capacidade_total      = caixas_por_nivel * niveis_por_prateleira * total_prateleiras

        dados = {
            "nome_resp":             request.form.get("nome_resp"),
            "email_resp":            request.form.get("email_resp"),
            "telefone":              request.form.get("telefone"),
            "stats":                 request.form.get("stats"),
            "nome":                  request.form.get("nome"),
            "cep":                   request.form.get("cep"),
            "endereco":              request.form.get("endereco"),
            "referencia":            request.form.get("referencia"),
            "area_total":            to_float(request.form.get("area_total")),
            "caixas_por_nivel":      caixas_por_nivel,
            "niveis_por_prateleira": niveis_por_prateleira,
            "total_prateleiras":     total_prateleiras,
            "capacidade_total":      capacidade_total,
        }
        Galpao.update(galpao_id, dados)
        flash("Galpão atualizado com sucesso!", "sucesso")
    except Exception as e:
        flash(f"Erro: {e}", "erro")
    return redirect(url_for("info_galpao", galpao_id=galpao_id))


@app.route("/galpao/deletar/<int:galpao_id>", methods=["POST"])
@login_obrigatorio
def deletar_galpao(galpao_id):
    try:
        Galpao.delete(galpao_id)
        flash("Galpão excluído com sucesso!", "sucesso")
    except Exception as e:
        flash(f"Erro: {e}", "erro")
    return redirect(url_for("galpao"))
    


# ---------------- EMPILHADEIRAS ---------------- #

@app.route("/empilhadeira/salvar", methods=["POST"])
@login_obrigatorio
def salvar_empilhadeira():
    try:
        empilhadeira = Empilhadeira(
            marca=request.form.get("marca"),
            modelo=request.form.get("modelo"),
            ano_fabricacao=request.form.get("ano_fabricacao"),
            tipo_combustivel=request.form.get("tipo_combustivel"),
            capacidade=request.form.get("capacidade"),
            galpao_id=request.form.get("galpao_id"),
            ativo=request.form.get("ativo")
        )
        empilhadeira.insert()
        flash("Empilhadeira cadastrada com sucesso!", "sucesso")

    except Exception as e:
        flash(f"Erro: {e}", "erro")

    return redirect(url_for("info_galpao", galpao_id=request.form.get("galpao_id")))

@app.route("/empilhadeira/atualizar/<int:empilhadeira_id>", methods=["POST"])
@login_obrigatorio
def atualizar_empilhadeira(empilhadeira_id):
    galpao_id = request.form.get("galpao_id")
    try:
        conn = Database.connect()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE empilhadeira
            SET marca=%s, modelo=%s, ano_fabricacao=%s,
                tipo_combustivel=%s, capacidade=%s, ativo=%s
            WHERE id=%s
        """, (
            request.form["marca"],
            request.form["modelo"],
            request.form["ano_fabricacao"],
            request.form["tipo_combustivel"],
            request.form["capacidade"],
            request.form["ativo"],
            empilhadeira_id
        ))
        conn.commit()
        conn.close()
        flash("Empilhadeira atualizada com sucesso!", "sucesso")
    except Exception as e:
        flash(f"Erro: {e}", "erro")
    return redirect(url_for("info_galpao", galpao_id=galpao_id))


@app.route("/empilhadeira/deletar/<int:empilhadeira_id>", methods=["POST"])
@login_obrigatorio
def deletar_empilhadeira(empilhadeira_id):
    galpao_id = request.form.get("galpao_id")
    try:
        conn = Database.connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM empilhadeira WHERE id = %s", (empilhadeira_id,))
        conn.commit()
        conn.close()
        flash("Empilhadeira removida com sucesso!", "sucesso")
    except Exception as e:
        flash(f"Erro: {e}", "erro")
    return redirect(url_for("info_galpao", galpao_id=galpao_id))


# ---------------- PRODUTOS ---------------- #

@app.route("/produtos")
@login_obrigatorio
def produtos():
    lista = Produto.find_all_completo()
    return render_template("estoque.html", produtos=lista, galpao=None)

@app.route("/produto/salvar", methods=["POST"])
@login_obrigatorio
def salvar_produto():
    galpao_id = to_int(request.form.get("galpao_id"))

    try:
        produto = Produto(
            sku=request.form.get("sku"),
            nome=request.form.get("nome"),
            descricao=request.form.get("descricao"),
            categoria=request.form.get("categoria"),
            preco_custo=to_float(request.form.get("preco_custo")),
            preco_venda=to_float(request.form.get("preco_venda")),
            peso=to_float(request.form.get("peso")),
            volume=to_float(request.form.get("volume")),
            tipo=request.form.get("tipo"),
            codigo_barras=request.form.get("codigo_barras"),
        )

        erros = produto.validate()
        if erros:
            for erro in erros:
                flash(erro, "erro")
            return redirect(url_for("estoque_galpao", galpao_id=galpao_id))

        produto_id = produto.insert()

        quantidade = to_int(request.form.get("quantidade"))
        quantidade_minimo = to_int(request.form.get("quantidade_minimo"))

        if galpao_id:
            conn = Database.connect()
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO estoque (produto_id, galpao_id, quantidade, estoque_minimo)
                    VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        quantidade = VALUES(quantidade),
                        estoque_minimo = VALUES(estoque_minimo)
                """, (produto_id, galpao_id, quantidade, quantidade_minimo))
                conn.commit()
            finally:
                cursor.close()
                conn.close()

        flash("Produto cadastrado com sucesso!", "sucesso")

    except Exception as e:
        flash(f"Erro: {e}", "erro")

    return redirect(url_for("estoque_galpao", galpao_id=galpao_id))

@app.route("/produto/editar/<int:id>")
@login_obrigatorio
def editar_produto(id):
    # Redireciona para info_produtos, que já exibe o formulário de edição
    return redirect(url_for("info_produtos", id=id))

@app.route("/produto/atualizar/<int:id>", methods=["POST"])
@login_obrigatorio
def atualizar_produto(id):

    dados = {
        "sku": request.form.get("sku"),
        "nome": request.form.get("nome"),
        "descricao": request.form.get("descricao"),
        "categoria": request.form.get("categoria"),
        "preco_custo": to_float(request.form.get("preco_custo")),
        "preco_venda": to_float(request.form.get("preco_venda")),
        "peso": to_float(request.form.get("peso")),
        "volume": to_float(request.form.get("volume")),
        "tipo": request.form.get("tipo"),
        "codigo_barras": request.form.get("codigo_barras"),
        "item_por_caixa": to_int(request.form.get("item_por_caixa")),
        "estoque_minimo": to_int(request.form.get("estoque_minimo"))
    }

    try:
        Produto.update(id, dados)

        conn = Database.connect()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE estoque
            SET estoque_minimo = %s
            WHERE produto_id = %s
        """, (
            dados["estoque_minimo"],
            id
        ))

        conn.commit()

        cursor.close()
        conn.close()

        flash("Produto atualizado com sucesso!", "sucesso")

    except Exception as e:
        flash(f"Erro ao atualizar produto: {e}", "erro")

    return redirect(url_for("info_produtos", id=id))

@app.route("/produto/desativar/<int:id>")
@login_obrigatorio
def desativar_produto(id):
    try:
        Produto.desativar(id)
        flash("Produto desativado com sucesso!", "sucesso")
    except Exception as e:
        flash(f"Erro: {e}", "erro")
    return redirect(url_for("info_produtos", id=id))

@app.route("/produto/reativar/<int:id>")
@login_obrigatorio
def reativar_produto(id):
    try:
        Produto.reativar(id)
        flash("Produto reativado com sucesso!", "sucesso")
    except Exception as e:
        flash(f"Erro: {e}", "erro")
    return redirect(url_for("produtos_inativos"))

@app.route("/produtos/inativos")
@login_obrigatorio
def produtos_inativos():
    lista = Produto.find_inativos()
    return render_template("produtos_inativos.html", produtos=lista)

@app.route("/produto/excluir/<int:id>")
@login_obrigatorio
def excluir_produto(id):
    try:
        Produto.safe_delete(id)
        flash("Produto excluído com sucesso!", "sucesso")
    except ValueError as e:
        flash(str(e), "erro")
        return redirect(url_for("info_produtos", id=id))
    except Exception as e:
        flash(f"Erro: {e}", "erro")
        return redirect(url_for("info_produtos", id=id))

    return redirect(url_for("produtos"))

# ---------------- INFO PRODUTO ---------------- #

@app.route("/info_produto/<int:id>")
@login_obrigatorio
def info_produtos(id):
    conn = Database.connect()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                p.*,
                COALESCE(SUM(e.quantidade), 0)      AS quantidade,
                COALESCE(MIN(e.estoque_minimo), 0)  AS estoque_minimo,
                GROUP_CONCAT(DISTINCT f.nome ORDER BY f.nome SEPARATOR ', ')
                                                    AS fornecedor
            FROM produto p
            LEFT JOIN estoque e              ON p.id = e.produto_id
            LEFT JOIN fornecedor_produto fp  ON p.id = fp.produto_id
            LEFT JOIN fornecedor f           ON fp.fornecedor_id = f.id
            WHERE p.id = %s
            GROUP BY p.id
        """, (id,))
        produto = cursor.fetchone()

        if not produto:
            flash("Produto não encontrado.", "erro")
            return redirect(url_for("produtos"))

        produtos = Produto.find_all_completo()

    finally:
        cursor.close()
        conn.close()

    return render_template("info_produto.html", produto=produto, produtos=produtos)

# ---------------- GALPÕES ---------------- #

@app.route("/galpao")
@login_obrigatorio
def galpao():
    return render_template("galpao.html", galpoes=Galpao.find_all())

@app.route("/galpao/novo")
@login_obrigatorio
def novo_galpao():
    return render_template("galpao.html")

@app.route("/galpao/salvar", methods=["POST"])
@login_obrigatorio
def salvar_galpao():
    try:
        caixas_por_nivel = to_int(request.form.get("caixas_por_nivel"))
        niveis_por_prateleira = to_int(request.form.get("niveis_por_prateleira"))
        total_prateleiras = to_int(request.form.get("total_prateleiras"))
        capacidade_total = caixas_por_nivel * niveis_por_prateleira * total_prateleiras

        g = Galpao(
            nome=request.form.get("nome"),
            stats=request.form.get("stats"),
            cep=request.form.get("cep"),
            email_resp=request.form.get("email_resp"),
            nome_resp=request.form.get("nome_resp"),
            endereco=request.form.get("endereco"),
            referencia=request.form.get("referencia"),
            cidade=request.form.get("cidade"),
            estado=request.form.get("estado"),
            area_total=to_float(request.form.get("area_total")),
            telefone=request.form.get("telefone"),
            total_prateleiras=total_prateleiras,
            niveis_por_prateleira=niveis_por_prateleira,
            caixas_por_nivel=caixas_por_nivel,
            capacidade_total=capacidade_total
        )
        g.insert()
        flash("Galpão cadastrado com sucesso!", "sucesso")

    except Exception as e:
        flash(f"Erro: {e}", "erro")

    return redirect(url_for("galpao"))

# ---------------- FORNECEDORES ---------------- #

@app.route("/fornecedores")
@login_obrigatorio
def fornecedores():
    conexao = Database.connect()
    cursor = conexao.cursor(dictionary=True)

    try:
        # Removido o WHERE ativo = 'ativo' — agora traz todos
        cursor.execute("""
            SELECT
                f.id,
                f.nome,
                f.nome_ctt,
                f.email,
                f.telefone,
                f.ativo,
                f.cnpj,
                COUNT(fp.produto_id) AS total_produtos

            FROM fornecedor f

            LEFT JOIN fornecedor_produto fp
                ON fp.fornecedor_id = f.id

            GROUP BY
                f.id,
                f.nome,
                f.nome_ctt,
                f.email,
                f.telefone,
                f.ativo,
                f.cnpj

            ORDER BY f.nome ASC
        """)

        lista_fornecedores = cursor.fetchall()
        

        cursor.execute("SELECT id, nome, sku FROM produto ORDER BY nome ASC")
        lista_produtos = cursor.fetchall()

        cursor.execute("""
            SELECT
                fp.produto_id,
                fp.fornecedor_id,
                p.nome AS produto_nome,
                p.sku,
                f.nome AS fornecedor_nome,
                fp.preco_custo,
                fp.desconto,
                fp.quantidade_minima,
                fp.prazo_entrega_dias,
                fp.ativo
            FROM fornecedor_produto fp
            JOIN produto p ON fp.produto_id = p.id
            JOIN fornecedor f ON fp.fornecedor_id = f.id
            ORDER BY f.nome ASC, p.nome ASC
        """)
        fornecedores_produtos = cursor.fetchall()

    finally:
        cursor.close()
        conexao.close()

    return render_template(
        "fornecedores.html",
        fornecedores=lista_fornecedores,
        lista_fornecedores=lista_fornecedores,
        lista_produtos=lista_produtos,
        fornecedores_produtos=fornecedores_produtos
    )


@app.route("/fornecedor/novo")
@login_obrigatorio
def novo_fornecedor():
    return render_template("form_fornecedor.html")


@app.route("/fornecedor/salvar", methods=["POST"])
@login_obrigatorio
def salvar_fornecedor():
    try:
        fornecedor = Fornecedor(
            nome=request.form.get("nome"),
            ativo=request.form.get("ativo"),
            cnpj=request.form.get("cnpj"),
            nome_ctt=request.form.get("nome_ctt"),
            telefone=request.form.get("telefone"),
            email=request.form.get("email")
        )
        fornecedor.insert()
        flash("Fornecedor cadastrado!", "sucesso")
    except Exception as e:
        flash(f"Erro: {e}", "erro")
    return redirect(url_for("fornecedores"))


@app.route("/fornecedor/atualizar/<int:fornecedor_id>", methods=["POST"])
@login_obrigatorio
def atualizar_fornecedor(fornecedor_id):
    try:
        conexao = Database.connect()
        cursor = conexao.cursor()

        cursor.execute("""
            UPDATE fornecedor
            SET nome=%s, cnpj=%s, nome_ctt=%s, email=%s, telefone=%s, ativo=%s
            WHERE id=%s
        """, (
            request.form.get("nome"),
            request.form.get("cnpj"),
            request.form.get("nome_ctt"),
            request.form.get("email"),
            request.form.get("telefone"),
            request.form.get("ativo"),
            fornecedor_id
        ))

        conexao.commit()
        flash("Fornecedor atualizado com sucesso!", "sucesso")

    except Exception as e:
        flash(f"Erro: {e}", "erro")

    finally:
        cursor.close()
        conexao.close()

    return redirect(url_for("fornecedores"))


@app.route("/fornecedor/deletar/<int:fornecedor_id>", methods=["POST"])
@login_obrigatorio
def deletar_fornecedor(fornecedor_id):
    try:
        conexao = Database.connect()
        cursor = conexao.cursor()

        cursor.execute("DELETE FROM fornecedor WHERE id = %s", (fornecedor_id,))
        conexao.commit()
        flash("Fornecedor removido com sucesso!", "sucesso")

    except Exception as e:
        flash(f"Erro: {e}", "erro")

    finally:
        cursor.close()
        conexao.close()

    return redirect(url_for("fornecedores"))


@app.route("/fornecedores/vincular_produto", methods=["POST"])
@login_obrigatorio
def vincular_fornecedor_produto():
    fornecedor_id = to_int(request.form.get("fornecedor_id"))
    produto_id = to_int(request.form.get("produto_id"))
    preco_custo = to_float(request.form.get("preco_custo"))
    desconto = to_float(request.form.get("desconto"))
    quantidade_minima = to_int(request.form.get("quantidade_minima"))
    prazo_entrega_dias = to_int(request.form.get("prazo_entrega_dias"))

    conexao = Database.connect()
    cursor = conexao.cursor()

    try:
        sql = """
            INSERT INTO fornecedor_produto
            (fornecedor_id, produto_id, preco_custo, desconto, quantidade_minima, prazo_entrega_dias, ativo)
            VALUES (%s, %s, %s, %s, %s, %s, 1)
            ON DUPLICATE KEY UPDATE
                preco_custo = VALUES(preco_custo),
                desconto = VALUES(desconto),
                quantidade_minima = VALUES(quantidade_minima),
                prazo_entrega_dias = VALUES(prazo_entrega_dias),
                ativo = 1
        """
        cursor.execute(sql, (fornecedor_id, produto_id, preco_custo, desconto, quantidade_minima, prazo_entrega_dias))
        conexao.commit()
        flash("Produto associado ao fornecedor com sucesso!", "sucesso")
    except Exception as e:
        conexao.rollback()
        flash(f"Erro ao salvar vínculo comercial: {e}", "erro")
    finally:
        cursor.close()
        conexao.close()

    return redirect(url_for("fornecedores"))

# ---------------- INFO FORNECEDOR ---------------- #
@app.route("/info_fornecedor/<int:fornecedor_id>")
@login_obrigatorio
def info_fornecedor(fornecedor_id):
    fornecedor = Fornecedor.find_by_id(fornecedor_id)

    if not fornecedor:
        flash("Fornecedor não encontrado.", "erro")
        return redirect(url_for("fornecedores"))

    produtos = Fornecedor.find_produtos(fornecedor_id)
    lista_produtos = Produto.find_all()

    return render_template(
        "info_fornecedor.html",
        fornecedor=fornecedor,
        produtos=produtos,
        lista_produtos=lista_produtos,
        historico=[]   # FIX: evita erro no template enquanto a tabela de log não existe
    )

# ---------------- ITENS FORNECEDOR ---------------- #

@app.route("/itens_fornecedores/<int:fornecedor_id>")
@login_obrigatorio
def itens_fornecedor(fornecedor_id):
    conexao = Database.connect()
    cursor = conexao.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM fornecedor WHERE id = %s", (fornecedor_id,))
        fornecedor = cursor.fetchone()

        if not fornecedor:
            flash("Fornecedor não encontrado.", "erro")
            return redirect(url_for("fornecedores"))

        # Busca os produtos vinculados com todas as colunas que o template precisa
        cursor.execute("""
            SELECT
                p.id            AS produto_id,
                p.nome          AS produto_nome,
                p.sku,
                fp.preco_custo,
                fp.desconto,
                fp.quantidade_minima,
                fp.prazo_entrega_dias,
                fp.ativo,
                f.nome          AS fornecedor_nome
            FROM fornecedor_produto fp
            JOIN produto   p ON p.id  = fp.produto_id
            JOIN fornecedor f ON f.id = fp.fornecedor_id
            WHERE fp.fornecedor_id = %s
            ORDER BY p.nome ASC
        """, (fornecedor_id,))
        fornecedores_produtos = cursor.fetchall()

        return render_template(
            "itens_fornecedores.html",
            fornecedor=fornecedor,
            fornecedores_produtos=fornecedores_produtos
        )
    finally:
        cursor.close()
        conexao.close()


# Rota nova: cria o produto E já vincula ao fornecedor em uma só ação
@app.route("/fornecedor/<int:fornecedor_id>/salvar_item", methods=["POST"])
@login_obrigatorio
def salvar_item_fornecedor(fornecedor_id):
    try:
        produto = Produto(
            sku=request.form.get("sku"),
            nome=request.form.get("nome"),
            descricao=request.form.get("descricao"),
            categoria=request.form.get("categoria"),
            preco_custo=to_float(request.form.get("preco_custo")),
            preco_venda=0.0,
            peso=to_float(request.form.get("peso")),
            volume=to_float(request.form.get("volume")),
            tipo=request.form.get("tipo"),
            codigo_barras=request.form.get("codigo_barras") or None,
        )

        erros = produto.validate()
        if erros:
            for erro in erros:
                flash(erro, "erro")
            return redirect(url_for("itens_fornecedor", fornecedor_id=fornecedor_id))

        produto_id = produto.insert()

        # Salva campos extras que não estão no __init__ padrão
        conn = Database.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE produto
                SET unidade_medida = %s, item_por_caixa = %s
                WHERE id = %s
            """, (
                request.form.get("unidade_medida", "un"),
                to_int(request.form.get("item_por_caixa")),
                produto_id
            ))

            # Vincula ao fornecedor
            cursor.execute("""
                INSERT INTO fornecedor_produto
                    (fornecedor_id, produto_id, preco_custo, desconto,
                     quantidade_minima, prazo_entrega_dias, ativo)
                VALUES (%s, %s, %s, 0, %s, %s, 1)
                ON DUPLICATE KEY UPDATE
                    preco_custo       = VALUES(preco_custo),
                    quantidade_minima = VALUES(quantidade_minima),
                    prazo_entrega_dias = VALUES(prazo_entrega_dias),
                    ativo             = 1
            """, (
                fornecedor_id,
                produto_id,
                to_float(request.form.get("preco_custo")),
                to_int(request.form.get("pedido_minimo")),
                to_int(request.form.get("tempo_entrega")),
            ))
            conn.commit()
        finally:
            cursor.close()
            conn.close()

        flash("Produto cadastrado e vinculado ao fornecedor!", "sucesso")

    except Exception as e:
        flash(f"Erro: {e}", "erro")

    return redirect(url_for("itens_fornecedor", fornecedor_id=fornecedor_id))

# ---------------- CLIENTES ---------------- #

@app.route("/clientes")
@login_obrigatorio
def cliente():

    conexao = Database.connect()
    cursor = conexao.cursor(dictionary=True)

    sql = """
        SELECT
            c.*,
            COUNT(pc.id) AS total_pedidos,
            COALESCE(SUM(pc.valor_total), 0) AS total_gasto
        FROM cliente c
        LEFT JOIN pedido_cliente pc
            ON pc.cliente_id = c.id
        GROUP BY c.id
        ORDER BY c.empresa
    """

    cursor.execute(sql)
    clientes = cursor.fetchall()

    cursor.close()
    conexao.close()

    return render_template(
        "cliente.html",
        clientes=clientes
    )

@app.route("/cliente/novo")
@login_obrigatorio
def novo_cliente():
    return render_template("cliente.html")

@app.route("/cliente/salvar", methods=["POST"])
@login_obrigatorio
def salvar_cliente():
    try:
        c = Cliente(
            nome=request.form.get("nome"),
            ativo=request.form.get("ativo"),
            cidade=request.form.get("cidade"),
            empresa=request.form.get("empresa"),
            cep=request.form.get("cep"),
            estado=request.form.get("estado"),
            cpf_cnpj=request.form.get("cpf"),
            email=request.form.get("email"),
            telefone=request.form.get("telefone")
        )
        c.insert()
        flash("Cliente cadastrado!", "sucesso")
    except Exception as e:
        flash(f"Erro: {e}", "erro")
    return redirect(url_for("cliente"))

# ---------------- FUNCIONÁRIOS ---------------- #

@app.route("/funcionario/salvar", methods=["POST"])
@login_obrigatorio
def salvar_funcionario():
    try:
        salario = request.form.get("salario")
        salario = float(salario) if salario else 0.00

        funcionario = Funcionario(
            nome=request.form.get("nome"),
            cpf=request.form.get("cpf"),
            salario=salario,
            data_nascimento=request.form.get("data_nascimento"),
            data_admissao=request.form.get("data_admissao"),
            email=request.form.get("email"),
            telefone=request.form.get("telefone"),
            ativo=request.form.get("ativo"),
            cargo=request.form.get("cargo"),
            galpao_id=request.form.get("galpao_id")
        )
        funcionario.insert()
        flash("Funcionário cadastrado com sucesso!", "sucesso")

    except Exception as e:
        flash(f"Erro: {e}", "erro")

    return redirect(url_for("info_galpao", galpao_id=request.form.get("galpao_id")))

@app.route("/funcionario/atualizar", methods=["POST"])
@login_obrigatorio
def atualizar_funcionario():
    try:
        salario = request.form.get("salario")
        salario = float(salario) if salario else 0.00

        conn = Database.connect()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE funcionario
            SET nome=%s, cpf=%s, salario=%s, email=%s,
                telefone=%s, cargo=%s, ativo=%s
            WHERE id=%s
        """, (
            request.form["nome"],
            request.form["cpf"],
            salario,
            request.form["email"],
            request.form["telefone"],
            request.form["cargo"],
            request.form["ativo"],
            request.form["id"]
        ))

        conn.commit()
        conn.close()
        flash("Funcionário atualizado com sucesso!", "sucesso")

    except Exception as e:
        flash(f"Erro: {e}", "erro")

    return redirect(url_for("info_galpao", galpao_id=request.form.get("galpao_id")))

@app.route("/funcionario/deletar/<int:funcionario_id>", methods=["POST"])
@login_obrigatorio
def deletar_funcionario(funcionario_id):
    galpao_id = request.form.get("galpao_id")
    try:
        conn = Database.connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM funcionario WHERE id = %s", (funcionario_id,))
        conn.commit()
        conn.close()
        flash("Funcionário removido com sucesso!", "sucesso")
    except Exception as e:
        flash(f"Erro ao remover funcionário: {e}", "erro")
    return redirect(url_for("info_galpao", galpao_id=galpao_id))

# ---------------- MOVIMENTAÇÕES ---------------- #

@app.route("/movimentacoes")
@login_obrigatorio
def movimentacoes():
    return render_template(
        "movimentacoes.html",
        movimentacoes=Movimentacao.find_all_with_product()
    )

@app.route("/movimentacao/nova")
@login_obrigatorio
def nova_movimentacao():
    lista = Produto.find_all()
    return render_template("form_movimentacao.html", produtos=lista)

@app.route("/movimentacao/salvar", methods=["POST"])
@login_obrigatorio
def salvar_movimentacao():
    produto_id = to_int(request.form.get("produto_id"))
    galpao_id = to_int(request.form.get("galpao_id"))
    funcionario_id = to_int(request.form.get("funcionario_id"))
    tipo = request.form.get("tipo").lower()
    quantidade = to_float(request.form.get("quantidade"))

    try:
        conexao = Database.connect()
        cursor = conexao.cursor()

        cursor.execute("""
            INSERT INTO movimentacao
            (produto_id, galpao_id, funcionario_id, tipo, quantidade)
            VALUES (%s, %s, %s, %s, %s)
        """, (produto_id, galpao_id, funcionario_id, tipo, quantidade))

        cursor.execute("""
            SELECT quantidade FROM estoque
            WHERE produto_id = %s AND galpao_id = %s
        """, (produto_id, galpao_id))

        resultado = cursor.fetchone()
        atual = resultado[0] if resultado else 0

        if tipo == "entrada":
            nova_qtd = atual + quantidade
        elif tipo == "saida":
            nova_qtd = atual - quantidade
        else:
            nova_qtd = atual

        cursor.execute("""
            UPDATE estoque SET quantidade = %s
            WHERE produto_id = %s AND galpao_id = %s
        """, (nova_qtd, produto_id, galpao_id))

        conexao.commit()
        conexao.close()
        flash("Movimentação registrada!", "sucesso")

    except Exception as e:
        flash(f"Erro: {e}", "erro")

    return redirect(url_for("movimentacoes"))

# ---------------- INFO CLIENTES ---------------- #

@app.route("/info_cliente/<int:cliente_id>")
@login_obrigatorio
def info_cliente(cliente_id):
    c = Cliente.find_by_id(cliente_id)
    if not c:
        flash("Cliente não encontrado.", "erro")
        return redirect(url_for("cliente"))
    pedidos = PedidoCliente.find_by_cliente(cliente_id)
    return render_template("info_cliente.html", cliente=c, pedidos=pedidos)


@app.route("/cliente/atualizar/<int:cliente_id>", methods=["POST"])
@login_obrigatorio
def atualizar_cliente(cliente_id):
    try:
        dados = {
            "nome":     request.form.get("nome"),
            "ativo":   request.form.get("ativo"),
            "empresa":  request.form.get("empresa"),
            "email":    request.form.get("email"),
            "telefone": request.form.get("telefone"),
            "cep":      request.form.get("cep"),
            "cidade":   request.form.get("cidade"),
            "estado":   request.form.get("estado"),
        }
        Cliente.update(cliente_id, dados)
        flash("Cliente atualizado com sucesso!", "sucesso")
    except Exception as e:
        flash(f"Erro: {e}", "erro")
    return redirect(url_for("info_cliente", cliente_id=cliente_id))


@app.route("/cliente/deletar/<int:cliente_id>", methods=["POST"])
@login_obrigatorio
def deletar_cliente(cliente_id):
    try:
        Cliente.delete(cliente_id)
        flash("Cliente excluído com sucesso!", "sucesso")
    except Exception as e:
        flash(f"Erro: {e}", "erro")
    return redirect(url_for("cliente"))


# ------------------------------------------------------------------ #
# API — produtos disponíveis por galpão                               #
# ------------------------------------------------------------------ #

@app.route("/api/produtos_do_galpao/<int:galpao_id>")
@login_obrigatorio
def api_produtos_do_galpao(galpao_id):
    from flask import jsonify
    conn = Database.connect()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT p.id, p.sku, p.nome, p.preco_venda,
                   e.quantidade AS estoque_disponivel
            FROM estoque e
            JOIN produto p ON e.produto_id = p.id
            WHERE e.galpao_id = %s AND e.quantidade > 0
            ORDER BY p.nome ASC
        """, (galpao_id,))
        return jsonify(cursor.fetchall())
    finally:
        cursor.close()
        conn.close()
        
@app.route("/api/todos_produtos")
@login_obrigatorio
def api_todos_produtos():
    from flask import jsonify
    conn = Database.connect()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT id, sku, nome, preco_custo
            FROM produto
            WHERE ativo = TRUE
            ORDER BY nome ASC
        """)
        return jsonify(cursor.fetchall())
    finally:
        cursor.close()
        conn.close()

@app.route("/api/produtos_do_fornecedor/<int:fornecedor_id>")
@login_obrigatorio
def api_produtos_do_fornecedor(fornecedor_id):
    from flask import jsonify
    conn = Database.connect()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT
                p.id,
                p.sku,
                p.nome,
                fp.preco_custo,
                COALESCE(e_total.estoque_disponivel, 0) AS estoque_disponivel
            FROM fornecedor_produto fp
            JOIN produto p ON fp.produto_id = p.id
            LEFT JOIN (
                SELECT produto_id, SUM(quantidade) AS estoque_disponivel
                FROM estoque
                GROUP BY produto_id
            ) e_total ON e_total.produto_id = p.id
            WHERE fp.fornecedor_id = %s
              AND fp.ativo = 1
              AND p.ativo = TRUE
            ORDER BY p.nome ASC
        """, (fornecedor_id,))
        return jsonify(cursor.fetchall())
    finally:
        cursor.close()
        conn.close()
# ------------------------------------------------------------------ #
# PEDIDOS DE ENTRADA  (usa tabela: pedido_fornecedor)                 #
# ------------------------------------------------------------------ #
@app.route("/cadastro_pedido_entrada")
@login_obrigatorio
def cadastro_pedido_entrada():
    return render_template(
        "pedidos_fornecedor.html",
        galpoes=Galpao.find_all(),
        fornecedores=Fornecedor.find_all()
    )



@app.route("/cadastro_pedido/<int:cliente_id>")
@login_obrigatorio
def cadastro_pedido(cliente_id):
    cliente = Cliente.find_by_id(cliente_id)
    if not cliente:
        flash("Cliente não encontrado.", "erro")
        return redirect(url_for("cliente"))
    return render_template(
        "cadastro_pedidos.html",
        galpoes=Galpao.find_all(),
        cliente=cliente
    )

@app.route("/pedidos_entrada")
@login_obrigatorio
def listar_pedidos_entrada():
    conn = Database.connect()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT pf.*, f.nome AS fornecedor_nome, g.nome AS galpao_nome
            FROM pedido_fornecedor pf
            LEFT JOIN fornecedor f ON pf.fornecedor_id = f.id
            LEFT JOIN galpao     g ON pf.galpao_id     = g.id
            ORDER BY pf.id DESC
        """)
        pedidos = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    return render_template(
        "pedidos_fornecedor.html",
        pedidos=pedidos,
        galpoes=Galpao.find_all(),
        fornecedores=Fornecedor.find_all()
    )

@app.route("/salvar_pedido_entrada", methods=["POST"])
@login_obrigatorio
def salvar_pedido_entrada():
    fornecedor_id    = to_int(request.form.get("fornecedor_id"))
    galpao_id        = to_int(request.form.get("galpao_id"))
    numero_documento = request.form.get("numero_documento")
    data_prevista    = request.form.get("data_entrada")
    observacao       = request.form.get("observacao")

    try:
        itens = json.loads(request.form.get("itens_json", "[]"))
    except Exception:
        itens = []

    if not itens:
        flash("Adicione pelo menos um item ao pedido.", "erro")
        return redirect(url_for("novo_pedido_entrada"))

    if not fornecedor_id or not galpao_id:
        flash("Selecione o fornecedor e o galpão de destino.", "erro")
        return redirect(url_for("novo_pedido_entrada"))

    valor_total = sum(i["quantidade"] * i["preco_unitario"] for i in itens)

    conn = Database.connect()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO pedido_fornecedor
                (fornecedor_id, galpao_id, numero_documento,
                 data_prevista, observacao, status, valor_total)
            VALUES (%s, %s, %s, %s, %s, 'recebido', %s)
        """, (fornecedor_id, galpao_id, numero_documento,
              data_prevista, observacao, valor_total))
        pedido_id = cursor.lastrowid

        for item in itens:
            cursor.execute("""
                INSERT INTO item_pedido_fornecedor
                    (pedido_fornecedor_id, produto_id, quantidade, preco_unitario)
                VALUES (%s, %s, %s, %s)
            """, (pedido_id, item["produto_id"],
                  item["quantidade"], item["preco_unitario"]))

            # Incrementa estoque automaticamente
            cursor.execute("""
                INSERT INTO estoque (produto_id, galpao_id, quantidade, estoque_minimo)
                VALUES (%s, %s, %s, 0)
                ON DUPLICATE KEY UPDATE quantidade = quantidade + VALUES(quantidade)
            """, (item["produto_id"], galpao_id, item["quantidade"]))

        conn.commit()
        flash("Pedido de entrada cadastrado com sucesso!", "sucesso")
        return redirect(url_for("listar_pedidos_entrada"))

    except Exception as e:
        conn.rollback()
        flash(f"Erro ao cadastrar pedido de entrada: {e}", "erro")
        return redirect(url_for("novo_pedido_entrada"))
    finally:
        cursor.close()
        conn.close()
        
@app.route("/pedidos_entrada/novo", methods=["GET", "POST"])
@login_obrigatorio
def novo_pedido_entrada():
    fornecedores = Fornecedor.find_all()
    produtos     = Produto.find_all()
    galpoes      = Galpao.find_all()

    if request.method == "POST":
        fornecedor_id    = to_int(request.form.get("fornecedor_id"))
        galpao_id        = to_int(request.form.get("galpao_id"))
        numero_documento = request.form.get("numero_documento")
        data_prevista    = request.form.get("data_entrada")   # campo "data_entrada" no form
        observacao       = request.form.get("observacao")

        produtos_form    = request.form.getlist("produto_id[]")
        quantidades_form = request.form.getlist("quantidade[]")
        valores_form     = request.form.getlist("valor_unitario[]")

        itens = []
        for i in range(len(produtos_form)):
            if produtos_form[i] and quantidades_form[i]:
                itens.append({
                    "produto_id":    to_int(produtos_form[i]),
                    "quantidade":    to_float(quantidades_form[i]),
                    "preco_unitario": to_float(valores_form[i]) if i < len(valores_form) else 0.0
                })

        if not itens:
            flash("Adicione pelo menos um item ao pedido.", "erro")
            return redirect(url_for("novo_pedido_entrada"))

        conn = Database.connect()
        cursor = conn.cursor()
        try:
            valor_total = sum(i["quantidade"] * i["preco_unitario"] for i in itens)

            cursor.execute("""
                INSERT INTO pedido_fornecedor
                    (fornecedor_id, galpao_id, numero_documento,
                     data_prevista, observacao, status, valor_total)
                VALUES (%s, %s, %s, %s, %s, 'recebido', %s)
            """, (fornecedor_id, galpao_id, numero_documento,
                  data_prevista, observacao, valor_total))
            pedido_id = cursor.lastrowid

            for item in itens:
                cursor.execute("""
                    INSERT INTO item_pedido_fornecedor
                        (pedido_fornecedor_id, produto_id, quantidade, preco_unitario)
                    VALUES (%s, %s, %s, %s)
                """, (pedido_id, item["produto_id"],
                      item["quantidade"], item["preco_unitario"]))

                # Incrementa o estoque automaticamente
                cursor.execute("""
                    INSERT INTO estoque (produto_id, galpao_id, quantidade, estoque_minimo)
                    VALUES (%s, %s, %s, 0)
                    ON DUPLICATE KEY UPDATE quantidade = quantidade + VALUES(quantidade)
                """, (item["produto_id"], galpao_id, item["quantidade"]))

            conn.commit()
            flash("Pedido de entrada cadastrado com sucesso!", "sucesso")
            return redirect(url_for("listar_pedidos_entrada"))

        except Exception as e:
            conn.rollback()
            flash(f"Erro ao cadastrar pedido de entrada: {e}", "erro")
        finally:
            cursor.close()
            conn.close()

    return render_template(
        "pedidos_entrada/form.html",
        fornecedores=fornecedores,
        produtos=produtos,
        galpoes=galpoes
    )


@app.route("/pedidos_entrada/visualizar/<int:pedido_id>")
@login_obrigatorio
def visualizar_pedido_entrada(pedido_id):
    conn = Database.connect()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT pf.*, f.nome AS fornecedor_nome, g.nome AS galpao_nome
            FROM pedido_fornecedor pf
            LEFT JOIN fornecedor f ON pf.fornecedor_id = f.id
            LEFT JOIN galpao     g ON pf.galpao_id     = g.id
            WHERE pf.id = %s
        """, (pedido_id,))
        pedido = cursor.fetchone()

        if not pedido:
            flash("Pedido não encontrado.", "erro")
            return redirect(url_for("listar_pedidos_entrada"))

        cursor.execute("""
            SELECT ipf.*, p.nome AS produto_nome, p.sku
            FROM item_pedido_fornecedor ipf
            JOIN produto p ON ipf.produto_id = p.id
            WHERE ipf.pedido_fornecedor_id = %s
        """, (pedido_id,))
        pedido["itens"] = cursor.fetchall()

    finally:
        cursor.close()
        conn.close()

    return render_template("pedidos_entrada/visualizar.html", pedido=pedido)


# ------------------------------------------------------------------ #
# PEDIDOS DE SAÍDA  (usa tabela: pedido_cliente)                      #
# ------------------------------------------------------------------ #

@app.route("/cadastro_pedido_saida")
@login_obrigatorio
def cadastro_pedido_saida():
    return render_template(
        "cadastro_pedidos.html",
        galpoes=Galpao.find_all(),
        clientes=Cliente.find_all()
    )


@app.route("/pedidos_saida")
@login_obrigatorio
def listar_pedidos_saida():
    conn = Database.connect()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT pc.*, c.nome AS cliente_nome, g.nome AS galpao_nome
            FROM pedido_cliente pc
            LEFT JOIN cliente c ON pc.cliente_id = c.id
            LEFT JOIN galpao  g ON pc.galpao_id  = g.id
            WHERE pc.galpao_id IS NOT NULL
            ORDER BY pc.data_pedido DESC
        """)
        pedidos = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
    return render_template(
    "cliente.html",
    cliente=c,
    pedidos=pedidos,
    galpoes=galpoes,
    produtos=lista_produtos
)


@app.route("/salvar_pedido_saida", methods=["POST"])
@login_obrigatorio
def salvar_pedido_saida():
    cliente_id       = to_int(request.form.get("cliente_id"))
    galpao_id        = to_int(request.form.get("galpao_id"))
    numero_documento = request.form.get("numero_documento")
    data_saida       = request.form.get("data_saida")
    observacao       = request.form.get("observacao")

    try:
        itens = json.loads(request.form.get("itens_json", "[]"))
    except Exception:
        itens = []

    if not itens:
        flash("Adicione pelo menos um item ao pedido.", "erro")
        return redirect(url_for("cadastro_pedido", cliente_id=cliente_id))

    valor_total = sum(i["quantidade"] * i["preco_unitario"] for i in itens)

    conn = Database.connect()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO pedido_cliente
                    (cliente_id, galpao_id, numero_documento, data_pedido,
                    observacao, valor_total, status_pedido)
                VALUES (%s, %s, %s, %s, %s, %s, 'pendente')
            """, (cliente_id, galpao_id, numero_documento, data_saida, observacao, valor_total))
        pedido_id = cursor.lastrowid

        for item in itens:
            cursor.execute("""
                INSERT INTO item_pedido_cliente
                    (pedido_cliente_id, produto_id, quantidade, preco_unitario_no_momento)
                VALUES (%s, %s, %s, %s)
            """, (pedido_id, item["produto_id"],
                  item["quantidade"], item["preco_unitario"]))

            cursor.execute("""
                UPDATE estoque SET quantidade = quantidade - %s
                WHERE produto_id = %s AND galpao_id = %s
            """, (item["quantidade"], item["produto_id"], galpao_id))

        conn.commit()
        flash("Pedido de saída cadastrado com sucesso!", "sucesso")
        return redirect(url_for("pedidos_clientes", cliente_id=cliente_id))

    except Exception as e:
        conn.rollback()
        flash(f"Erro ao cadastrar pedido de saída: {e}", "erro")
        return redirect(url_for("cadastro_pedido", cliente_id=cliente_id))
    finally:
        cursor.close()
        conn.close()


@app.route("/pedidos_saida/visualizar/<int:pedido_id>")
@login_obrigatorio
def visualizar_pedido_saida(pedido_id):
    conn = Database.connect()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT pc.*, c.nome AS cliente_nome, g.nome AS galpao_nome
            FROM pedido_cliente pc
            LEFT JOIN cliente c ON pc.cliente_id = c.id
            LEFT JOIN galpao  g ON pc.galpao_id  = g.id
            WHERE pc.id = %s
        """, (pedido_id,))
        pedido = cursor.fetchone()

        if not pedido:
            flash("Pedido não encontrado.", "erro")
            return redirect(url_for("listar_pedidos_saida"))

        cursor.execute("""
            SELECT ipc.*, p.nome AS produto_nome, p.sku
            FROM item_pedido_cliente ipc
            JOIN produto p ON ipc.produto_id = p.id
            WHERE ipc.pedido_cliente_id = %s
        """, (pedido_id,))
        pedido["itens"] = cursor.fetchall()

    finally:
        cursor.close()
        conn.close()

    return render_template("pedidos_saida/visualizar.html", pedido=pedido)

@app.route("/editar_pedido/<int:id>")
@login_obrigatorio
def editar_pedido(id):
    # buscar pedido + itens, renderizar formulário de edição
    pass

@app.route("/deletar_pedido/<int:id>")
@login_obrigatorio
def deletar_pedido(id):
    conn = Database.connect()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM item_pedido_fornecedor WHERE pedido_fornecedor_id = %s", (id,))
        cursor.execute("DELETE FROM pedido_fornecedor WHERE id = %s", (id,))
        conn.commit()
        flash("Pedido excluído com sucesso!", "sucesso")
    except Exception as e:
        conn.rollback()
        flash(f"Erro ao excluir pedido: {e}", "erro")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for("listar_pedidos_entrada"))

# ---------------- PEDIDOS CLIENTES ---------------- #

@app.route("/pedidos_cliente/<int:cliente_id>")
@login_obrigatorio
def pedidos_clientes(cliente_id):
    conexao = Database.connect()
    cursor = conexao.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM cliente WHERE id = %s", (cliente_id,))
        c = cursor.fetchone()

        if not c:
            flash("Cliente não encontrado.", "erro")
            return redirect(url_for("cliente"))

        cursor.execute("""
            SELECT pc.*, c.nome AS cliente_nome, c.email AS cliente_email
            FROM pedido_cliente pc
            JOIN cliente c ON pc.cliente_id = c.id
            WHERE pc.cliente_id = %s
            ORDER BY pc.data_pedido DESC
        """, (cliente_id,))
        pedidos = cursor.fetchall()

        galpoes = Galpao.find_all()
        lista_produtos = Produto.find_all()

        return render_template(
            "pedidos_cliente.html",
            cliente=c,
            pedidos=pedidos,
            galpoes=galpoes,
            produtos=lista_produtos
        )
    except Exception as e:
        print("ERRO REAL:", e)
        flash(f"Erro ao carregar pedidos do cliente: {e}", "erro")
        return redirect(url_for("cliente"))
    finally:
        cursor.close()
        conexao.close()
        
# ---------------- INFO PEDIDOS ------------#

@app.route("/pedido-cliente/<int:pedido_id>")
def info_pedido_cliente(pedido_id):

    conexao = Database.connect()
    cursor = conexao.cursor(dictionary=True)

    try:
        # Dados do pedido
        sql = """
            SELECT
                pc.*,
                c.nome AS cliente_nome,
                c.email AS cliente_email,
                c.telefone AS cliente_telefone,
                c.cidade,
                c.estado,
                g.nome AS galpao_nome
            FROM pedido_cliente pc
            LEFT JOIN cliente c
                ON pc.cliente_id = c.id
            LEFT JOIN galpao g
                ON pc.galpao_id = g.id
            WHERE pc.id = %s
        """

        cursor.execute(sql, (pedido_id,))
        pedido = cursor.fetchone()

        if not pedido:
            flash("Pedido não encontrado.", "danger")
            return redirect(url_for("clientes"))

        # Itens do pedido
        sql_itens = """
            SELECT
                ipc.*,
                p.nome,
                p.sku,
                p.codigo_barras
            FROM item_pedido_cliente ipc
            INNER JOIN produto p
                ON ipc.produto_id = p.id
            WHERE ipc.pedido_cliente_id = %s
        """

        cursor.execute(sql_itens, (pedido_id,))
        itens = cursor.fetchall()

        return render_template(
            "info_pedido_cliente.html",
            pedido=pedido,
            itens=itens
        )

    except Exception as e:
        flash(f"Erro ao carregar pedido: {e}", "danger")
        return redirect(url_for("pedidos_clientes"))

    finally:
        cursor.close()
        conexao.close()
# ---------------- PEDIDOS ---------------- #

@app.route("/pedidos")
@login_obrigatorio
def pedidos():
    conn = Database.connect()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT pf.*, f.nome AS fornecedor_nome, g.nome AS galpao_nome
            FROM pedido_fornecedor pf
            LEFT JOIN fornecedor f ON pf.fornecedor_id = f.id
            LEFT JOIN galpao     g ON pf.galpao_id     = g.id
            ORDER BY pf.id DESC
        """)
        pedidos = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    return render_template(
        "pedidos.html",
        pedidos=pedidos,
        galpoes=Galpao.find_all(),
        fornecedores=Fornecedor.find_all(),
        produtos=Produto.find_all()
    )

@app.route("/pedido/salvar", methods=["POST"])
@login_obrigatorio
def salvar_pedido():
    dados = {
        "produto_id": to_int(request.form.get("produto_id")),
        "tipo": request.form.get("tipo").upper(),
        "quantidade": to_int(request.form.get("quantidade")),
        "observacao": request.form.get("observacao")
    }
    try:
        PedidoCliente.create(dados)
        flash("Pedido criado com sucesso!", "sucesso")
        return redirect(url_for("pedidos"))
    except Exception as e:
        flash(f"Erro ao criar pedido: {e}", "erro")
        return redirect(url_for("produtos"))

@app.route("/pedido/processar/<int:id>")
@login_obrigatorio
def processar_pedido(id):
    try:
        PedidoCliente.processar(id)
        flash("Pedido processado com sucesso!", "sucesso")
    except Exception as e:
        flash(f"Erro ao processar pedido: {e}", "erro")
    return redirect(url_for("pedidos"))

@app.route("/pedido/cancelar/<int:id>")
@login_obrigatorio
def cancelar_pedido(id):
    try:
        PedidoCliente.cancelar(id)
        flash("Pedido cancelado com sucesso!", "sucesso")
    except Exception as e:
        flash(f"Erro ao cancelar pedido: {e}", "erro")
    return redirect(url_for("pedidos"))

# ---------------- RUN ---------------- #

if __name__ == "__main__":
    app.run(debug=True)
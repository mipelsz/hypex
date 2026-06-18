from core.database import Database
from werkzeug.security import generate_password_hash

# ===== DADOS DA EMPRESA =====
nome_empresa = "Imbil"
cnpj = "00.000.000/0002-00"

# ===== DADOS DO USUÁRIO =====
nome_usuario = "Miguel Rodrigues"
cpf = "321.654.321-00"
email = "contato@imbil.com"
telefone = "11999999999"
data_nascimento = "1990-02-02"
senha = generate_password_hash("654321")

conexao = Database.connect()
cursor = conexao.cursor()


try:
    sql_empresa = """
    INSERT INTO empresa (nome, cnpj)
    VALUES (%s, %s)
    """
    cursor.execute(sql_empresa, (nome_empresa, cnpj))
    empresa_id = cursor.lastrowid

    sql_usuario = """
    INSERT INTO usuario (nome, cpf, data_nascimento, email, telefone, senha, empresa_id)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(sql_usuario, (
        nome_usuario,
        cpf,
        data_nascimento,
        email,
        telefone,
        senha,
        empresa_id
    ))

    conexao.commit()
    print("✅ Empresa e usuário cadastrados com sucesso!")

    print("\n LOGIN PARA ENVIAR AO CLIENTE:")
    print("Email:", email)
    print("Senha: 654321")

except Exception as e:
    print("Erro ao cadastrar:", e)

finally:
    cursor.close()
    conexao.close()
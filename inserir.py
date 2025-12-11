import mysql.connector


def insert_funcionarios(dados):
    cursor = None
    conn = None

    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='banco_projeto'
        )

        cursor = conn.cursor()

        sql = (
            "INSERT INTO funcionarios (nome, senha, email, cep, cpf, telefone, data_nasc, data_entrada) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        )

        valores = (
            dados['nome'],
            dados['senha'],
            dados['email'],
            dados['cep'],
            dados['cpf'],
            dados['telefone'],
            dados['data_nasc'],
            dados['data_entrada']
        )

        cursor.execute(sql, valores)
        conn.commit()

        return {'status': 'sucesso', 'mensagem': 'Funcionário cadastrado!'}

    except mysql.connector.Error as err:
        return {'status': 'erro', 'mensagem': f"Erro ao cadastrar funcionário: {err}"}

    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()

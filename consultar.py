import mysql.connector
from conectar import connect_db

def read_funcionarios():
    conn = connect_db()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM funcionario")
            resultados = cursor.fetchall()
            return {'status': 'sucesso', 'dados': resultados}
        except mysql.connector.Error as err:
            return {'status': 'erro', 'mensagem': f'Erro ao listar funcionários: {err}'}
        finally:
            cursor.close()
            conn.close()

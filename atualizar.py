import mysql.connector
from conectar import connect_db

def update_funcionarios(dados):
    conn = connect_db()
    if conn:
        try:
            cursor = conn.cursor()
            sql = "UPDATE funcionario SET telefone = %s WHERE funcionario_id = %s"
            values = (dados['telefone'], dados['funcionario_id'])

            cursor.execute(sql, values)
            conn.commit()

            return {
                'status': 'sucesso',
                'mensagem': f"Funcionário {dados['funcionario_id']} atualizado com sucesso"
            }

        except mysql.connector.Error as err:
            return {'status': 'erro', 'mensagem': f"Erro ao atualizar funcionário: {err}"}
        finally:
            cursor.close()
            conn.close()
    
from core.database import Database
from core.empresa import empresa_atual
 
 
class Funcionario:
 
    # Inicializa os dados do funcionário.
    def __init__(self, nome, cpf, salario, data_nascimento, data_admissao, email, telefone, cargo, galpao_id, ativo):
        self.nome = nome
        self.cpf = cpf
        self.salario = salario
        self.data_nascimento = data_nascimento
        self.data_admissao = data_admissao
        self.email = email
        self.telefone = telefone
        self.cargo = cargo
        self.galpao_id = galpao_id
        self.ativo = ativo
 
    # Cadastra um novo funcionário.
    def insert(self):
        conn = Database.connect()
        cursor = conn.cursor()
 
        cursor.execute("""
            INSERT INTO funcionario
            (empresa_id, nome, cpf, salario, data_nascimento, data_admissao, ativo, email, telefone, cargo, galpao_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            empresa_atual(),
            self.nome,
            self.cpf,
            self.salario,
            self.data_nascimento,
            self.data_admissao,
            self.ativo,
            self.email,
            self.telefone,
            self.cargo,
            self.galpao_id
        ))
        conn.commit()
        conn.close()
 
    # Busca os funcionários de um galpão.
    @staticmethod
    def find_by_galpao(galpao_id):
        conn = Database.connect()
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute("""
                SELECT
                    f.*,
                    TRIM(CONCAT(COALESCE(e.marca, ''), ' ', COALESCE(e.modelo, ''))) AS empilhadeira,
                    e.id AS empilhadeira_id
                FROM funcionario f
                LEFT JOIN empilhadeira e ON e.funcionario_id = f.id
                WHERE f.galpao_id = %s
                ORDER BY f.nome
            """, (galpao_id,))

            return cursor.fetchall()

        finally:
            cursor.close()
            conn.close()

    # Lista todos os funcionários da empresa.
    @staticmethod
    def find_all():
        conn = Database.connect()
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute("""
                SELECT f.*, g.nome AS galpao_nome
                FROM funcionario f
                LEFT JOIN galpao g ON f.galpao_id = g.id
                WHERE f.empresa_id = %s
                ORDER BY f.nome
            """, (empresa_atual(),))
            return cursor.fetchall()

        finally:
            cursor.close()
            conn.close()
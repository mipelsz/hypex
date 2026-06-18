from core.database import Database
 
 
class Funcionario:
 
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
 
    def insert(self):
        conn = Database.connect()
        cursor = conn.cursor()
 
        cursor.execute("""
            INSERT INTO funcionario
            (nome, cpf, salario, data_nascimento, data_admissao, ativo, email, telefone, cargo, galpao_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
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
 
    @staticmethod
    def find_by_galpao(galpao_id):
        conn = Database.connect()
        cursor = conn.cursor(dictionary=True)
 
        cursor.execute("""
            SELECT * FROM funcionario
            WHERE galpao_id = %s
        """, (galpao_id,))
 
        dados = cursor.fetchall()
        conn.close()
 
        return dados
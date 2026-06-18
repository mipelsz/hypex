from core.database import Database
 
 
class Empilhadeira:
 
    def __init__(self, marca, modelo, ano_fabricacao, tipo_combustivel, capacidade, galpao_id, ativo):
        self.marca = marca
        self.modelo = modelo
        self.ano_fabricacao = ano_fabricacao
        self.tipo_combustivel = tipo_combustivel
        self.capacidade = capacidade
        self.galpao_id = galpao_id
        self.ativo = ativo
 
    def insert(self):
        conn = Database.connect()
        cursor = conn.cursor()
 
        cursor.execute("""
            INSERT INTO empilhadeira
            (marca, modelo, ano_fabricacao, tipo_combustivel, capacidade, galpao_id, ativo)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            self.marca,
            self.modelo,
            self.ano_fabricacao,
            self.tipo_combustivel,
            self.capacidade,
            self.galpao_id,
            self.ativo
        ))
 
        conn.commit()
        conn.close()
 
    @staticmethod
    def find_by_galpao(galpao_id):
        conn = Database.connect()
        cursor = conn.cursor(dictionary=True)
 
        cursor.execute("""
            SELECT * FROM empilhadeira
            WHERE galpao_id = %s
        """, (galpao_id,))
 
        dados = cursor.fetchall()  # FIX: era "return dadosfrom" — typo que colava o próximo arquivo
        conn.close()
 
        return dados
from core.database import Database


class Fornecedor:

    def __init__(self, nome, telefone, email, ativo, cnpj, nome_ctt):
        self.nome = nome
        self.cnpj = cnpj
        self.nome_ctt = nome_ctt
        self.ativo = ativo
        self.telefone = telefone
        self.email = email

    def insert(self):
        conn = Database.connect()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO fornecedor (nome, telefone, email, ativo, cnpj, nome_ctt) VALUES (%s,%s,%s,%s,%s,%s)",
                (self.nome, self.telefone, self.email, self.ativo, self.cnpj, self.nome_ctt)
            )
            conn.commit()
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def find_all():
        conn = Database.connect()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM fornecedor ORDER BY nome ASC")
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def find_by_id(fornecedor_id):
        conn = Database.connect()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM fornecedor WHERE id = %s", (fornecedor_id,))
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def find_produtos(fornecedor_id):
        conn = Database.connect()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT
                    p.id, p.nome, p.sku, p.categoria,
                    fp.preco_custo, fp.desconto,
                    fp.quantidade_minima, fp.prazo_entrega_dias, fp.ativo
                FROM fornecedor_produto fp
                JOIN produto p ON fp.produto_id = p.id
                WHERE fp.fornecedor_id = %s
                ORDER BY p.nome ASC
            """, (fornecedor_id,))
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()
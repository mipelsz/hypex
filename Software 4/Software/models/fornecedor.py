from core.database import Database
from core.empresa import empresa_atual


class Fornecedor:

    # Inicializa os dados do fornecedor.
    def __init__(self, nome, telefone, email, ativo, cnpj, nome_ctt):
        self.nome = nome
        self.cnpj = cnpj
        self.nome_ctt = nome_ctt
        self.ativo = ativo
        self.telefone = telefone
        self.email = email

    # Cadastra um novo fornecedor.
    def insert(self):
        conn = Database.connect()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO fornecedor (empresa_id, nome, telefone, email, ativo, cnpj, nome_ctt) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s)",
                (empresa_atual(), self.nome, self.telefone, self.email, self.ativo, self.cnpj, self.nome_ctt)
            )
            conn.commit()
        finally:
            cursor.close()
            conn.close()

    # Lista todos os fornecedores da empresa.
    @staticmethod
    def find_all():
        conn = Database.connect()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM fornecedor WHERE empresa_id = %s ORDER BY nome ASC",
                           (empresa_atual(),))
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    # Busca um fornecedor pelo ID.
    @staticmethod
    def find_by_id(fornecedor_id):
        conn = Database.connect()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM fornecedor WHERE id = %s AND empresa_id = %s",
                           (fornecedor_id, empresa_atual()))
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

    # Lista os produtos de um fornecedor.
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
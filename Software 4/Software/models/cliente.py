from core.database import Database


class Cliente:

    def __init__(self, nome, empresa, ativo, cidade, estado,
                 cpf_cnpj, cep, email, telefone):
        self.nome = nome
        self.empresa = empresa
        self.ativo = ativo
        self.cidade = cidade
        self.estado = estado
        self.cpf_cnpj = cpf_cnpj
        self.cep = cep
        self.email = email
        self.telefone = telefone

    def insert(self):
        conn = Database.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO cliente
                (nome, empresa, ativo, cidade, estado, cpf_cnpj, cep, email, telefone)
                VALUES (%s, %s, %s,%s, %s, %s, %s, %s, %s)
            """, (
                self.nome, self.empresa, self.ativo, self.cidade, self.estado,
                self.cpf_cnpj, self.cep, self.email, self.telefone
            ))
            conn.commit()
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def find_all():
        conn = Database.connect()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM cliente")
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def find_by_id(id):
        conn = Database.connect()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM cliente WHERE id = %s", (id,))
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def update(cliente_id, dados):
        conn = Database.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE cliente SET
                    nome = %s,
                    empresa = %s,
                    email = %s,
                    telefone = %s,
                    cep = %s,
                    cidade = %s,
                    estado = %s,
                    ativo = %s
                WHERE id = %s
            """, (
                dados["nome"], dados["empresa"], dados["email"],
                dados["telefone"], dados["cep"], dados["cidade"],
                dados["estado"], dados["ativo"], cliente_id
            ))
            conn.commit()
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def delete(cliente_id):
        conn = Database.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM cliente WHERE id = %s", (cliente_id,))
            conn.commit()
        finally:
            cursor.close()
            conn.close()
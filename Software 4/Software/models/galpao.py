from core.database import Database


class Galpao:

    def __init__(self, nome, stats, email_resp, nome_resp, endereco, referencia, cidade, estado, area_total, telefone, cep,
                 total_prateleiras, niveis_por_prateleira, caixas_por_nivel, capacidade_total):
        self.nome = nome
        self.stats = stats
        self.email_resp = email_resp
        self.nome_resp = nome_resp
        self.endereco = endereco
        self.referencia = referencia
        self.cidade = cidade
        self.estado = estado
        self.area_total = area_total
        self.telefone = telefone
        self.cep = cep
        self.total_prateleiras = total_prateleiras
        self.niveis_por_prateleira = niveis_por_prateleira
        self.caixas_por_nivel = caixas_por_nivel
        self.capacidade_total = capacidade_total

    def insert(self):
        conn = Database.connect()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO galpao 
            (nome, stats, email_resp, nome_resp, endereco, referencia, cidade, estado, area_total, telefone, cep, total_prateleiras, niveis_por_prateleira, caixas_por_nivel, capacidade_total)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            self.nome, self.stats, self.email_resp, self.nome_resp,
            self.endereco, self.referencia, self.cidade, self.estado,
            self.area_total, self.telefone, self.cep, self.total_prateleiras,
            self.niveis_por_prateleira, self.caixas_por_nivel, self.capacidade_total
        ))
        conn.commit()
        conn.close()

    @staticmethod
    def find_all():
        conn = Database.connect()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                g.*,

                COALESCE(SUM(e.quantidade), 0) AS total_produtos,

                CASE
                    WHEN g.capacidade_total > 0 THEN
                        ROUND(
                            (COALESCE(SUM(e.quantidade), 0) / g.capacidade_total) * 100,
                            0
                        )
                    ELSE 0
                END AS ocupacao

            FROM galpao g
            LEFT JOIN estoque e
                ON e.galpao_id = g.id

            GROUP BY g.id
            ORDER BY g.nome
        """)

        result = cursor.fetchall()

        cursor.close()
        conn.close()

        return result

    @staticmethod
    def find_by_id(id):
        conn = Database.connect()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM galpao WHERE id = %s", (id,))
        galpao = cursor.fetchone()
        cursor.close() 
        conn.close()
        return galpao

    @staticmethod
    def update(galpao_id, dados):
        conn = Database.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE galpao SET
                    nome_resp             = %s,
                    email_resp            = %s,
                    telefone              = %s,
                    stats                 = %s,
                    nome                  = %s,
                    cep                   = %s,
                    endereco              = %s,
                    referencia            = %s,
                    area_total            = %s,
                    caixas_por_nivel      = %s,
                    niveis_por_prateleira = %s,
                    total_prateleiras     = %s,
                    capacidade_total      = %s
                WHERE id = %s
            """, (
                dados["nome_resp"], dados["email_resp"], dados["telefone"],
                dados["stats"],    dados["nome"],        dados["cep"],
                dados["endereco"], dados["referencia"],  dados["area_total"],
                dados["caixas_por_nivel"], dados["niveis_por_prateleira"],
                dados["total_prateleiras"], dados["capacidade_total"],
                galpao_id
            ))
            conn.commit()
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def delete(galpao_id):
        conn = Database.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM galpao WHERE id = %s", (galpao_id,))
            conn.commit()
        finally:
            cursor.close()
            conn.close()
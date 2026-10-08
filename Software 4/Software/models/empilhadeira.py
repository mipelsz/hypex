from core.database import Database 
from core.empresa import empresa_atual 
 
 
class Empilhadeira: 
 
    # Inicializa os dados da empilhadeira.
    def __init__(self, marca, modelo, ano_fabricacao, tipo_combustivel, 
                 capacidade, galpao_id, ativo, funcionario_id=None): 
        self.marca = marca 
        self.modelo = modelo 
        self.ano_fabricacao = ano_fabricacao 
        self.tipo_combustivel = tipo_combustivel 
        self.capacidade = capacidade 
        self.galpao_id = galpao_id 
        self.funcionario_id = funcionario_id or None 
        self.ativo = ativo 
 
    # Cadastra uma nova empilhadeira.
    def insert(self): 
        conn = Database.connect() 
        cursor = conn.cursor() 
        try: 
            cursor.execute(""" 
                INSERT INTO empilhadeira 
                    (empresa_id, marca, modelo, ano_fabricacao, tipo_combustivel, 
                     capacidade, galpao_id, funcionario_id, ativo) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) 
            """, ( 
                empresa_atual(), 
                self.marca, 
                self.modelo, 
                self.ano_fabricacao, 
                self.tipo_combustivel, 
                self.capacidade, 
                self.galpao_id, 
                self.funcionario_id, 
                self.ativo 
            )) 
 
            conn.commit() 
            return cursor.lastrowid 
 
        except Exception: 
            conn.rollback() 
            raise 
 
        finally: 
            cursor.close() 
            conn.close() 

    # Busca as empilhadeiras de um galpão.
    @staticmethod 
    def find_by_galpao(galpao_id): 
        conn = Database.connect() 
        cursor = conn.cursor(dictionary=True) 
        try: 
            cursor.execute(""" 
                SELECT e.*, f.nome AS funcionario_nome 
                FROM empilhadeira e 
                LEFT JOIN funcionario f ON f.id = e.funcionario_id 
                WHERE e.galpao_id = %s 
                ORDER BY e.marca, e.modelo 
            """, (galpao_id,)) 
            return cursor.fetchall() 
 
        finally: 
            cursor.close() 
            conn.close() 
 
    # Atualiza os dados da empilhadeira.
    @staticmethod 
    def update(empilhadeira_id, dados): 
        conn = Database.connect() 
        cursor = conn.cursor() 
        try: 
            cursor.execute(""" 
                UPDATE empilhadeira SET 
                    marca            = %s, 
                    modelo           = %s, 
                    ano_fabricacao   = %s, 
                    tipo_combustivel = %s, 
                    capacidade       = %s, 
                    funcionario_id   = %s, 
                    ativo            = %s 
                WHERE id = %s 
            """, ( 
                dados.get("marca"), 
                dados.get("modelo"), 
                dados.get("ano_fabricacao"), 
                dados.get("tipo_combustivel"), 
                dados.get("capacidade"), 
                dados.get("funcionario_id") or None, 
                dados.get("ativo"), 
                empilhadeira_id 
            )) 
 
            conn.commit() 
            return cursor.rowcount 
 
        except Exception: 
            conn.rollback() 
            raise 
 
        finally: 
            cursor.close() 
            conn.close() 
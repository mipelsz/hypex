from core.database import Database


# Classe responsável por representar e manipular endereços no banco de dados
class Endereco:

    # Construtor da classe Endereco
    # Inicializa os atributos principais do endereço
    def __init__(self, rua, cidade, estado, cep):
        self.rua = rua
        self.cidade = cidade
        self.estado = estado
        self.cep = cep


    # Insere um novo endereço no banco de dados
    def insert(self):
        conn = Database.connect()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO endereco (rua, cidade, estado, cep) VALUES (%s,%s,%s,%s)",
            (self.rua, self.cidade, self.estado, self.cep)
        )

        conn.commit()
        conn.close()


    # Busca e retorna todos os endereços cadastrados
    @staticmethod
    def find_all():
        conn = Database.connect()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM endereco")
        return cursor.fetchall()
from core.database import Database

class CrudBase:
    table = ""
    fields = []

    @classmethod
    def find_all(cls, order_by="id"):
        conexao = Database.connect()
        cursor = conexao.cursor(dictionary=True)
        try:
            sql = f"SELECT * FROM {cls.table} ORDER BY {order_by}"
            cursor.execute(sql)
            return cursor.fetchall()
        finally:
            cursor.close()
            conexao.close()

    @classmethod
    def find_by_id(cls, id):
        conexao = Database.connect()
        cursor = conexao.cursor(dictionary=True)
        try:
            sql = f"SELECT * FROM {cls.table} WHERE id = %s"
            cursor.execute(sql, (id,))
            return cursor.fetchone()
        finally:
            cursor.close()
            conexao.close()

    @classmethod
    def delete(cls, id):
        conexao = Database.connect()
        cursor = conexao.cursor()
        try:
            sql = f"DELETE FROM {cls.table} WHERE id = %s"
            cursor.execute(sql, (id,))
            conexao.commit()
            return cursor.rowcount
        except Exception:
            conexao.rollback()
            raise
        finally:
            cursor.close()
            conexao.close()

    def insert(self):
        conexao = Database.connect()
        cursor = conexao.cursor()
        try:
            colunas = ", ".join(self.fields)
            marcadores = ", ".join(["%s"] * len(self.fields))
            valores = tuple(getattr(self, campo) for campo in self.fields)
            sql = f"INSERT INTO {self.table} ({colunas}) VALUES ({marcadores})"
            cursor.execute(sql, valores)
            conexao.commit()
            return cursor.lastrowid
        except Exception:
            conexao.rollback()
            raise
        finally:
            cursor.close()
            conexao.close()

    def update(self, id):
        conexao = Database.connect()
        cursor = conexao.cursor()
        try:
            campos = ", ".join([f"{campo} = %s" for campo in self.fields])
            valores = tuple(getattr(self, campo) for campo in self.fields) + (id,)
            sql = f"UPDATE {self.table} SET {campos} WHERE id = %s"
            cursor.execute(sql, valores)
            conexao.commit()
            return cursor.rowcount
        except Exception:
            conexao.rollback()
            raise
        finally:
            cursor.close()
            conexao.close()

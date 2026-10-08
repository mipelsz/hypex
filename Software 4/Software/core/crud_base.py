from core.database import Database
from core.empresa import empresa_atual

class CrudBase:
    table = ""
    fields = []

    por_empresa = True

    @classmethod
    def _filtro_empresa(cls, prefixo=" WHERE"):
        if cls.por_empresa:
            return f"{prefixo} empresa_id = %s", (empresa_atual(),)
        return "", ()

    @classmethod
    def find_all(cls, order_by="id"):
        conexao = Database.connect()
        cursor = conexao.cursor(dictionary=True)
        try:
            filtro, valores = cls._filtro_empresa()
            sql = f"SELECT * FROM {cls.table}{filtro} ORDER BY {order_by}"
            cursor.execute(sql, valores)
            return cursor.fetchall()
        finally:
            cursor.close()
            conexao.close()

    @classmethod
    def find_by_id(cls, id):
        conexao = Database.connect()
        cursor = conexao.cursor(dictionary=True)
        try:
            filtro, valores = cls._filtro_empresa(" AND")
            sql = f"SELECT * FROM {cls.table} WHERE id = %s{filtro}"
            cursor.execute(sql, (id,) + valores)
            return cursor.fetchone()
        finally:
            cursor.close()
            conexao.close()

    @classmethod
    def delete(cls, id):
        conexao = Database.connect()
        cursor = conexao.cursor()
        try:
            filtro, valores = cls._filtro_empresa(" AND")
            sql = f"DELETE FROM {cls.table} WHERE id = %s{filtro}"
            cursor.execute(sql, (id,) + valores)
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
            campos = list(self.fields)
            valores = [getattr(self, campo) for campo in self.fields]
            if self.por_empresa and "empresa_id" not in campos:
                campos.insert(0, "empresa_id")
                valores.insert(0, empresa_atual())
            colunas = ", ".join(campos)
            marcadores = ", ".join(["%s"] * len(campos))
            sql = f"INSERT INTO {self.table} ({colunas}) VALUES ({marcadores})"
            cursor.execute(sql, tuple(valores))
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
            filtro, extra = self._filtro_empresa(" AND")
            valores = tuple(getattr(self, campo) for campo in self.fields) + (id,) + extra
            sql = f"UPDATE {self.table} SET {campos} WHERE id = %s{filtro}"
            cursor.execute(sql, valores)
            conexao.commit()
            return cursor.rowcount
        except Exception:
            conexao.rollback()
            raise
        finally:
            cursor.close()
            conexao.close()

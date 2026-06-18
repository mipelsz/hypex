from datetime import datetime
from core.crud_base import CrudBase
from core.database import Database


class PedidoCliente(CrudBase):

    table = "pedido_cliente"

    fields = [
        "cliente_id",
        "galpao_id",
        "valor_total",
        "status_pedido",
    ]

    def __init__(self, cliente_id, galpao_id, valor_total=0, status_pedido="pendente"):
        self.cliente_id = cliente_id
        self.galpao_id = galpao_id
        self.valor_total = valor_total
        self.status_pedido = status_pedido

    # ------------------------------------------------------------------
    # Cria pedido + itens em uma única transação
    # dados = {
    #   "cliente_id": int,
    #   "galpao_id":  int,
    #   "itens": [
    #       {"produto_id": int, "quantidade": float, "preco_unitario": float},
    #       ...
    #   ]
    # }
    # ------------------------------------------------------------------
    @classmethod
    def criar_com_itens(cls, dados):
        conexao = Database.connect()
        cursor = conexao.cursor()

        try:
            itens = dados.get("itens", [])
            if not itens:
                raise ValueError("O pedido deve ter pelo menos um item.")

            # Calcula o total somando todos os itens
            valor_total = sum(
                float(i["quantidade"]) * float(i["preco_unitario"])
                for i in itens
            )

            # 1. Insere o cabeçalho do pedido
            cursor.execute("""
                INSERT INTO pedido_cliente
                    (cliente_id, galpao_id, valor_total, status_pedido)
                VALUES (%s, %s, %s, 'pendente')
            """, (
                dados["cliente_id"],
                dados["galpao_id"],
                valor_total,
            ))
            pedido_id = cursor.lastrowid

            # 2. Insere cada item na tabela item_pedido_cliente
            for item in itens:
                cursor.execute("""
                    INSERT INTO item_pedido_cliente
                        (pedido_cliente_id, produto_id, quantidade, preco_unitario_no_momento)
                    VALUES (%s, %s, %s, %s)
                """, (
                    pedido_id,
                    item["produto_id"],
                    float(item["quantidade"]),
                    float(item["preco_unitario"]),
                ))

            # 3. Baixa o estoque de cada item no galpão escolhido
            galpao_id = dados["galpao_id"]
            for item in itens:
                cursor.execute("""
                    SELECT quantidade FROM estoque
                    WHERE produto_id = %s AND galpao_id = %s
                    FOR UPDATE
                """, (item["produto_id"], galpao_id))

                resultado = cursor.fetchone()
                if not resultado:
                    raise ValueError(
                        f"Produto {item['produto_id']} não encontrado no estoque do galpão."
                    )

                estoque_atual = resultado[0]
                nova_qtd = estoque_atual - float(item["quantidade"])

                if nova_qtd < 0:
                    raise ValueError(
                        f"Estoque insuficiente para o produto {item['produto_id']}. "
                        f"Disponível: {estoque_atual}, Solicitado: {item['quantidade']}."
                    )

                cursor.execute("""
                    UPDATE estoque SET quantidade = %s
                    WHERE produto_id = %s AND galpao_id = %s
                """, (nova_qtd, item["produto_id"], galpao_id))

            conexao.commit()
            return pedido_id

        except Exception:
            conexao.rollback()
            raise

        finally:
            cursor.close()
            conexao.close()

    # ------------------------------------------------------------------
    # Busca todos os pedidos de um cliente (para info_cliente.html)
    # ------------------------------------------------------------------
    @classmethod
    def find_by_cliente(cls, cliente_id):
        conexao = Database.connect()
        cursor = conexao.cursor(dictionary=True)

        try:
            cursor.execute("""
                SELECT
                    pc.*,
                    c.nome  AS cliente_nome,
                    c.email AS cliente_email
                FROM pedido_cliente pc
                JOIN cliente c ON pc.cliente_id = c.id
                WHERE pc.cliente_id = %s
                ORDER BY pc.data_pedido DESC
            """, (cliente_id,))

            return cursor.fetchall()

        finally:
            cursor.close()
            conexao.close()

    # ------------------------------------------------------------------
    # Lista geral de pedidos com todos os itens (para pedidos.html)
    # ------------------------------------------------------------------
    @classmethod
    def find_all_with_product(cls):
        conexao = Database.connect()
        cursor = conexao.cursor(dictionary=True)

        try:
            cursor.execute("""
                SELECT
                    pc.id,
                    pc.data_pedido,
                    pc.status_pedido,
                    pc.valor_total,
                    c.nome  AS cliente_nome,
                    p.nome  AS produto,
                    ip.quantidade,
                    ip.preco_unitario_no_momento
                FROM pedido_cliente pc
                JOIN cliente c              ON pc.cliente_id = c.id
                JOIN item_pedido_cliente ip ON pc.id = ip.pedido_cliente_id
                JOIN produto p              ON ip.produto_id = p.id
                ORDER BY pc.data_pedido DESC
            """)

            return cursor.fetchall()

        finally:
            cursor.close()
            conexao.close()

    # ------------------------------------------------------------------
    # Cancela um pedido pendente e devolve o estoque
    # ------------------------------------------------------------------
    @classmethod
    def cancelar(cls, pedido_id):
        conexao = Database.connect()
        cursor = conexao.cursor(dictionary=True)

        try:
            cursor.execute(
                "SELECT * FROM pedido_cliente WHERE id = %s", (pedido_id,)
            )
            pedido = cursor.fetchone()

            if not pedido:
                raise ValueError("Pedido não encontrado.")
            if pedido["status_pedido"] != "pendente":
                raise ValueError("Só é possível cancelar pedidos com status 'pendente'.")

            # Devolve o estoque
            cursor.execute("""
                SELECT produto_id, quantidade
                FROM item_pedido_cliente
                WHERE pedido_cliente_id = %s
            """, (pedido_id,))
            itens = cursor.fetchall()

            for item in itens:
                cursor.execute("""
                    UPDATE estoque SET quantidade = quantidade + %s
                    WHERE produto_id = %s AND galpao_id = %s
                """, (item["quantidade"], item["produto_id"], pedido["galpao_id"]))

            cursor.execute("""
                UPDATE pedido_cliente
                SET status_pedido = 'cancelado', updated_at = %s
                WHERE id = %s
            """, (datetime.now(), pedido_id))

            conexao.commit()

        except Exception:
            conexao.rollback()
            raise

        finally:
            cursor.close()
            conexao.close()
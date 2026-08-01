from werkzeug.security import check_password_hash, generate_password_hash

from database import get_db


def _product_from_row(row):
    return {
        "id": row["id"],
        "nome": row["nome"],
        "descricao": row["descricao"],
        "preco": row["preco"],
        "estoque": row["estoque"],
        "categoria": row["categoria"],
        "ativo": row["ativo"],
        "criado_em": row["criado_em"],
    }


def _user_from_row(row):
    return {
        "id": row["id"],
        "nome": row["nome"],
        "email": row["email"],
        "tipo": row["tipo"],
        "criado_em": row["criado_em"],
    }


def _load_orders(where_clause="", params=()):
    db = get_db()
    cursor = db.cursor()

    query = "SELECT * FROM pedidos"
    if where_clause:
        query += " " + where_clause
    cursor.execute(query, params)
    pedido_rows = cursor.fetchall()

    pedidos = []
    pedido_ids = [row["id"] for row in pedido_rows]
    itens_por_pedido = {pedido_id: [] for pedido_id in pedido_ids}

    if pedido_ids:
        placeholders = ",".join(["?"] * len(pedido_ids))
        cursor.execute(
            """
            SELECT
                ip.pedido_id,
                ip.produto_id,
                ip.quantidade,
                ip.preco_unitario,
                p.nome AS produto_nome
            FROM itens_pedido ip
            LEFT JOIN produtos p ON p.id = ip.produto_id
            WHERE ip.pedido_id IN ({})
            ORDER BY ip.id
            """.format(placeholders),
            pedido_ids,
        )
        for item in cursor.fetchall():
            itens_por_pedido[item["pedido_id"]].append(
                {
                    "produto_id": item["produto_id"],
                    "produto_nome": item["produto_nome"] or "Desconhecido",
                    "quantidade": item["quantidade"],
                    "preco_unitario": item["preco_unitario"],
                }
            )

    for row in pedido_rows:
        pedidos.append(
            {
                "id": row["id"],
                "usuario_id": row["usuario_id"],
                "status": row["status"],
                "total": row["total"],
                "criado_em": row["criado_em"],
                "itens": itens_por_pedido.get(row["id"], []),
            }
        )

    return pedidos


def get_todos_produtos():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM produtos")
    rows = cursor.fetchall()
    return [_product_from_row(row) for row in rows]


def get_produto_por_id(produto_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,))
    row = cursor.fetchone()
    if row:
        return _product_from_row(row)
    return None


def criar_produto(nome, descricao, preco, estoque, categoria):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        """
        INSERT INTO produtos (nome, descricao, preco, estoque, categoria)
        VALUES (?, ?, ?, ?, ?)
        """,
        (nome, descricao, preco, estoque, categoria),
    )
    db.commit()
    return cursor.lastrowid


def atualizar_produto(produto_id, nome, descricao, preco, estoque, categoria):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        """
        UPDATE produtos
        SET nome = ?, descricao = ?, preco = ?, estoque = ?, categoria = ?
        WHERE id = ?
        """,
        (nome, descricao, preco, estoque, categoria, produto_id),
    )
    db.commit()
    return True


def deletar_produto(produto_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
    db.commit()
    return True


def get_todos_usuarios():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM usuarios")
    rows = cursor.fetchall()
    return [_user_from_row(row) for row in rows]


def get_usuario_por_id(usuario_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,))
    row = cursor.fetchone()
    if row:
        return _user_from_row(row)
    return None


def login_usuario(email, senha):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
    row = cursor.fetchone()
    if row and check_password_hash(row["senha"], senha):
        return _user_from_row(row)
    return None


def criar_usuario(nome, email, senha, tipo="cliente"):
    db = get_db()
    cursor = db.cursor()
    senha_hash = generate_password_hash(senha)
    cursor.execute(
        """
        INSERT INTO usuarios (nome, email, senha, tipo)
        VALUES (?, ?, ?, ?)
        """,
        (nome, email, senha_hash, tipo),
    )
    db.commit()
    return cursor.lastrowid


def criar_pedido(usuario_id, itens):
    db = get_db()
    cursor = db.cursor()

    total = 0
    itens_detalhados = []

    try:
        for item in itens:
            produto_id = item["produto_id"]
            quantidade = item["quantidade"]

            cursor.execute(
                "SELECT id, nome, preco, estoque FROM produtos WHERE id = ?",
                (produto_id,),
            )
            produto = cursor.fetchone()
            if produto is None:
                return {"erro": "Produto " + str(produto_id) + " não encontrado"}
            if produto["estoque"] < quantidade:
                return {"erro": "Estoque insuficiente para " + produto["nome"]}

            total += produto["preco"] * quantidade
            itens_detalhados.append(
                {
                    "produto_id": produto["id"],
                    "quantidade": quantidade,
                    "preco_unitario": produto["preco"],
                }
            )

        cursor.execute(
            """
            INSERT INTO pedidos (usuario_id, status, total)
            VALUES (?, 'pendente', ?)
            """,
            (usuario_id, total),
        )
        pedido_id = cursor.lastrowid

        for item in itens_detalhados:
            cursor.execute(
                """
                INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario)
                VALUES (?, ?, ?, ?)
                """,
                (
                    pedido_id,
                    item["produto_id"],
                    item["quantidade"],
                    item["preco_unitario"],
                ),
            )
            cursor.execute(
                "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
                (item["quantidade"], item["produto_id"]),
            )

        db.commit()
        return {"pedido_id": pedido_id, "total": total}
    except Exception:
        db.rollback()
        raise


def get_pedidos_usuario(usuario_id):
    return _load_orders("WHERE usuario_id = ?", (usuario_id,))


def get_todos_pedidos():
    return _load_orders()


def relatorio_vendas():
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT COUNT(*) FROM pedidos")
    total_pedidos = cursor.fetchone()[0]

    cursor.execute("SELECT COALESCE(SUM(total), 0) FROM pedidos")
    faturamento = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM pedidos WHERE status = 'pendente'")
    pendentes = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM pedidos WHERE status = 'aprovado'")
    aprovados = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM pedidos WHERE status = 'cancelado'")
    cancelados = cursor.fetchone()[0]

    desconto = 0
    if faturamento > 10000:
        desconto = faturamento * 0.1
    elif faturamento > 5000:
        desconto = faturamento * 0.05
    elif faturamento > 1000:
        desconto = faturamento * 0.02

    return {
        "total_pedidos": total_pedidos,
        "faturamento_bruto": round(faturamento, 2),
        "desconto_aplicavel": round(desconto, 2),
        "faturamento_liquido": round(faturamento - desconto, 2),
        "pedidos_pendentes": pendentes,
        "pedidos_aprovados": aprovados,
        "pedidos_cancelados": cancelados,
        "ticket_medio": round(faturamento / total_pedidos, 2) if total_pedidos > 0 else 0,
    }


def atualizar_status_pedido(pedido_id, novo_status):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "UPDATE pedidos SET status = ? WHERE id = ?",
        (novo_status, pedido_id),
    )
    db.commit()
    return True


def buscar_produtos(termo, categoria=None, preco_min=None, preco_max=None):
    db = get_db()
    cursor = db.cursor()

    query = "SELECT * FROM produtos WHERE 1=1"
    params = []

    if termo:
        query += " AND (nome LIKE ? OR descricao LIKE ?)"
        termo_like = "%" + termo + "%"
        params.extend([termo_like, termo_like])
    if categoria:
        query += " AND categoria = ?"
        params.append(categoria)
    if preco_min is not None:
        query += " AND preco >= ?"
        params.append(preco_min)
    if preco_max is not None:
        query += " AND preco <= ?"
        params.append(preco_max)

    cursor.execute(query, params)
    rows = cursor.fetchall()
    return [_product_from_row(row) for row in rows]

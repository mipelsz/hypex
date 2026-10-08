from flask import session


def empresa_atual():
    return session.get("empresa_id")

from flask import redirect, url_for

def autenticar(username: str) -> None:
    global usuario
    usuario = username

    arquivo = open('data/usuario.txt', 'w')
    arquivo.write(fr'{username}')

def usuario_autenticado() -> str | None:
    arquivo = open('data/usuario.txt')
    linhas = arquivo.readlines()
    if linhas and linhas[0]:
        return linhas[0]
    return None

def validar_usuario(funcao):
    def vu_closure(*args):
        if usuario_autenticado() is None:
            return redirect(url_for('login'))
        return funcao(*args)
    return vu_closure
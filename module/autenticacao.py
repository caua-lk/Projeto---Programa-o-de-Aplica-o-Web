def autenticar(username: str) -> None:
    global usuario
    usuario = username

    arquivo = open('data/usuario.txt', 'w')
    arquivo.write(username)

def usuario_autenticado() -> str | None:
    arquivo = open('data/usuario.txt')
    linhas = arquivo.readlines()
    if not linhas[0]:
        return None
    return linhas[0]
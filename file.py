def usuario_autenticado() -> str | None:
    arquivo = open('data/usuario.txt')
    linhas = arquivo.readlines()
    if not linhas[0]:
        return None
    return linhas[0]

print(usuario_autenticado())
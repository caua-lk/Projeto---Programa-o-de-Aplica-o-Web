import sqlite3
def conexao():
    conexao = sqlite3.connect('bank.sql')
    conexao.row_factory = sqlite3.Row
    return conexao
def iniciar():
    conect = conexao()
    conect.execute("""
        CREATE TABLE IF NOT EXISTS User (
            id INTEGER PRIMARY KEY NOT NULL AUTOINCREMENT,
            nome TEXT NOT NULL,
            senha TEXT NOT NULL
        )
    """)
    conect.execute('''
        CREATE TABLE IF NOT EXISTS Tarefa (
        id INTEGER PRIMARY KEY NOT NULL AUTOINCREMENT,
        nome TEXTO NOT NULL,
        descricao TEXT NOT NULL,
        prazo TEXT,
        user_id INTEGER,
        FOREING KEY (user_id) REFERENCES User (id)
        )
    ''')
    conect.commit()
    conect.close()
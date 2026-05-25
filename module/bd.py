import sqlite3
def conexao():
    conexao = sqlite3.connect('bank.db')
    conexao.row_factory = sqlite3.Row
    return conexao
def iniciar():
    conect = conexao()
    cursor = conect.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS User (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            senha TEXT NOT NULL
        )
    """)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Tarefa (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXTO NOT NULL,
        descricao TEXT NOT NULL,
        prazo TEXT,
        user_id INTEGER,
        FOREING KEY user_id REFERENCES User (id)
        )
    ''')
    conect.commit()
    conect.close()
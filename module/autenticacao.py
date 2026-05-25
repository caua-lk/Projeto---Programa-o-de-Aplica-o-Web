from flask import session, redirect, url_for

def validar_usuario(callback):
    def wrapper(*args):
        if not session.get('user'):
            return redirect(url_for('login'))
        return callback(*args)
    return wrapper
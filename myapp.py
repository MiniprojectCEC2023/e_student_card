from flask import Flask, g
import mysql.connector

def create_app():
    app = Flask(__name__)

    def get_db():
        if 'db' not in g:
            g.db = mysql.connector.connect(
                host='localhost',
                user='root',
                password='shibanMySQL1234@DB',
                database='mini'
            )
            print("Connection established!")
        return g.db

    @app.teardown_appcontext
    def close_db(error):
        db = g.pop('db', None)
        if db is not None:
            db.close()

    return app



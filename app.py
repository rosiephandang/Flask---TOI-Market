import sqlite3
from flask import Flask, g, render_template, Blueprint

DATABASE = 'database.db'

#initialise app
app = Flask(__name__)
app.config['SECRET KEY'] = 'knjksjmygjhspjmkthjjk'

# views = Blueprint('views',__name__)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close() 
    return (rv[0] if rv else None) if one else rv


@app.route('/')
def home():
    # home page
    sql = """SELECT * FROM users;"""
    results = query_db(sql)
    return render_template("layout.html", results=results)

if __name__ == "__main__":
    app.run(debug=True)
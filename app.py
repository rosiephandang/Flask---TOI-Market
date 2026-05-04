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
    # home page along with product viewing & sort
    sql = """SELECT * FROM users;"""
    results = query_db(sql)
    return render_template("layout.html", results=results)

@app.route('/login/<id>')
def login(id):
    # login page
    sql = """SELECT * FROM users;"""
    results = query_db(sql, (id,), one=True)
    return render_template("login.html", results=results)

@app.route('/signup/<id>')
def signup(id):
    # signup page
    sql = """SELECT * FROM users;"""
    results = query_db(sql, (id,), one=True)
    return render_template("signup.html", results=results)

@app.route('/product/<id>')
def product(id):
    # product viewing page
    sql = """SELECT * FROM users;"""
    results = query_db(sql, (id,), one=True)
    return render_template("product.html", results=results)

@app.route('/userprofile/<id>')
def userprofile(id):
    # user profile editing page
    sql = """SELECT * FROM users;"""
    results = query_db(sql, (id,), one=True)
    return render_template("userprofile.html", results=results)

@app.route('/sellerprofile/<id>')
def sellerprofile(id):
    # seller/other user profile viewing page
    sql = """SELECT * FROM users;"""
    results = query_db(sql, (id,), one=True)
    return render_template("sellerprofile.html", results=results)

@app.route('/meeting/<id>')
def meeting(id):
    # meeting page
    sql = """SELECT * FROM users;"""
    results = query_db(sql, (id,), one=True)
    return render_template("meeting.html", results=results)

@app.route('/notifications/<id>')
def notifications(id):
    # meeting page
    sql = """SELECT * FROM users;"""
    results = query_db(sql, (id,), one=True)
    return render_template("notifications.html", results=results)


if __name__ == "__main__":
    app.run(debug=True)
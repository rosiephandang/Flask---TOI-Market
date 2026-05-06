import sqlite3
from flask import Flask, g, render_template

DATABASE = 'database.db'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'


# ---------- DATABASE ----------
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row  # allows dict-style access
    return g.db


@app.teardown_appcontext
def close_connection(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    results = cur.fetchall()
    cur.close()
    return (results[0] if results else None) if one else results


# ---------- ROUTES ----------

@app.route('/')
def home():
    products = query_db("SELECT * FROM products;")
    return render_template("home.html", products=products)

@app.route('/login/<int:user_id>')
def login(user_id):
    user = query_db("SELECT * FROM users WHERE user_id = ?", (user_id,), one=True)
    return render_template("login.html", user=user)


@app.route('/signup/<int:user_id>')
def signup(user_id):
    user = query_db("SELECT * FROM users WHERE user_id = ?", (user_id,), one=True)
    return render_template("signup.html", user=user)


@app.route('/product/<int:product_id>')
def product(product_id):
    product = query_db("SELECT * FROM products WHERE product_id = ?", (product_id,), one=True)
    return render_template("product.html", product=product)


@app.route('/userprofile/<int:user_id>')
def userprofile(user_id):
    user = query_db("SELECT * FROM users WHERE user_id = ?", (user_id,), one=True)
    return render_template("userprofile.html", user=user)


@app.route('/sellerprofile/<int:user_id>')
def sellerprofile(user_id):
    user = query_db("SELECT * FROM users WHERE user_id = ?", (user_id,), one=True)
    return render_template("sellerprofile.html", user=user)


@app.route('/meeting/<int:location_id>')
def meeting(location_id):
    location = query_db("SELECT * FROM locations WHERE location_id = ?", (location_id,), one=True)
    return render_template("meeting.html", location=location)

@app.route('/notifications/<int:user_id>')
def notifications(user_id):
    user = query_db("SELECT * FROM users WHERE user_id = ?", (user_id,), one=True)
    return render_template("notifications.html", user=user)


if __name__ == "__main__":
    app.run(debug=True)
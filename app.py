import sqlite3
from flask import Flask, g, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash

DATABASE = 'database.db'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'


#  database
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


# routes/pages 

@app.route('/')
def home():
    products = query_db("""
    SELECT products.*, users.username AS seller_username
    FROM products
    INNER JOIN users
    ON products.seller_key = users.user_id;""")   
    print(dict(products[0]))
    return render_template("home.html", products=products)

@app.route('/login/<int:user_id>')
def login(user_id):
    user = query_db("SELECT * FROM users WHERE user_id = ?", (user_id,), one=True)
    return render_template("login.html", user=user)


@app.route('/product/<int:product_id>')
def product(product_id):
    product = query_db("""
    SELECT products.*,
users.username
AS seller_username
FROM products
INNER JOIN users
ON products.seller_key = users.user_id
WHERE products.product_id = ?;""", (product_id,), one=True)
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

@app.route('/about_us/<int:user_id>')
def about_us(user_id):
    user = query_db("SELECT * FROM users WHERE user_id = ?", (user_id,), one=True)
    return render_template("about_us.html", user=user)


#  login-signup routes
@app.route('/signup/<int:user_id>', methods=["GET","POST"])
def signup(user_id):
    #user=None
    #if the user posts from the signup page
    if request.method == "POST":
        #add the new username and hashed password to the database
        email= request.form.get['email']
        username = request.form.get['username']
        password = request.form.get['password']
        
        #hash it with the cool secutiry function
        hashed_password = generate_password_hash(password)
        #write it as a new user to the database
        sql = "INSERT INTO users (email,username,password) VALUES (?,?,?)"
        query_db(sql,(email,username,hashed_password))
        if email or username or password == '':
            print("You must enter in all the boxes.")
        #message flashes exist in the base.html template and give user feedback
        else:
            flash("Sign Up Successful")
            #user = query_db("SELECT * FROM users WHERE user_id = ?", (user_id,), one=True)
            return redirect(url_for("home"))
    else:
        return render_template("signup.html", user_id=user_id)




if __name__ == "__main__":
    app.run(debug=True)
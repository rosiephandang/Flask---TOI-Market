import sqlite3
from flask import Flask, g, render_template, request, flash, redirect, url_for, session
from werkzeug.security import check_password_hash, generate_password_hash
import re

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

@app.route('/signed_in')
def home_signed_in():
    products = query_db("""
    SELECT products.*, users.username AS seller_username
    FROM products
    INNER JOIN users
    ON products.seller_key = users.user_id;""")   
    print(dict(products[0]))
    return render_template("home_signed_in.html", products=products)

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

#signup & login pageeee
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    msg = ''
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        username = request.form['username']
        password = request.form['password']
        # validation if fields arent filled
        if not email or not username or not password:
            msg = 'Please fill out all fields!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif "@burnside.school.nz" not in email:
            msg = 'You must have a Burnside High School email to use TOI Market!'
        elif not re.match(r'^[A-Za-z0-9]+$', username):
            msg = 'Username must contain only letters and numbers!'
        else:
            # check if email in database
            account = query_db('SELECT * FROM users WHERE email = ?', (email,),one=True)
            if account:
                msg = 'Account already exists!'
            else:
                hashed_password = generate_password_hash(password)
                db = get_db()
                db.execute('INSERT INTO users (email, username, password) VALUES (?, ?, ?)',(email.lower(), username, hashed_password))
                db.commit()
                flash('You have successfully created an account on TOI Market!')
                return redirect(url_for('home_signed_in'))
    return render_template('signup.html', msg=msg)

@app.route('/login', methods=["GET","POST"])
def login():
    #if the user posts a username and password
    msg = ''
    if request.method == "POST":
        #get the username and password
        email = request.form['email'].strip().lower()
        password = request.form['password']
        if not email or not password:
            msg = 'Please fill out all fields!'
        else:
            sql = "SELECT * FROM users WHERE email = ?"
            user = query_db(sql, (email,),one=True)
            if user:
                #we got a user!!
                #check password matches-
                if check_password_hash(user[3],password):
                    #we are logged in successfully
                    #Store the username in the session
                    session['user'] = dict(user)
                    flash("Logged in successfully!")
                    return redirect(url_for('home_signed_in'))
                else:
                    msg = "Password or email is incorrect."
            else:
                msg = "Email does not exist."
    #render this template regardles of get/post
    return render_template('login.html', msg = msg)

@app.route('/logout')
def logout():
    #just clear the username from the session and redirect back to the home page
    session['user'] = None
    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)






import sqlite3
from flask import Flask, g, render_template, request, flash, redirect, url_for, session
from werkzeug.security import generate_password_hash
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


#@app.route('/register', methods=['GET', 'POST'])
#def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only letters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, password, email))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
    return render_template('register.html', msg=msg)

#  login-signup routes
#@app.route('/signup/<int:user_id>', methods=["GET","POST"])
#def signup(user_id):
    #user=None
    #if the user posts from the signup page
    if request.method == "POST":
        #add the new username and hashed password to the database
        email= request.form.get['email']
        username = request.form.get['username']
        password = request.form.get['password']
        
        #hash it with the cool secutiry function
        hashed_password = generate_password_hash(password)
        query_db(sql,(email,username,hashed_password))
        if not all([email,username,password]):
            not_filled = "You must enter in all the boxes."
            return render_template("signup.html", notice=not_filled)
        #message flashes exist in the base.html template and give user feedback
        else:
            #write it as a new user to the database
            sql = "INSERT INTO users (email,username,password) VALUES (?,?,?)"
            flash("Sign Up Successful")
            #user = query_db("SELECT * FROM users WHERE user_id = ?", (user_id,), one=True)
            return redirect(url_for("home"))
    else:
        return render_template("signup.html", user_id=user_id)
    

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


if __name__ == "__main__":
    app.run(debug=True)
import sqlite3
from flask import Flask, g, render_template, request, flash, redirect, url_for, session
from werkzeug.security import check_password_hash, generate_password_hash 
import re
from datetime import date

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
    search = request.args.get('search', '').strip()
    if search:
        products = query_db("SELECT products.*, users.username AS seller_username FROM products INNER JOIN users ON products.seller_key = users.user_id WHERE products.product_name LIKE ? OR products.description LIKE ?  OR users.username LIKE ? ORDER BY products.date_posted DESC", (
            '%' + search + '%',
            '%' + search + '%',
            '%' + search + '%'
        ))   
    else:
        products = query_db("SELECT products.*, users.username AS seller_username FROM products INNER JOIN users ON products.seller_key = users.user_id ORDER BY products.date_posted DESC")
    print(dict(products[0]))
    return render_template("home.html", products=products, search=search)

@app.route('/signed_in')
def home_signed_in():
    search = request.args.get('search', '').strip()
    if search:
        products = query_db("SELECT products.*, users.username AS seller_username FROM products INNER JOIN users ON products.seller_key = users.user_id WHERE products.product_name LIKE ? OR products.description LIKE ?  OR users.username LIKE ? ORDER BY products.date_posted DESC", (
            '%' + search + '%',
            '%' + search + '%',
            '%' + search + '%'
        ))   
    else:
        products = query_db("SELECT products.*, users.username AS seller_username FROM products INNER JOIN users ON products.seller_key = users.user_id ORDER BY products.date_posted DESC")
        users = query_db("SELECT users.*, users.username AS seller_username FROM users INNER JOIN products ON users.user_id = products.seller_key")  
    print(dict(products[0])) 
    print(dict(users[0]))
    return render_template("home_signed_in.html", products=products, users=users, search=search)

@app.route('/product/<int:product_id>')
def product(product_id):
    product = query_db("SELECT products.*, users.username AS seller_username FROM products INNER JOIN users ON products.seller_key = users.user_id WHERE products.product_id = ?;", (product_id,), one=True)
    return render_template("product.html", product=product)


@app.route('/sellerprofile/<int:user_id>')
def sellerprofile(user_id):
    user = query_db("SELECT * FROM users WHERE user_id = ?", (user_id,), one=True)
    return render_template("sellerprofile.html", user=user)


@app.route('/meeting/<int:location_id>')
def meeting(location_id):
    location = query_db("SELECT * FROM locations WHERE location_id = ?", (location_id,), one=True)
    return render_template("meeting.html", location=location)

@app.route('/news/<int:user_id>')
def news(user_id):
    user = query_db("SELECT * FROM users WHERE user_id = ?", (user_id,), one=True)
    return render_template("news.html", user=user)

@app.route('/about_us/<int:user_id>')
def about_us(user_id):
    user = query_db("SELECT * FROM users WHERE user_id = ?", (user_id,), one=True)
    return render_template("about_us.html", user=user)

#signed in pages
@app.route('/about_us_signed_in/<int:user_id>')
def about_us_signed_in(user_id):
    user = query_db("SELECT * FROM users WHERE user_id = ?", (user_id,), one=True)
    return render_template("about_us_signed_in.html", user=user)

@app.route('/meeting_signed_in/<int:location_id>')
def meeting_signed_in(location_id):
    location = query_db("SELECT * FROM locations WHERE location_id = ?",(location_id,),one=True)
    return render_template("meeting_signed_in.html", location=location)

@app.route('/product_signed_in/<int:product_id>')
def product_signed_in(product_id):
    product = query_db("SELECT products.*, users.user_id AS seller_key, users.username AS seller_username FROM products INNER JOIN users ON products.seller_key = users.user_id WHERE products.product_id = ?", (product_id,), one=True)
    user_id = session.get('user_id')
    liked = query_db("SELECT * FROM product_likes WHERE product_id = ? AND user_id = ?", (product_id, user_id), one=True)
    return render_template("product_signed_in.html",product=product, liked=liked)

@app.route('/notifications_signed_in/<int:user_id>')
def notifications_signed_in(user_id):
    notifications = query_db("SELECT alerts.alert_id, alerts.message, alerts.date_created, alerts.status AS notification_status, offers.offer_id, offers.offer_price, offers.status AS offer_status, products.product_id, products.product_name, products.image_url, users.username AS buyer_username FROM alerts INNER JOIN offers ON alerts.offer_key = offers.offer_id INNER JOIN products ON offers.product_key = products.product_id INNER JOIN users ON offers.byer_key = users.user_id WHERE alerts.user_key = ? ORDER BY alerts.date_created DESC", (user_id,))
    return render_template("notifications_signed_in.html",notifications=notifications)

@app.route('/seller_profile_signed_in/<int:user_id>')
def seller_profile_signed_in(user_id):
    user = query_db("SELECT * FROM users WHERE user_id = ?", (user_id,), one=True)
    products = query_db("SELECT * FROM products WHERE seller_key = ? ORDER BY date_posted DESC", (user_id,))
    return render_template("seller_profile_signed_in.html", user=user, products=products)

@app.route('/userprofile_signed_in/<int:user_id>', methods=["GET","POST"])
def userprofile_signed_in(user_id):
    db = get_db()
    user = query_db("SELECT * FROM users WHERE user_id = ?",(user_id,),one=True)
    if request.method == "POST":
        new_username = request.form.get('username') 
        new_description = request.form.get('description')
        db.execute("UPDATE users SET username = ?, description = ? WHERE user_id = ?", (new_username, new_description, user_id))
        db.commit()
        flash("Profile updated!")
        return redirect(url_for("userprofile_signed_in", user_id=user_id))
    # urm products this user has liked
    liked_products = query_db("SELECT products.*, users.username AS seller_username, product_likes.date_liked FROM product_likes INNER JOIN products ON product_likes.product_id = products.product_id INNER JOIN users ON products.seller_key = users.user_id  WHERE product_likes.user_id = ? ORDER BY product_likes.date_liked DESC", (user_id,))
    return render_template("userprofile_signed_in.html", user=user, liked_products=liked_products)

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
                today = date.today().isoformat()
                cursor = db.execute('INSERT INTO users (email, username, password, date_joined) VALUES (?, ?, ?, ?)',(email.lower(), username, hashed_password, today))
                # cursor = db.execute("UPDATE user SET score = 0 WHERE id = ?", (user_id,))
                db.commit()
                # log the user in immeadiately after signup by storing ID
                session['user_id'] = cursor.lastrowid
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
                if check_password_hash(user['password'],password):
                    #we are logged in successfully
                    #Store the username in the session
                    session['user_id'] = user['user_id']
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
    #session.pop('user_id', None)
    flash('Logged out successfully')
    return redirect('/')


# like route
@app.route('/like/<int:product_id>', methods=['POST'])
def like_product(product_id):
    user_id = session.get('user_id')
    #if not user_id:
        #flash("You must be logged in to like products.")
        #return redirect(url_for('login'))
    alr_liked = query_db("SELECT * FROM product_likes WHERE product_id = ? AND user_id = ?", (product_id, user_id), one=True)
    db = get_db()
    if alr_liked:
        db.execute("DELETE FROM product_likes WHERE product_id = ? AND user_id = ?", (product_id, user_id))
        db.execute("UPDATE products SET likes = likes - 1 WHERE product_id = ?", (product_id,))
        flash("You've unliked this product!")
    else:
        today = date.today().isoformat()
        db.execute("INSERT INTO product_likes (product_id, user_id, date_liked) VALUES (?, ?, ?)", (product_id, user_id, today))
        db.execute("UPDATE products SET likes = likes + 1 WHERE product_id = ?", (product_id,))
        flash("You've liked this product!")
    db.commit()
    return redirect(url_for('product_signed_in', product_id=product_id))

# for sellers/users to add products
@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        product_name = request.form['product_name']
        description = request.form['description']
        price = request.form['price']
        hazards = request.form['health_hazards']
        image = request.files['image']
        if not product_name or not description or not price or not image:
            flash("Please fill out all required fields.")
            return redirect(url_for('add_product'))
        # savee image
        filename = image.filename
        image.save('static/uploads/' + filename)
        # automatically filled information
        user_id = session['user_id']
        today = date.today().isoformat()
        db = get_db()
        db.execute("INSERT INTO products (product_name, description, price_suggested, seller_key, image_url, date_posted, status, health_hazards, likes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (product_name, description, price, user_id, '/static/uploads/' + filename, today,'available', hazards, 0))
        db.commit()
        flash("Your product has been added!")
        return redirect(url_for('userprofile_signed_in', user_id=user_id))
    return render_template('add_product_signed_in.html')


@app.route('/request_product/<int:product_id>', methods=['POST'])
def request_product(product_id):
    buyer_id = session.get('user_id')
    product = query_db("SELECT * FROM products WHERE product_id = ?", (product_id,), one=True)
    # if its gone/deleted by admin
    if not product:
        flash("Product not found.")
        return redirect(url_for('home_signed_in'))
    seller_id = product['seller_key']
    # no allow sellers to request their own products
    if buyer_id == seller_id:
        flash("You cannot request to buy your own product.")
        return redirect(url_for('product_signed_in', product_id=product_id))
    # check if they already requested itt
    existing = query_db("SELECT * FROM offers WHERE product_key = ? AND byer_key = ? AND status = 'pending'", (product_id, buyer_id), one=True)
    if existing:
        flash("You have already requested this product.")
        return redirect(url_for('product_signed_in',product_id=product_id))
    offer_price = request.form['offer']
    message = request.form.get('message', '')
    db = get_db()
    cursor = db.execute("INSERT INTO offers (product_key, seller_key, offer_price, message, date_sent, status, byer_key) VALUES (?, ?, ?, ?, ?, ?, ?)", (product_id, seller_id,offer_price, message, date.today().isoformat(),'pending', buyer_id))
    offer_id = cursor.lastrowid
    db.execute("INSERT INTO alerts (user_key, offer_key, alert_type, message, date_created, status) VALUES (?, ?, ?, ?, ?, ?)", (product['seller_key'], offer_id, 1, 'Someone has requested to buy your product: ' + product['product_name'], date.today().isoformat(), 'unread'))
    db.commit()
    flash("Your request has been sent to the seller.")
    return redirect(url_for('product_signed_in', product_id=product_id))

@app.route('/requests')
def requests_page():
    seller_id = session.get('user_id')
    requests = query_db("SELECT offers.offer_id, offers.offer_price, offers.message, offers.date_sent, offers.status, products.product_id, products.product_name, products.image_url, users.username AS buyer_username FROM offers INNER JOIN products ON offers.product_key = products.product_id INNER JOIN users ON offers.byer_key = users.user_id WHERE offers.seller_key = ? ORDER BY offers.date_sent DESC", (seller_id,))
    locations = query_db("SELECT * FROM locations ORDER BY location_name")
    return render_template("requests_signed_in.html", requests=requests, locations=locations)

@app.route('/approve_request/<int:offer_id>', methods=['POST'])
def approve_request(offer_id):
    seller_id = session.get('user_id')
    location_id = request.form['meeting_location']
    db = get_db()
    # find the offer make sure it belongs to this seller
    offer = query_db("SELECT * FROM offers WHERE offer_id = ? AND seller_key = ?", (offer_id, seller_id), one=True)
    if not offer:
        flash("Offer not found.")
        return redirect(url_for('requests_page'))
    # approve the offer
    db.execute("UPDATE offers SET status = 'approved' WHERE offer_id = ?", (offer_id,))
    # meetup
    db.execute("INSERT INTO meetups (offer_key,location_key, meetup_time, status)VALUES (?, ?, ?, ?)", (offer_id, location_id, None, 'pending'))
    # ntify buyer
    db.execute("INSERT INTO alerts (user_key, offer_key, alert_type, message, date_created,status)VALUES (?, ?, ?, ?, ?, ?)", (offer['byer_key'], offer_id, 2, 'Your offer has been approved!', date.today().isoformat(), 'unread'))
    db.commit()
    flash("Offer approved!")
    return redirect(url_for('requests_page'))



if __name__ == "__main__":
    app.run(debug=True)






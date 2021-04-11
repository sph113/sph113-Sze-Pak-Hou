from flask import *
import sqlite3, hashlib, os
from werkzeug.utils import secure_filename
from datetime import date
import random

app = Flask(__name__)
app.secret_key = 'random string'
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['jpeg', 'jpg', 'png', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def getLoginDetails():
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        if 'email' not in session:
            loggedIn = False
            firstName = ''
            noOfItems = 0
            isadmin = False
        else:
            loggedIn = True
            email=session['email']
            cur.execute("SELECT userId, firstName, admin FROM users WHERE email = ?", (email, ))
            userId, firstName, Admin = cur.fetchone()
            cur.execute("SELECT count(productId) FROM kart WHERE userId = ?", (userId, ))
            noOfItems = cur.fetchone()[0]
            if Admin == 1:
                isadmin = True
            else:
                isadmin = False
    conn.close()
    return (loggedIn, firstName, noOfItems, isadmin)

@app.route("/")
def root():
    loggedIn, firstName, noOfItems, isadmin = getLoginDetails()
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT productId, name, image FROM products')
        itemData = cur.fetchall()
        cur.execute('SELECT vendorId, name FROM vendors')
        vendorData = cur.fetchall()
    itemData = parse(itemData)
    random.sample(itemData[0],4)
    
    return render_template('home.html', itemData=random.sample(itemData[0],4), loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems, vendorData=vendorData, isadmin=isadmin)

@app.route("/all")
def all():
    loggedIn, firstName, noOfItems, isadmin = getLoginDetails()
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT productId, name, price, description, image, stock FROM products')
        itemData = cur.fetchall()
        cur.execute('SELECT vendorId, name FROM vendors')
        vendorData = cur.fetchall()
    itemData = parse(itemData)   
    return render_template('allproduct.html', itemData=itemData, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems, vendorData=vendorData, isadmin=isadmin)

@app.route("/add")
def admin():
    loggedIn, firstName, noOfItems, isadmin = getLoginDetails()
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT vendorId, name FROM vendors")
        vendors = cur.fetchall()
        cur.execute('SELECT vendorId, name FROM vendors')
        vendorData = cur.fetchall()
    conn.close()
    return render_template('add.html', vendors=vendors, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems, vendorData=vendorData, isadmin=isadmin)

@app.route("/addItem", methods=["GET", "POST"])
def addItem():
    if request.method == "POST":
        name = request.form['name']
        price = float(request.form['price'])
        description = request.form['description']
        stock = int(request.form['stock'])
        vendorId = int(request.form['vendor'])

        #Uploading image procedure
        image = request.files['image']
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        imagename = filename
        with sqlite3.connect('database.db') as conn:
            try:
                cur = conn.cursor()
                cur.execute('''INSERT INTO products (name, price, description, image, stock, vendorId) VALUES (?, ?, ?, ?, ?, ?)''', (name, price, description, imagename, stock, vendorId))
                conn.commit()
                msg="added successfully"
            except:
                msg="error occured"
                conn.rollback()
        conn.close()
        print(msg)
        return redirect(url_for('root'))

@app.route("/remove")
def remove():
    loggedIn, firstName, noOfItems, isadmin = getLoginDetails()
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT productId, name, price, description, image, stock FROM products')
        data = cur.fetchall()
        cur.execute('SELECT vendorId, name FROM vendors')
        vendorData = cur.fetchall()
    conn.close()
    return render_template('remove.html', data=data, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems, vendorData=vendorData, isadmin=isadmin)

@app.route("/removeItem")
def removeItem():
    productId = request.args.get('productId')
    with sqlite3.connect('database.db') as conn:
        try:
            cur = conn.cursor()
            cur.execute('DELETE FROM products WHERE productID = ?', (productId, ))
            conn.commit()
            msg = "Deleted successsfully"
        except:
            conn.rollback()
            msg = "Error occured"
    conn.close()
    print(msg)
    return redirect(url_for('remove'))

@app.route("/edititemform")
def editeproduct():
    loggedIn, firstName, noOfItems, isadmin = getLoginDetails()
    productId = request.args.get('productId')
    with sqlite3.connect('database.db') as con:
        cur = con.cursor()
        cur.execute('SELECT productId, name, price, description, image, stock, vendorId FROM products WHERE productId = ?',(productId,))
        data = cur.fetchall()
        cur.execute('SELECT vendorId, name FROM vendors')
        vendorData = cur.fetchall()
        vendors=vendorData
        vendorId=data[0][6]
        fileaddress=url_for('static', filename='uploads/' + data[0][4])
        cur.execute('SELECT name FROM vendors WHERE vendorId = ?',(vendorId,))
        vendorname = cur.fetchone()[0]
    con.close()
    return render_template('editproduct.html', fileaddress=fileaddress ,productId=productId ,vendorname=vendorname ,vendors=vendors, data=data, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems, vendorData=vendorData, isadmin=isadmin)

@app.route("/editItem", methods=["GET", "POST"])
def editItem():
    productId = request.args.get('productId')
    if request.method == "POST":
        name = request.form['name']
        price = float(request.form['price'])
        description = request.form['description']
        stock = int(request.form['stock'])
        vendorId = int(request.form['vendor'])

        #Uploading image procedure
        with sqlite3.connect('database.db') as conn:
            try:
                cur = conn.cursor()
                cur.execute('''UPDATE products SET name = ?, price = ?, description = ?, stock = ?, vendorId = ?WHERE productId = ?''', (name,price,description,stock,vendorId,productId,))
                conn.commit()
                msg="edit successfully"
            except:
                msg="error occured"
                conn.rollback()
        conn.close()
        return redirect(url_for('remove'))

@app.route("/displayVendor")
def displayVendor():
        loggedIn, firstName, noOfItems, isadmin = getLoginDetails()
        vendorId = request.args.get("vendorId")
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT products.productId, products.name, products.price, products.image, vendors.name FROM products, vendors WHERE products.vendorId = vendors.vendorId AND vendors.vendorId = ?", (vendorId, ))
            data = cur.fetchall()
            cur.execute('SELECT vendorId, name FROM vendors')
            vendorData = cur.fetchall()
        conn.close()
        vendorName = data[0][4]
        data = parse(data)
        return render_template('displayVendor.html', data=data, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems, vendorName=vendorName, vendorData=vendorData, isadmin=isadmin)

@app.route("/account/profile")
def profileHome():
    if 'email' not in session:
        return redirect(url_for('root'))
    loggedIn, firstName, noOfItems, isadmin = getLoginDetails()
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT vendorId, name FROM vendors')
        vendorData = cur.fetchall()
        cur.execute("SELECT userId, email, firstName, lastName, address1, address2, zipcode, city, state, country, phone FROM users WHERE email = ?", (session['email'], ))
        profileData = cur.fetchone()
    return render_template("profileHome.html", profileData=profileData, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems, vendorData=vendorData, isadmin=isadmin)

@app.route("/account/profile/edit")
def editProfile():
    if 'email' not in session:
        return redirect(url_for('root'))
    loggedIn, firstName, noOfItems, isadmin = getLoginDetails()
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT vendorId, name FROM vendors')
        vendorData = cur.fetchall()
        cur.execute("SELECT userId, email, firstName, lastName, address1, address2, zipcode, city, state, country, phone FROM users WHERE email = ?", (session['email'], ))
        profileData = cur.fetchone()
    conn.close()
    return render_template("editProfile.html", profileData=profileData, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems, vendorData=vendorData, isadmin=isadmin)

@app.route("/account/profile/changePassword", methods=["GET", "POST"])
def changePassword():
    loggedIn, firstName, noOfItems, isadmin = getLoginDetails()
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    if request.method == "POST":
        oldPassword = request.form['oldpassword']
        oldPassword = hashlib.md5(oldPassword.encode()).hexdigest()
        newPassword = request.form['newpassword']
        newPassword = hashlib.md5(newPassword.encode()).hexdigest()
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT userId, password FROM users WHERE email = ?", (session['email'], ))
            userId, password = cur.fetchone()
            changepassword=True
            if (password == oldPassword):
                try:
                    cur.execute("UPDATE users SET password = ? WHERE userId = ?", (newPassword, userId))
                    conn.commit()
                    msg="Changed successfully"
                    flash(msg)
                except:
                    conn.rollback()
                    msg = "Failed"
                    flash(msg)
                return render_template("changePassword.html")
            else:
                msg = "Wrong password"
                flash(msg)
        conn.close()
        return render_template("changePassword.html",changepassword=changepassword)
    else:
        return render_template("changePassword.html")

@app.route("/updateProfile", methods=["GET", "POST"])
def updateProfile():
    if request.method == 'POST':
        email = request.form['email']
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        address1 = request.form['address1']
        address2 = request.form['address2']
        zipcode = request.form['zipcode']
        city = request.form['city']
        state = request.form['state']
        country = request.form['country']
        phone = request.form['phone']
        with sqlite3.connect('database.db') as con:
                try:
                    cur = con.cursor()
                    cur.execute('UPDATE users SET firstName = ?, lastName = ?, address1 = ?, address2 = ?, zipcode = ?, city = ?, state = ?, country = ?, phone = ? WHERE email = ?', (firstName, lastName, address1, address2, zipcode, city, state, country, phone, email))

                    con.commit()
                    msg = "Saved Successfully"
                except:
                    con.rollback()
                    msg = "Error occured"
        con.close()
        flash(msg)
        return redirect(url_for('editProfile'))

@app.route("/loginForm")
def loginForm():
    if 'email' in session:
        return redirect(url_for('root'))
    else:
        return render_template('login.html', error='')

@app.route("/login", methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if is_valid(email, password):
            session['email'] = email
            return redirect(url_for('root'))
        else:
            error = 'Invalid UserId / Password'
            flash("Invalid UserId / Password")
            return render_template('login.html', error=error)

@app.route("/productDescription")
def productDescription():
    loggedIn, firstName, noOfItems, isadmin = getLoginDetails()
    productId = request.args.get('productId')
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT vendorId, name FROM vendors')
        vendorData = cur.fetchall()
        cur.execute('SELECT productId, name, price, description, image, stock FROM products WHERE productId = ?', (productId, ))
        productData = cur.fetchone()
    conn.close()
    return render_template("productDescription.html", data=productData, loggedIn = loggedIn, firstName = firstName, noOfItems = noOfItems, vendorData=vendorData, isadmin=isadmin)

@app.route("/addToCart")
def addToCart():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    else:
        productId = int(request.args.get('productId'))
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT userId FROM users WHERE email = ?", (session['email'], ))
            userId = cur.fetchone()[0]
            try:
                cur.execute("INSERT INTO kart (userId, productId) VALUES (?, ?)", (userId, productId))
                conn.commit()
                msg = "Added successfully"
            except:
                conn.rollback()
                msg = "Error occured"
        conn.close()
        return redirect(url_for('root'))

@app.route("/cart")
def cart():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    loggedIn, firstName, noOfItems, isadmin = getLoginDetails()
    email = session['email']
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT userId FROM users WHERE email = ?", (email, ))
        userId = cur.fetchone()[0]
        cur.execute("SELECT products.productId, products.name, products.price, products.image FROM products, kart WHERE products.productId = kart.productId AND kart.userId = ?", (userId, ))
        products = cur.fetchall()
        cur.execute('SELECT vendorId, name FROM vendors')
        vendorData = cur.fetchall()
    totalPrice = 0
    for row in products:
        totalPrice += row[2]
    return render_template("cart.html", products = products, totalPrice=totalPrice, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems, vendorData=vendorData, isadmin=isadmin)

@app.route("/removeFromCart")
def removeFromCart():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    email = session['email']
    productId = int(request.args.get('productId'))
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT userId FROM users WHERE email = ?", (email, ))
        userId = cur.fetchone()[0]
        try:
            cur.execute("DELETE FROM kart WHERE userId = ? AND productId = ?", (userId, productId))
            conn.commit()
            msg = "removed successfully"
        except:
            conn.rollback()
            msg = "error occured"
    conn.close()
    return redirect(url_for('root'))

@app.route("/logout")
def logout():
    session.pop('email', None)
    return redirect(url_for('root'))

def is_valid(email, password):
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute('SELECT email, password FROM users')
    data = cur.fetchall()
    for row in data:
        if row[0] == email and row[1] == hashlib.md5(password.encode()).hexdigest():
            return True
    return False

@app.route("/register", methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        #Parse form data    
        password = request.form['password']
        email = request.form['email']
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        address1 = request.form['address1']
        address2 = request.form['address2']
        zipcode = request.form['zipcode']
        city = request.form['city']
        state = request.form['state']
        country = request.form['country']
        phone = request.form['phone']

        with sqlite3.connect('database.db') as con:
            try:
                cur = con.cursor()
                cur.execute('INSERT INTO users (password, email, firstName, lastName, address1, address2, zipcode, city, state, country, phone) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (hashlib.md5(password.encode()).hexdigest(), email, firstName, lastName, address1, address2, zipcode, city, state, country, phone))

                con.commit()

                msg = "Registered Successfully"
            except:
                con.rollback()
                msg = "Error occured"
        con.close()
        flash(msg)
        return render_template("login.html", error=msg)

@app.route("/registerationForm")
def registrationForm():
    return render_template("register.html")

@app.route('/checkout')
def checkout():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    loggedIn, firstName, noOfItems, isadmin = getLoginDetails()
    email = session['email']
    
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT vendorId, name FROM vendors')
        vendorData = cur.fetchall()
        cur.execute("SELECT userId FROM users WHERE email = ?", (email, ))
        userId = cur.fetchone()[0]
        cur.execute("SELECT products.productId FROM products, kart WHERE products.productId = kart.productId AND kart.userId = ?", (userId, ))
        productIds = cur.fetchall()
        for datas in productIds:
            for productId in datas:(
                cur.execute("INSERT INTO orders ( userId, productId, ordertime ) VALUES ( ?, ?, ? );", ( userId, productId, date.today() ))
            )
        conn.commit()
        cur.execute("DELETE FROM kart where userId = ?",(userId, ))
    conn.close()
    return render_template("order.html", loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems, vendorData=vendorData, isadmin=isadmin)

@app.route('/account/orders')
def orders():
    loggedIn, firstName, noOfItems, isadmin = getLoginDetails()
    email = session['email']
    Today=str(date.today())
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT vendorId, name FROM vendors')
        vendorData = cur.fetchall()
        cur.execute("SELECT userId FROM users WHERE email = ?", (email, ))
        userId = cur.fetchone()[0]
        cur.execute("SELECT orders.ordertime ,products.productId ,products.name ,products.image FROM orders,products WHERE orders.userId= ? AND orders.productId=products.productId", (userId, ))
        ordersData = cur.fetchall()
        cur.execute("SELECT DISTINCT ordertime FROM orders WHERE ordertime != ? AND userId = ?", (Today, userId))
        dates = cur.fetchall()
    conn.close()
    return render_template("orders.html",Today=Today ,dates=dates ,ordersData=ordersData, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems, vendorData=vendorData, isadmin=isadmin)

@app.route('/aboutus')
def aboutus():
    loggedIn, firstName, noOfItems, isadmin = getLoginDetails()
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT vendorId, name FROM vendors')
        vendorData = cur.fetchall()
    conn.close()
    return render_template('aboutus.html', loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems, vendorData=vendorData, isadmin=isadmin)

@app.route('/searchd', methods = ['POST', 'GET'])
def search():
    loggedIn, firstName, noOfItems, isadmin = getLoginDetails()
    search = request.args.get('search')
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT vendorId, name FROM vendors')
        vendorData = cur.fetchall()
    conn.close()
    with sqlite3.connect('database.db') as con:
        cur = con.cursor()
        cur.execute("SELECT productId, name, price, description, image, stock FROM products WHERE name LIKE ?", ("%%"+search+"%%"),)
        itemData = cur.fetchall()
        itemData = parse(itemData) 
        msg = "Here are the result(s) for:"+ search
    con.close()
    return render_template("search.html", error=msg, itemData=itemData, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems, vendorData=vendorData, isadmin=isadmin)

@app.route('/search', methods = ['POST', 'GET'])
def dsearch():
    
    search = request.args.get('search')
    qurey="%%"+search+"%%"
    return do_search(qurey=qurey,search=search)
    
def do_search(qurey,search):
    with sqlite3.connect('database.db') as con:
            loggedIn, firstName, noOfItems, isadmin = getLoginDetails()
            cur = con.cursor()
            cur.execute('SELECT vendorId, name FROM vendors')
            vendorData = cur.fetchall()
            cur.execute('SELECT productId, name, price, description, image, stock FROM products WHERE name like ?', (qurey,))
            itemData = cur.fetchall()
            itemData = parse(itemData)
    return render_template("search.html",search=search ,itemData=itemData, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems, vendorData=vendorData, isadmin=isadmin)

def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def parse(data):
    ans = []
    i = 0
    while i < len(data):
        curr = []
        for j in range(7):
            if i >= len(data):
                break
            curr.append(data[i])
            i += 1
        ans.append(curr)
    return ans

if __name__ == '__main__':
    app.run(debug=True)

import sqlite3

#Open database
conn = sqlite3.connect('database.db')

#Create table
conn.execute('''CREATE TABLE users 
		(userId INTEGER PRIMARY KEY, 
		password TEXT,
		email TEXT,
		firstName TEXT,
		lastName TEXT,
		address1 TEXT,
		address2 TEXT,
		zipcode TEXT,
		city TEXT,
		state TEXT,
		country TEXT, 
		phone TEXT,
		admin INTEGER
		)''')

conn.execute('''CREATE TABLE products
		(productId INTEGER PRIMARY KEY,
		name TEXT,
		price REAL,
		description TEXT,
		image TEXT,
		stock INTEGER,
		vendorId INTEGER,
		FOREIGN KEY(vendorId) REFERENCES vendors(vendorId)
		)''')

conn.execute('''CREATE TABLE kart
		(userId INTEGER,
		productId INTEGER,
		FOREIGN KEY(userId) REFERENCES users(userId),
		FOREIGN KEY(productId) REFERENCES products(productId)
		)''')

conn.execute('''CREATE TABLE orders
		(orderId INTEGER PRIMARY KEY,
		userId INTEGER,
		productId INTEGER,
		ordertime TEXT,
		FOREIGN KEY(userId) REFERENCES users(userId),
		FOREIGN KEY(productId) REFERENCES products(productId)
		)''')

conn.execute('''CREATE TABLE vendors
		(vendorId INTEGER PRIMARY KEY,
		name TEXT
		)''')



conn.close()


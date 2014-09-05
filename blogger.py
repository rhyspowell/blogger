# all the imports
import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from contextlib import closing
from flask_sqlalchemy import SQLAlchemy

# create our little application
app = Flask(__name__)
#application configuration
app.config.from_pyfile('blogger.config')

#Connect and build database functions
def connect_db():
	return sqlite3.connect(app.config['DATABASE'])

def init_db():
	with closing(connect_db()) as db:
		with app.open_resource('schema.sql', mode='r') as f:
			db.cursor().executescript(f.read())
		db.commit()

@app.before_request
def before_request():
	g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
	db = getattr(g, 'db', None)
	if db is not None:
		db.close()

#main page route
@app.route('/')
def show_entries():
	cur = g.db.execute('select title, text from entries order by id desc')
	entries = [dict(title=row[0], text=row[1]) for row in cur.fetchall()]
	return render_template('show_entries.html', entries=entries)

#add a post
@app.route('/add', methods=['GET', 'POST'])
def add_entry():
	if request.method == 'GET':
		if not session.get('logged_in'):
			flash('You need to be logged in to do that')
			return redirect(url_for('show_entries'))
		return render_template('add_post.html')
	if request.method == 'POST':
		g.db.execute('insert into entries (title, text) values (?,?)', [request.form['title'], request.form['text']])
		g.db.commit()
		flash('New entry was sucessfully posted')
		return redirect(url_for('show_entries'))

#login and out methods
@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST':
		if request.form['username'] != app.config['USERNAME'] or request.form['password'] != app.config['PASSWORD']:
			error = "Incorrect username or password"
		else:
			session['logged_in'] = True
			flash('You have sucessfully logged in')
			return redirect(url_for('show_entries'))
	return render_template('login.html', error=error)

@app.route('/logout')
def logout():
	session.pop('logged_in', None)
	flash('You have been logged out')
	return redirect(url_for('show_entries'))

if __name__ == '__main__':
	app.run()
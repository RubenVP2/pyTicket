from flask import Flask
from flask import render_template
from flask import abort, redirect, url_for
from flask import Flask, current_app, g, render_template
from flask.cli import with_appcontext

import sqlite3
import click

app = Flask(__name__)

@app.route('/login/')
def login():
    return render_template('userConnect.html')

@app.route('/ticketDetail/')
def ticketDetail():
    return render_template('ticketDetail.html')

@app.errorhandler(404)
def page_not_found(error):
    return render_template('error404.html'), 404

@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/add-ticket')
def ajout_ticket_page():
    """ return template to add a ticket """
    return render_template('add-ticket.html')

@app.route('/admin')
def  admin_page():
    """ return template admin """
    return render_template('admin.html')
@app.route('/testgetallusers')
def testGetAllUsers():
    users = get_all_users()
    return render_template('testusers.html', users=users)

@app.route('/testuser/<username>')
def user(username=None):
    return render_template('testuserdetails.html', username=username)


# BDD

def get_all_users():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM user")
    return cur.fetchall()

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            'instance/bdd.db',
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()

    with app.open_resource('schema.sql') as f:
        # Pour éxécuter du script SQL
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


app.teardown_appcontext(close_db)
app.cli.add_command(init_db_command)

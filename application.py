from flask import Flask
from flask import render_template
from flask import abort, redirect, url_for
from flask import Flask, current_app, g, render_template, session, request
from flask.cli import with_appcontext

import sqlite3
import click
from flask.globals import request, session
from werkzeug.utils import escape

app = Flask(__name__)

app.secret_key = b'\x98\xca\x17\xbfg/v\x1dB\x93Lu\xcf3\x93\xfa'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user = login(request.form['username'],request.form['password'])
        if user:
            session['username'] = request.form['username']
            return redirect(url_for('ticket'))
    return render_template('index.html')

@app.route('/ticketDetail/')
def ticketDetail():
    return render_template('ticketDetail.html')

@app.errorhandler(404)
def page_not_found(error):
    return render_template('error404.html'), 404

@app.route('/ticket')
def ticket():
    """ Return list of tickets to suit of type user """
    user = get_user(session['username'])
    if user['isAdmin']:
        return render_template('ticket.html', user=user, tickets=get_all_tickets())
    return render_template('ticket.html', user=user, tickets=get_ticket_for_user())

@app.route('/add-ticket')
def ajout_ticket_page():
    """ return template to add a ticket """
    return render_template('add-ticket.html')

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

def get_ticket_for_user(username):
    """ Return tickets for a user specified in param """
    db = get_db()
    cur = db.cursor()
    cur.execute(f"""
    SELECT id, user.username as 'username', date_ticket, sujet_ticket, description_ticket, etat_ticket 
    FROM user, ticket
    WHERE user.id = ticket.client_id 
    AND ticket.client_id = {username}
    """)
    return cur.fetchall()

def get_all_tickets():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT ticket.id, user.username as 'username', datetime(date_ticket, 'unixepoch'), sujet_ticket, description_ticket, etat_ticket FROM user inner join ticket on user.id = ticket.client_id")
    return cur.fetchall()

def login(username, password):
    db = get_db()
    cur = db.cursor()
    cur.execute(f"SELECT username FROM user where username='{username}' AND password ='{password}'")
    return cur.fetchall()

def get_user(username):
    db = get_db()
    cur = db.cursor()
    cur.execute(f"SELECT * FROM user where username='{username}'")
    return cur.fetchone()

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

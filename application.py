from flask import Flask
from flask import render_template
from flask import abort, redirect, url_for
from flask import Flask, current_app, g, render_template, session, request
from flask.cli import with_appcontext

import sqlite3
import json
import click
from flask.globals import request, session
from werkzeug.utils import escape

app = Flask(__name__)

app.secret_key = b'\x98\xca\x17\xbfg/v\x1dB\x93Lu\xcf3\x93\xfa'
@app.route('/', methods=['GET', 'POST'])
def index():
    if 'username' in session:
        return redirect(url_for('ticket'))
    if request.method == 'POST':
        user = login(request.form['username'],request.form['password'])
        if user:
            session['username'] = request.form['username']
            return redirect(url_for('ticket'))
        else:
            error = 'true'
            return render_template('index.html', error=error)
    return render_template('index.html')

@app.route('/logout')
def logout():
    """ Remove session for user currently connect """
    session.pop('username', None)
    return redirect(url_for('index'))

@app.errorhandler(404)
def page_not_found(error):
    return render_template('error404.html'), 404

@app.route('/ticket')
def ticket():
    """ Return list of tickets to suit of type user """
    user = get_user(session['username'])
    if user['isAdmin']:
        return render_template('ticket.html', user=user, tickets=get_all_tickets())
    return render_template('ticket.html', user=user, tickets=get_ticket_for_user(user))


@app.route('/ticket/<idTicket>', methods=["GET", "POST"])
def ticketDetail(idTicket):
    """ Test to catch error for idTicket greater than max id on database"""
    maxIdTicket = max_ticket()
    if int(idTicket) <= maxIdTicket[0]:
        """ Call func to update ticket """
        if request.method == "POST":
            msg = update_ticket(idTicket, request.form['sujet'], request.form['description'], request.form['radioEtat'])
            return redirect(url_for('ticket'))
        """ Return template who show detail of it or update the ticket in database"""
        return render_template('ticketDetail.html', ticket = get_ticket(idTicket), user=get_user(session['username']))
    return redirect(url_for('ticket'))

@app.route('/ticket/<idTicket>/delete')
def ticketDelete(idTicket):
    """ Delete ticket on database  and send it to /ticket with message success or error """
    res = delete_ticket(idTicket)
    return redirect(url_for('ticket'))

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

def make_query(query, needCommit, isAll=None):
    """ Make query and return in list all rows or just one """
    db = get_db()
    cur = db.cursor()
    cur.execute(query)
    if needCommit:
        db.commit()
        return 'DONE';
    if isAll:
        return cur.fetchall()
    return cur.fetchone()


def get_ticket(idTicket):
    """ Return information of ticket """
    return make_query(f"""
        SELECT ticket.id, user.username as 'username', sujet_ticket, 
        datetime(date_ticket, 'unixepoch'), description_ticket, etat_ticket 
        FROM user inner join ticket on user.id = ticket.client_id 
        WHERE ticket.id = {idTicket}; """, 0, 0) 

def update_ticket(idTicket, sujet_ticket, description_ticket, etat_ticket):
    """ Update information of ticket """
    return make_query(f"""UPDATE ticket SET sujet_ticket = "{sujet_ticket}", 
        description_ticket = "{description_ticket}",
        etat_ticket = "{etat_ticket}" WHERE id = {idTicket} """, 1)

def max_ticket():
    """Return the greatest id of ticket """
    return make_query("SELECT Max(id) FROM Ticket", 0, 0)

def delete_ticket(idTicket):
    """ Delete ticket by id """
    return make_query(f"DELETE from ticket WHERE id = {idTicket}", 1)

def get_ticket_for_user(username):
    """ Return tickets for a user specified in param """
    db = get_db()
    cur = db.cursor()
    cur.execute(f"SELECT ticket.id, user.username as 'username', sujet_ticket, datetime(date_ticket, 'unixepoch'), description_ticket, etat_ticket FROM user inner join ticket on user.id = ticket.client_id WHERE user.id LIKE '{username[0]}' ")
    return cur.fetchall()

def get_all_tickets():
    """ Return all tickets in database """
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT ticket.id, user.username as 'username', sujet_ticket, datetime(date_ticket, 'unixepoch'), description_ticket, etat_ticket FROM user inner join ticket on user.id = ticket.client_id")
    return cur.fetchall()

def login(username, password):
    db = get_db()
    cur = db.cursor()
    cur.execute(f"SELECT username, isAdmin FROM user where username='{username}' AND password ='{password}'")
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

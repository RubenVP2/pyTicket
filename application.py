from flask import Flask
from flask import render_template
from flask import redirect, url_for
from flask import Flask, g, render_template, session, request
from flask.cli import with_appcontext
import sqlite3
import click
from flask.globals import request, session
from flask.helpers import flash

app = Flask(__name__)

app.secret_key = b'\x98\xca\x17\xbfg/v\x1dB\x93Lu\xcf3\x93\xfa'

# Route
@app.route('/', methods=['GET', 'POST'])
def index():
    """ Show the login form or log the user """
    """ Check if the user is logged in"""
    if 'username' in session:
        return redirect(url_for('ticket'))
    if request.method == 'POST':
        """ Try to log the user with username and password in the form"""
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
    """ Show 404 not found """
    return render_template('error404.html'), 404

@app.route('/ticket')
def ticket():
    """ Return list of tickets to suit of type user """
    """ check if the user is logged in """
    if 'username' in session:
        user = get_user(session['username'])
        if user['isAdmin']:
            return render_template('ticket.html', user=user, tickets=get_all_tickets())
        return render_template('ticket.html', user=user, tickets=get_ticket_for_user(user))
    return redirect(url_for('index'))

@app.route('/add-ticket',methods=['GET','POST'])
def ajout_ticket_page():
    """add ticket for user type=client"""
    if 'username' in session :
        user = get_user(session['username'])
        if user['isAdmin'] == 0:
            if request.method == 'POST':
                userId = get_userId(session['username'])
                ajoutTicket = add_ticket(userId,request.form['subject_ticket'],request.form['description_ticket'])
                return redirect(url_for('ticket'))
            """ return template to add a ticket """
            return render_template('add-ticket.html')
        return redirect(url_for('index'))
    return redirect(url_for('index'))                                                                       

@app.route('/ticket/<idTicket>', methods=["GET", "POST"])
def ticketDetail(idTicket: str):
    """ check if the user is logged in and check if idTicket can parse to int to catch error """
    if 'username' in session and isinstance(idTicket, int):
        user = get_user(session['username'])
        """ Test to catch error for idTicket greater than max id on database"""
        idTicketUrlValid = int(idTicket) <= max_ticket()[0]
        """ check if user can access to ticket in url and allow admin to access every ticket """
        if (idTicketUrlValid and ticketIsAtUser(int(idTicket))) or (user['isAdmin'] and idTicketUrlValid):
            """ Call func to update ticket and redirect to /ticket with msg """
            if request.method == "POST":
                update_ticket(int(idTicket), request.form['sujet'], request.form['description'], request.form['radioEtat'])
                flash("Les modifications ont bien été prises en compte", 'success')
                return redirect(url_for('ticket'))
            """ Return template who show detail of ticket """
            return render_template('ticketDetail.html', ticket = get_ticket(int(idTicket)), user=get_user(session['username']))
        flash("Vous avez tenté d'accéder à un ticket qui n'existe pas ou qui n'est pas le vôtre", 'info')
        return redirect(url_for('ticket'))
    return redirect(url_for('index'))

@app.route('/ticket/<idTicket>/delete')
def ticketDelete(idTicket: str):
    """ Check if the current user is the creator of this ticket and Delete it on database"""
    if 'username' in session :
        """ Check if idTicket can parse to int to catch error """
        if isinstance(idTicket, int) and ticketIsAtUser(int(idTicket)):
            delete_ticket(int(idTicket))
            flash("Votre ticket à bien été supprimé", 'success')
            return redirect(url_for('ticket'))
        """ Return error msg """
        flash("Impossible de supprimer un ticket qui n'est pas le vôtre", 'info')
        return redirect(url_for("ticket"))
    return redirect(url_for("index"))


@app.route('/profile', methods=['GET', 'POST'])
def userProfile():
    """ Show template for user profile """
    if "username" in session :
        """ Check if method is post, then we need to update values on database """
        if request.method == "POST":
            username = request.form['username']
            password = request.form['password']
            """ if password var is empty then i just make username update """
            if not password:
                """ update username in bdd and session and send to /ticket with msg success """
                update_user(get_user(session['username'])[0], username, onlyUsername=True)
                session['username'] = username
                flash('Vôtre pseudonyme à bien été mis à jour', 'success')
                return redirect(url_for('ticket'))
            """ update password, username, session and send to /ticket with msg success """
            update_user(get_user(session['username'])[0], username, password=password)
            session['username'] = username
            flash("Vos informations ont été mise à jour", 'success')
            return redirect(url_for('ticket'))
        return render_template('profile.html', user=get_user(session['username']))
    return redirect(url_for('index'))

# Autres

def ticketIsAtUser(idTicket: int):
    """ Test to know if user is the creator of this ticket"""
    tickets = get_ticket_for_user(get_user(session['username']))
    for ticket in tickets:
        if ticket[0] == idTicket:
            return True
    return False

# BDD

def make_query(query: str, needCommit: bool, isAll: bool=None):
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

def update_user(idUser: int, username: str, password: str=None, onlyUsername: bool=None):
    """Update information for user can update only username or password and username"""
    if onlyUsername:
        return make_query(f"UPDATE user SET username = '{username}' WHERE id = {idUser}", 1)
    return make_query(f"UPDATE user SET username = '{username}', password = '{password}' WHERE id = {idUser}", 1)

def get_ticket(idTicket: int):
    """ Return information of ticket """
    return make_query(f"""
        SELECT ticket.id, user.username as 'username', sujet_ticket,
        datetime(date_ticket, 'unixepoch'), description_ticket, etat_ticket
        FROM user inner join ticket on user.id = ticket.client_id
        WHERE ticket.id = {idTicket}; """, 0, 0)

def update_ticket(idTicket: int, sujet_ticket: str, description_ticket: str, etat_ticket: str):
    """ Update information of ticket """
    return make_query(f"""UPDATE ticket SET sujet_ticket = "{sujet_ticket}",
        description_ticket = "{description_ticket}",
        etat_ticket = "{etat_ticket}" WHERE id = {idTicket} """, 1)

def add_ticket(userId ,subject_ticket,description_ticket):
    """Insert ticket in database"""
    db = get_db()
    cur = db.cursor()
    #user = get_user(session['username'])
    cur.execute(f"INSERT INTO ticket (client_id,sujet_ticket,description_ticket) VALUES ({userId[0]},'{subject_ticket}','{description_ticket}')")
    db.commit()
    return "done"


def get_userId(username):
    db = get_db()
    cur = db.cursor()
    cur.execute(f"SELECT id FROM user where username='{username}'")
    return cur.fetchone()

def max_ticket():
    """Return the greatest id of ticket """
    return make_query("SELECT Max(id) FROM Ticket", 0, 0)

def delete_ticket(idTicket: int):
    """ Delete ticket by id """
    return make_query(f"DELETE from ticket WHERE id = {idTicket}", 1)

def get_ticket_for_user(username: tuple):
    """ Return tickets for a user specified in param """
    db = get_db()
    cur = db.cursor()
    cur.execute(f"SELECT ticket.id, user.username as 'username', sujet_ticket, strftime('%d/%m/%Y', date_ticket), etat_ticket FROM user inner join ticket on user.id = ticket.client_id WHERE user.id LIKE '{username[0]}' ")
    return cur.fetchall()

def get_all_tickets():
    """ Return all tickets in database """
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT ticket.id, user.username as 'username', sujet_ticket,date_ticket , strftime('%d/%m/%Y', date_ticket), etat_ticket FROM user inner join ticket on user.id = ticket.client_id ORDER BY datetime(date_ticket, 'unixepoch') DESC")
    return cur.fetchall()

def login(username: str, password: str):
    db = get_db()
    cur = db.cursor()
    cur.execute(f"SELECT username, isAdmin FROM user where username='{username}' AND password ='{password}'")
    return cur.fetchall()

def get_user(username: str):
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

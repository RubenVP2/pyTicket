import sqlite3
import click
from flask import Flask, current_app, g
from flask.templating import render_template

# App part
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/add-ticket')
def ajout_ticket():
    """ return template for add a ticket """
    return render_template('add-ticket.html')
from flask import Flask
from flask import render_template
from flask import abort, redirect, url_for

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

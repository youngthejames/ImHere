#!/usr/bin/env python2.7

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, render_template, request, g

tmpl_dir = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'templates')
app = Flask(__name__, template_folder=tmpl_dir)

engine = create_engine('postgresql://ricardo:password@localhost/mydb')


@app.before_request
def before_request():
    try:
        g.conn = engine.connect()
    except:
        print 'uh oh, problem connecting to database'
        import traceback; traceback.print_exc()
        g.conn = None


@app.teardown_request
def teardown_request(exception):
    try:
        g.conn.close()
    except Exception as e:
        pass


@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'GET':
        return render_template('login.html')
        
    else:
        return render_template('index.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'GET':
        return render_template('register.html')

    elif request.method == 'POST':

        # user hit register inside of the register page
        if len(request.form) is 3:

            username = request.form["username"]
            password = request.form["password"]
            vpassword = request.form["vpassword"]

            if username == '' or password == '' or vpassword == '':
                return render_template('register.html', incomplete=True)

            # TODO: check if username is already in database

            # check for a password mismatch
            if password != vpassword:
                return render_template('register.html', nomatch=True)

            # valid login
            else:
                return render_template('index.html', username=username)

        # coming from login page
        elif len(request.form) is 0:
            return render_template('register.html')
            

if __name__ == '__main__':
    import click

    @click.command()
    @click.option('--debug', is_flag=True)
    @click.option('--threaded', is_flag=True)
    @click.argument('HOST', default='0.0.0.0')
    @click.argument('PORT', default=4156, type=int)
    def run(debug, threaded, host, port):
        '''
        This function handles command line parameters.
        Run the app using:

            python app.py

        Show the help text using:
        
            python app.py --help
        
        '''
        HOST, PORT = host, port
        print 'running on %s:%d' % (HOST, PORT)
        app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

    run()

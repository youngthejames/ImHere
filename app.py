#!/usr/bin/env python2.7

import os
import httplib2
import uuid
import json

import oauth2client
import apiclient
import flask
import sqlalchemy

from sqlalchemy import *
# from sqlalchemy.pool import NullPool
from flask import Flask, render_template, request, g

from models import users_model

tmpl_dir = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'templates')
app = Flask(__name__, template_folder=tmpl_dir)

engine = create_engine(
    'postgres://cwuepekp:SkVXF4KcwLJvTNKT41e7ruWQDcF3OSEU@jumbo.db.elephantsql.com:5432/cwuepekp')


@app.before_request
def before_request():
    try:
        g.conn = engine.connect()
    except:
        print 'uh oh, problem connecting to database'
        import traceback
        traceback.print_exc()
        g.conn = None


# make sure user is authenticated w/ live session on every protected request
@app.before_request
def manage_session():
    # want to go through oauth flow for this route specifically
    # not get stuck in redirect loop
    if(request.path == '/oauth2callback'):
        return
    # want to allow users to public pages without a session
    if('protected' not in request.path):
        return
    # validate that user has valid session
    # add the google user info into session
    if 'credentials' not in flask.session:
        return flask.redirect(flask.url_for('oauth2callback'))

    credentials = oauth2client.client.OAuth2Credentials.from_json(
        flask.session['credentials'])
    if credentials.access_token_expired:
        return flask.redirect(flask.url_for('oauth2callback'))
    else:
        # use token to get user profile from google oauth api
        http_auth = credentials.authorize(httplib2.Http())
        userinfo_client = apiclient.discovery.build('oauth2', 'v2', http_auth)
        user = userinfo_client.userinfo().v2().me().get().execute()

        if 'columbia.edu' not in user['email']:
            return flask.redirect(flask.url_for('bademail'))

        um = users_model.Users(g.conn)

        flask.session['google_user'] = user
        flask.session['id'] = um.get_or_create_user(user)


@app.teardown_request
def teardown_request(exception):
    try:
        g.conn.close()
    except Exception as e:
        print e


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        if 'credentials' not in flask.session:
            return render_template('login.html')
        else:
            return render_template('main_student.html')
    elif request.method == 'POST':
        return flask.redirect(flask.url_for('protected'))


@app.route('/protected')
def protected():
    return flask.redirect(flask.url_for('index'))
    # return json.dumps(flask.session['google_user'])


@app.route('/bademail')
def bademail():
    return 'only columbia.edu email address accepted'


@app.route('/oauth/callback')
def oauth2callback():
    flow = oauth2client.client.flow_from_clientsecrets(
        'client_secrets.json',
        scope=[
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/userinfo.profile'],
        redirect_uri=flask.url_for('oauth2callback', _external=True))
    if 'code' not in flask.request.args:
        auth_uri = flow.step1_get_authorize_url()
        return flask.redirect(auth_uri)
    else:
        auth_code = flask.request.args.get('code')
        credentials = flow.step2_exchange(auth_code)
        flask.session['credentials'] = credentials.to_json()
        return flask.redirect(flask.url_for('protected'))


@app.route('/oauth/logout')
def logout():
    flask.session.clear()
    return flask.redirect(flask.url_for('index'))

'''
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
'''

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
        app.secret_key = str(uuid.uuid4())
        app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

    run()

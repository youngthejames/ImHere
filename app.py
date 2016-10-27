#!/usr/bin/env python2.7

import os
import httplib2
import uuid
import json

import oauth2client
import apiclient
import flask
import sqlalchemy
import random

from sqlalchemy import *
# from sqlalchemy.pool import NullPool
from flask import Flask, render_template, request, g
from datetime import datetime, date

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
        flask.session['redirect'] = request.path
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
            return flask.redirect(flask.url_for('main_teacher'))
    elif request.method == 'POST':
        return flask.redirect(flask.url_for('protected'))


@app.route('/protected/main_student', methods=['GET', 'POST'])
def main_student():

        # find relevant classes to user
        classes = []
        query = ('select courses.cid, courses.name, courses.start_time, '
                'courses.end_time, courses.start_date, courses.end_date, '
                'courses.day, courses.active, enrolled_in.sid '
                'from courses, enrolled_in '
                'where courses.cid = enrolled_in.cid '
                "and enrolled_in.sid = '%s'"
                % flask.session['id'])

        cursor = g.conn.execute(query)

        # result references each of the fields below
        for result in cursor:
            classes.append(result)

        cursor.close()
        context = dict(data = classes)

        # if in here, check if secret code matches
	if 'secret_code' in request.form.keys():
            secret_code = request.form['secret_code']
            now = datetime.time(datetime.now())
            today = date.today()

            query = ('select seid '
                     'from session, enrolled_in '
                     "where enrolled_in.sid = '%s' "
                     'and enrolled_in.cid = session.cid '
                     "and session.expires > '%s' "
                     "and session.day >= '%s'"
                     % (flask.session['id'], now, today))

            cursor = g.conn.execute(query)

            for result in cursor:
                seid = result[0]

            query = "select secret from session where seid = '%s'" % seid
            cursor = g.conn.execute(query)

            for result in cursor:
                actual_secret = result[0]

            if actual_secret == secret_code:

                # create attendance record here
                g.conn.execute("insert into attendance_record values ('%s', '%s')" % (flask.session['id'], seid))
                return render_template('main_student.html', correct = True, **context)
            else:
                return render_template('main_student.html', incorrect = True, **context)

        # looking at the page before a secret code has been submitted
        else:
            return render_template('main_student.html', **context)


@app.route('/protected/main_teacher', methods=['GET', 'POST'])
def main_teacher():

    now = datetime.time(datetime.now())
    today = date.today()

    if request.method=="POST":
        if "close" in request.form.keys():
            cid = request.form["close"]
            g.conn.execute("update session set expires = '%s' where session.cid = '%s'" % (now, cid))
            #g.conn.execute("update session set day = '%s' where session.cid = '%s'" % (today, cid))
            g.conn.execute("update courses set active = 0 where courses.cid = '%s'" % cid)

        elif "open" in request.form.keys():
            cid = request.form["open"]
            g.conn.execute("update courses set active = 1 where courses.cid = '%s'" % cid)
            randseid = random.randint(1, 1000)
            randsecret = random.randint(1000, 9999)
            print randseid
            print randsecret
            print cid

            print type(cid)
            g.conn.execute("insert into session values (%d, %s, '%d', '%s', '%s')" % (randseid, cid, randsecret, '23:59:59', today))
            print 'after execute'


    classes = []
    query = ('select courses.cid, name, active, secret '
             'from teaches inner join courses on '
             '(courses.cid = teaches.cid and '
             "teaches.tid = '%s') "
             'left outer join session on '
             '(courses.cid = session.cid and '
             "session.expires > '%s' and "
             "session.day >= '%s')"
             % (flask.session['id'], now, today))

    cursor = g.conn.execute(query)

    for result in cursor:
        classes.append(result)
    cursor.close()

    context = dict(data = classes)

    return render_template('main_teacher.html', **context)


@app.route('/protected/add_class')
def add_class():
    if request.method == "GET":
        return render_template('add_class.html')
    elif request.method =="POST":
        c_name = request.form['classname']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        latest_cid = g.conn.execute("select max(cid) from courses;")[0] + 1
        query = "insert into courses values(%d, %s, %s, %s, None, None, None, False);" % (latest_cid, request.form["name"], start_time, end_time)
        g.conn.execute(query)
        query = "insert into teaches(tid, sid) values(%s, %d);" % (flask.session['id'], latest_cid)
        g.conn.execute(query)
        for line in request.form['students']:
            if re.match(".*@columbia.edu", line):
                query = "select sid from students where name = %s;" %(line)
                cursor = g.conn.execute(query)
                for sid in cursor:
                    q2 = "insert into enrolled_in(cid, sid) values(%d, %d);" % (latest_cid, sid)


@app.route('/protected')
def protected():
    return flask.redirect(flask.url_for('index'))
    # return json.dumps(flask.session['google_user'])

@app.route('/protected/register', methods=['GET', 'POST'])
def register():

    if request.method == 'GET':
        return render_template('register.html', name=flask.session['google_user']['name'])
    else:
        if request.form['type'] == 'student':
            try:
                query = '''
                insert into students (sid, uni) values({0}, '{1}')
                '''.format(flask.session['id'], request.form['uni']);
                g.conn.execute(query)
            except:
                pass
            return flask.redirect(flask.url_for('main_student'))
        else:
            try:
                query = '''
                insert into teachers (tid) values({0})
                '''.format(flask.session['id'])
                g.conn.execute(query)
            except:
                pass
            # return flask.redirect(flask.url_for('main_teacher'))
            return flask.redirect(flask.url_for('index'))




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
        redirect = flask.session['redirect']
        flask.session.pop('redirect', None)
        return flask.redirect(redirect)


@app.route('/oauth/logout')
def logout():
    flask.session.clear()
    return flask.redirect(flask.url_for('index'))


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

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
from flask import Flask, render_template, request, g
from datetime import datetime, date

from models import users_model, students_model, index_model

tmpl_dir = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'templates')
app = Flask(__name__, template_folder=tmpl_dir)

engine = create_engine(('postgres://'
                        'cwuepekp:SkVXF4KcwLJvTNKT41e7ruWQDcF3OSEU'
                        '@jumbo.db.elephantsql.com:5432'
                        '/cwuepekp'))


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

        #if 'columbia.edu' not in user['email']:
        #    return flask.redirect(flask.url_for('bademail'))

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
            im = index_model.Index(g.conn, flask.session['id'])
            if im.is_student() and im.is_teacher():
                #TODO: allow for switching between student/teacher pages
                pass
            elif im.is_student():
                return flask.redirect(flask.url_for('main_student'))
            elif im.is_teacher():
                return flask.redirect(flask.url_for('main_teacher'))
            else:
                return render_template('login.html', not_registered=True)

    elif request.method == 'POST':
        return flask.redirect(flask.url_for('protected'))


@app.route('/protected/main_student', methods=['GET', 'POST'])
def main_student():

    sm = students_model.Students(g.conn, flask.session['id'])
    classes = sm.get_classes()

    context = dict(data=classes)

    if request.method == 'GET':
        return render_template('main_student.html', first=True, **context)

    elif request.method == 'POST':
        if 'secret_code' in request.form.keys():
            provided_secret = request.form['secret_code']
            actual_secret, seid = sm.get_secret_and_seid()

            if provided_secret == actual_secret:
                sm.insert_attendance_record(seid)
                valid = True
            else:
                valid = False
                
            return render_template(
                    'main_student.html',
                    valid=valid,
                    **context)
        else:
            # unreachable
            pass


@app.route('/protected/main_teacher', methods=['GET', 'POST'])
def main_teacher():

    now = datetime.time(datetime.now())
    today = date.today()

    if request.method == 'POST':

        if "close" in request.form.keys():

            cid = request.form["close"]

            query = ("update sessions set expires = '%s' "
                     "where sessions.cid = '%s'"
                     % (now, cid))
            g.conn.execute(query)

            query = "update courses set active = 0 where courses.cid = '%s'" \
                    % cid
            g.conn.execute(query)

        elif "open" in request.form.keys():

            cid = request.form["open"]

            query = "update courses set active = 1 where courses.cid = '%s'" \
                    % cid
            g.conn.execute(query)

            # generate a random secret 4-digit int for a session
            randsecret = random.randint(1000, 9999)
            query = ('insert into sessions (cid, secret, expires, day) '
                     "values (%s, '%d', '%s', '%s')"
                     % (cid, randsecret, '23:59:59', today))
            g.conn.execute(query)

    # find relevant classes and their valid sessions
    classes = []
    query = ('select courses.cid, name, active, secret '
             'from teaches inner join courses on '
             '(courses.cid = teaches.cid and '
             "teaches.tid = '%s') "
             'left outer join sessions on '
             '(courses.cid = sessions.cid and '
             "sessions.expires > '%s' and "
             "sessions.day >= '%s')"
             % (flask.session['id'], now, today))

    cursor = g.conn.execute(query)

    empty = True if cursor.rowcount == 0 else False

    for result in cursor:
        classes.append(result)
    cursor.close()

    context = dict(data=classes)

    return render_template('main_teacher.html', empty=empty, **context)


@app.route('/protected/add_class', methods=['POST', 'GET'])
def add_class():

    if request.method == 'GET':
        return render_template('add_class.html')

    elif request.method == 'POST':

        classname = request.form['classname']
        query = "insert into courses (name, active) values('%s', 0)" % classname
        g.conn.execute(query)

        # after we add course that generated a serial cid,
        # we need to get the cid
        #TODO: ensure the class selected is correct (e.g. class name conflict)
        query = "select cid from courses where name = '%s'" % classname
        cursor = g.conn.execute(query)
        result = cursor.fetchone()
        cid = result[0]

        query = 'insert into teaches values(%s, %d)' \
                % (flask.session['id'], cid)
        g.conn.execute(query)

        # parse text area for all student UNI's
        for line in request.form['unis'].split('\n'):
            line = line.strip('\r')

            query = "select sid from students where uni = '%s'" % (line)
            cursor = g.conn.execute(query)

            if cursor.rowcount == 1:
                # found a student with that sid
                result = cursor.fetchone()
                sid = result[0]

                try:
                    query = 'insert into enrolled_in values(%d, %d)' \
                            % (sid, cid)
                    g.conn.execute(query)
                except:
                    # insert failed because already in class??
                    pass
            else:
                # no student with that sid found
                # notify teacher that their submission didn't work
                pass

        return flask.redirect(flask.url_for('main_teacher'))


@app.route('/protected/remove_class', methods=['POST', 'GET'])
def remove_class():
    
    if request.method == 'GET':
        classes = []
        query = ('select courses.cid, courses.name '
                 'from courses, teaches '
                 'where courses.cid = teaches.cid '
                 'and teaches.tid = %s'
                 % flask.session['id'])
        cursor = g.conn.execute(query)

        for result in cursor:
            classes.append(result)

        context = dict(data=classes)

        return render_template('remove_class.html', **context)

    elif request.method == 'POST':

        # cid to be removed
        cid = request.form['cid']

        query = ('delete from teaches '
                 'where cid = %s '
                 'and tid = %s'
                 % (cid, flask.session['id']))
        g.conn.execute(query)

        return flask.redirect(flask.url_for('index'))


@app.route('/protected/view_class', methods=['POST', 'GET'])
def view_class():

    if request.method == 'POST':
        cid = request.form['cid']

        if 'add_student' in request.form.keys():
            uni = request.form['add_student']

            query = "select sid from students where uni = '%s'" % uni
            cursor = g.conn.execute(query)

            if cursor.rowcount == 1:
                result = cursor.fetchone()
                sid = result[0]

                try:
                    query = 'insert into enrolled_in values (%s, %s)' \
                            % (sid, cid)
                    g.conn.execute(query)
                except:
                    # execute failed because student already in enrolled_in??
                    pass

                    
            else:
                # no student with that sid found
                pass

        elif 'remove_student' in request.form.keys():
            uni = request.form['remove_student']

            query = "select sid from students where uni = '%s'" % uni
            cursor = g.conn.execute(query)

            if cursor.rowcount == 1:
                result = cursor.fetchone()
                sid = result[0]

                try:
                    query = ('delete from enrolled_in '
                             'where sid = %s '
                             'and cid = %s'
                             % (sid, cid))
                    g.conn.execute(query)
                    #TODO: delete all AR's of this class of student
                except:
                    #TODO: delete failed because sid not in enrolled_in
                    pass
            else:
                # failed because UNI not found in students
                pass

        query = 'select name from courses where cid = %s' % cid
        cursor = g.conn.execute(query)

        result = cursor.fetchone()
        cname = result[0]

        query = ('select name, family_name, email '
                 'from users, enrolled_in '
                 'where users.uid = enrolled_in.sid '
                 'and enrolled_in.cid = %s'
                 % cid)
        cursor = g.conn.execute(query)

        students = []
        for result in cursor:
            students.append(result)
        cursor.close()

        context = dict(data=students)

        return render_template(
                'view_class.html',
                cid=cid,
                cname=cname,
                **context)

    elif request.method == 'GET':
        return flask.redirect(flask.url_for('index'))


@app.route('/protected')
def protected():
    return flask.redirect(flask.url_for('index'))


@app.route('/protected/register', methods=['GET', 'POST'])
def register():

    if request.method == 'GET':
        return render_template(
                'register.html',
                name=flask.session['google_user']['name'])

    elif request.method == 'POST':

        if request.form['type'] == 'student':
            try:
                query = '''
                insert into students (sid, uni) values({0}, '{1}')
                '''.format(flask.session['id'], request.form['uni'])
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

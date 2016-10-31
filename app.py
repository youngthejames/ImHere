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
from flask import Flask, render_template, request, g

from models import users_model, index_model, teachers_model, students_model, courses_model

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

        # if 'columbia.edu' not in user['email']:
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
                # TODO: allow for switching between student/teacher pages
                # for now, just redirect to teacher
                return flask.redirect(flask.url_for('main_teacher'))
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
    courses = sm.get_courses()
    context = dict(data=courses)

    mylist = [1,2,3,4]

    if request.method == 'GET':
        return render_template('main_student.html', first=True, mylist=mylist, **context)

    elif request.method == 'POST':
        if 'secret_code' in request.form.keys():
            provided_secret = request.form['secret_code']
            actual_secret, seid = sm.get_secret_and_seid()

            if provided_secret == actual_secret:
                sm.insert_attendance_record(seid)
                valid = True
            else:
                valid = False

            return render_template('main_student.html', valid=valid, **context)


@app.route('/protected/main_teacher', methods=['GET', 'POST'])
def main_teacher():
    tm = teachers_model.Teachers(g.conn, flask.session['id'])

    if request.method == 'POST':
        if "close" in request.form.keys():
            cid = request.form["close"]
            tm.close_session(cid)
        elif "open" in request.form.keys():
            cid = request.form["open"]
            tm.open_session(cid)

    courses = tm.get_courses_with_session()
    empty = True if len(courses) == 0 else False
    context = dict(data=courses)

    return render_template('main_teacher.html', empty=empty, **context)


@app.route('/protected/add_class', methods=['POST', 'GET'])
def add_class():
    tm = teachers_model.Teachers(g.conn, flask.session['id'])

    if request.method == 'GET':
        return render_template('add_class.html')

    elif request.method == 'POST':
        course_name = request.form['classname']
        cid = tm.add_course(course_name)

        cm = courses_model.Courses(g.conn, cid)
        for uni in request.form['unis'].split('\n'):
            uni = uni.strip('\r')
            cm.add_student(uni)

        return flask.redirect(flask.url_for('main_teacher'))


@app.route('/protected/remove_class', methods=['POST', 'GET'])
def remove_class():
    tm = teachers_model.Teachers(g.conn, flask.session['id'])

    # show potential courses to remove on get request
    if request.method == 'GET':
        courses = tm.get_courses()
        context = dict(data=courses)
        return render_template('remove_class.html', **context)

    # remove course by cid
    elif request.method == 'POST':
        cid = request.form['cid']
        tm.remove_course(cid)
        return flask.redirect(flask.url_for('index'))


@app.route('/protected/view_class', methods=['POST', 'GET'])
def view_class():
    tm = teachers_model.Teachers(g.conn, flask.session['id'])

    if request.method == 'GET':
        flask.redirect(flask.url_for('index'))

    elif request.method == 'POST':
        if 'close' in request.form.keys():
            cid = request.form['close']
            tm.close_session(cid)
        elif 'open' in request.form.keys():
            cid = request.form['open']
            tm.open_session(cid)
        else:
            cid = request.form['cid']

        cm = courses_model.Courses(g.conn, cid)
        if 'add_student' in request.form.keys():
            uni = request.form['add_student']
            cm.add_student(uni)
        elif 'remove_student' in request.form.keys():
            uni = request.form['remove_student']
            cm.remove_student(uni)

        courses = tm.get_courses_with_session()

        course_name = cm.get_course_name()
        students = cm.get_students()
        empty_class = True if len(students) == 0 else False
        context = dict(data=students, courses=courses)

        return render_template(
                'view_class.html',
                cid=cid,
                course_name=course_name,
                empty_class=empty_class,
                **context)


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

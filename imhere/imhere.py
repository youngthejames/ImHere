#!/usr/bin/env python2.7

import os
import httplib2
import uuid

import oauth2client
import apiclient
import flask

from sqlalchemy import *
from flask import Flask, render_template, request, g

from models import users_model, index_model, teachers_model, students_model, \
    courses_model, sessions_model

tmpl_dir = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'templates')
app = Flask(__name__, template_folder=tmpl_dir)


@app.before_request
def before_request():
    try:
        g.conn = app.config['db'].connect()
    except:
        print 'uh oh, problem connecting to database'
        import traceback
        traceback.print_exc()
        g.conn = None


@app.before_request
def teacher_session():
    if '/teacher/' in request.path:
        if 'credentials' not in flask.session:
            return flask.redirect(flask.url_for('index'))
        elif not flask.session['is_teacher']:
            return flask.redirect(flask.url_for('register'))


@app.before_request
def student_session():
    if '/student/' in request.path:
        if 'credentials' not in flask.session:
            return flask.redirect(flask.url_for('index'))
        elif not flask.session['is_student']:
            return flask.redirect(flask.url_for('register'))


# make sure user is authenticated w/ live session on every request
@app.before_request
def manage_session():
    # want to go through oauth flow for this route specifically
    # not get stuck in redirect loop
    if request.path == '/oauth/callback':
        return

    # allow all users to visit the index page without a session
    if request.path == '/' or request.path == '/oauth/logout' or '/static/' in request.path:
        return

    # validate that user has valid session
    # add the google user info into session
    if 'credentials' not in flask.session:
        flask.session['redirect'] = request.path
        return flask.redirect(flask.url_for('oauth2callback'))

    #TODO: add token expired checking
    # credentials = oauth2client.client.OAuth2Credentials.from_json(
    #     flask.session['credentials'])
    # if credentials.access_token_expired:
    #     return flask.redirect(flask.url_for('oauth2callback'))


@app.teardown_request
def teardown_request(exception):
    try:
        g.conn.close()
    except Exception as e:
        print e


@app.route('/switch_type', methods=['POST'])
def switch_type():
    im = index_model.Index(g.conn, flask.session['id'])
    if request.form['type'] == 'teacher':
        if im.is_teacher():
            return flask.redirect(flask.url_for('main_teacher'))
        else:
            return flask.redirect(flask.url_for('register'))

    elif request.form['type'] == 'student':
        if im.is_student():
            return flask.redirect(flask.url_for('main_student'))
        else:
            return flask.redirect(flask.url_for('register'))


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('login.html')


@app.route('/login', methods=['GET', 'POST'])
def login():

    im = index_model.Index(g.conn, flask.session['id'])
    # TODO: allow for student/teacher redirects
    if im.is_student():
        return flask.redirect(flask.url_for('main_student'))
    elif im.is_teacher():
        return flask.redirect(flask.url_for('main_teacher'))
    else:
        return render_template('login.html', not_registered=True)


@app.route('/student/', methods=['GET', 'POST'])
def main_student():
    sm = students_model.Students(g.conn, flask.session['id'])
    courses = sm.get_courses()
    context = dict(data=courses)

    signed_in = True if sm.has_signed_in() else False

    if request.method == 'GET':
        return render_template(
                'main_student.html',
                signed_in=signed_in,
                **context)

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
                    submitted=True,
                    valid=valid,
                    **context)
        else:
            return render_template('main_student.html',
                signed_in=signed_in,
                **context)

@app.route('/student/view_class/<cid>', methods=['GET'])
def student_view_class(cid):
    cm = courses_model.Courses(g.conn, cid)
    sm = students_model.Students(g.conn, flask.session['id'])

    course_name = cm.get_course_name()
    attendance_record = sm.get_attendance_record(cid)
    present = 0
    total = len(attendance_record)
    for rec in attendance_record:
        if rec['sid'] is not None:
            present += 1

    flask.session['redirect'] = '/student/view_class/%s' % cid

    return render_template('student_view_class.html',
        course_name=course_name, attendance_record=attendance_record,
        present=present, total=total)

@app.route('/student/request/<seid>', methods=['POST'])
def student_change_request(seid):
    sm = students_model.Students(g.conn, flask.session['id'])

    message = request.form['message'] or ''

    sm.create_change_request(seid, message)

    redirect = flask.session.pop('redirect', None)

    return flask.redirect(redirect or '/student/')

@app.route('/teacher/', methods=['GET', 'POST'])
def main_teacher():
    tm = teachers_model.Teachers(g.conn, flask.session['id'])

    if request.method == 'POST':
        cm = courses_model.Courses(g.conn)
        if "close" in request.form.keys():
            cid = request.form["close"]
            cm.cid = cid
            cm.close_session(cm.get_active_session())
        elif "open" in request.form.keys():
            cid = request.form["open"]
            cm.cid = cid
            cm.open_session()

    courses = tm.get_courses_with_session()
    empty = True if len(courses) == 0 else False
    context = dict(data=courses)

    return render_template('main_teacher.html', empty=empty, **context)


@app.route('/teacher/add_class', methods=['POST', 'GET'])
def add_class():
    tm = teachers_model.Teachers(g.conn, flask.session['id'])

    if request.method == 'GET':
        return render_template('add_class.html')

    elif request.method == 'POST':
        # first check that all unis are valid
        um = users_model.Users(g.conn)
        for uni in request.form['unis'].split('\n'):
            uni = uni.strip('\r')
            # always reads at least one empty line from form
            if not uni:
                continue
            if not um.is_valid_uni(uni):
                return render_template('add_class.html', invalid_uni=True)

        # then create course and add students to course
        course_name = request.form['classname']
        cid = tm.add_course(course_name)
        cm = courses_model.Courses(g.conn, cid)

        for uni in request.form['unis'].split('\n'):
            uni = uni.strip('\r')
            cm.add_student(uni)

        return flask.redirect(flask.url_for('main_teacher'))


@app.route('/teacher/remove_class', methods=['POST', 'GET'])
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
        return flask.redirect(flask.url_for('main_teacher'))


@app.route('/teacher/view_class', methods=['POST', 'GET'])
def view_class():
    if request.method == 'GET':
        flask.redirect(flask.url_for('main_teacher'))

    elif request.method == 'POST':
        cm = courses_model.Courses(g.conn)

        if 'close' in request.form.keys():
            cid = request.form['close']
            cm.cid = cid
            cm.close_session(cm.get_active_session())
        elif 'open' in request.form.keys():
            cid = request.form['open']
            cm.cid = cid
            cm.open_session()
        else:
            cid = request.form['cid']
            cm.cid = cid

        res = 0
        uni = None
        if 'add_student' in request.form.keys():
            uni = request.form['add_student']
            res = cm.add_student(uni)
        elif 'remove_student' in request.form.keys():
            uni = request.form['remove_student']
            res = cm.remove_student(uni)

        if 'add_teacher' in request.form.keys():
            res = cm.add_teacher(request.form['email'])

        if 'remove_teacher' in request.form.keys():
            cm.remove_teacher(request.form['remove_teacher'])

        course_name = cm.get_course_name()
        secret = cm.get_secret_code()
        num_sessions = cm.get_num_sessions()
        students = cm.get_students()
        students_with_ar = []
        for student in students:
            sm = students_model.Students(g.conn, student[0])
            student_uni = sm.get_uni()
            num_ar = sm.get_num_attendance_records(cid)
            students_with_ar.append([student, student_uni, num_ar])

        teachers = cm.get_teachers()

        sessions = cm.get_sessions()

        context = dict(students=students_with_ar)

        return render_template(
                'view_class.html',
                cid=cid,
                secret=secret,
                course_name=course_name,
                num_sessions=num_sessions,
                uni=uni,
                res=res,
                teachers=teachers,
                userid=flask.session['id'],
                sessions=sessions,
                **context)


@app.route('/teacher/view_requests/', methods=['GET', 'POST'])
def view_requests():
    tm = teachers_model.Teachers(g.conn, flask.session['id'])
    if request.method == 'GET':
        results = tm.get_change_requests()
        context = dict(data=results)
        return render_template('view_requests.html', **context)
    elif request.method == 'POST':
        if 'approve' in request.form.keys():
            iden = request.form['approve'].split()
            seid = int(iden[0])
            sid = int(iden[1])
            sm = students_model.Students(g.conn, sid)
            sm.insert_attendance_record(seid)
            tm.update_change_request(1, seid, sid)
        elif 'deny' in request.form.keys():
            iden = request.form['deny'].split()
            seid = int(iden[0])
            sid = int(iden[1])
            tm.update_change_request(-1, seid, sid)
        results = tm.get_change_requests()
        context = dict(data=results)
        return render_template('view_requests.html', **context)

@app.route('/teacher/sessions/<seid>', methods=['GET'])
def view_session(seid):
    sm = sessions_model.Sessions(g.conn, seid)
    session = sm.get_session()[0]
    attendance = sm.get_attendance_record()

    return render_template('session.html',
        session=session, attendance=attendance)

@app.route('/teacher/sessions/<seid>', methods=['POST'])
def update_session(seid):
    sm = sessions_model.Sessions(g.conn, seid)
    tm = teachers_model.Teachers(g.conn, flask.session['id'])

    action = request.form['action']
    sid = request.form['sid'] if 'sid' in request.form.keys() else None

    stm = students_model.Students(g.conn, sid)

    if action == 'mark_present':
        stm.insert_attendance_record(seid)

    elif action == 'mark_absent':
        sm.remove_attendance_record(sid)

    elif action == 'approve':
        status = 1
        tm.update_change_request(int(status), int(seid), int(sid))
        stm.insert_attendance_record(seid)

    elif action == 'deny':
        status = 0
        tm.update_change_request(int(status), int(seid), int(sid))

    elif action == 'delete_session':
        sm.delete_session()
        return flask.redirect('/teacher/')

    session = sm.get_session()[0]
    attendance = sm.get_attendance_record()

    return render_template('session.html',
        session=session, attendance=attendance)


    # mark present

    # mark absent

    # update change request
        # approve or deny
        # status = 1 -> approve
            # create attendance record


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template(
                'register.html',
                name=flask.session['google_user']['name'],
                is_student=flask.session['is_student'],
                is_teacher=flask.session['is_teacher'])

    elif request.method == 'POST':
        if request.form['type'] == 'student':
            # check that uni doesn't already exist
            # if it doesn't, continue student creation
            um = users_model.Users(g.conn)
            if not um.is_valid_uni(request.form['uni']):
                query = '''
                insert into students (sid, uni) values({0}, '{1}')
                '''.format(flask.session['id'], request.form['uni'])
                g.conn.execute(query)
                flask.session['is_student'] = True
                return flask.redirect(flask.url_for('main_student'))
            else:
                return render_template(
                        'register.html',
                        name=flask.session['google_user']['name'],
                        invalid_uni=True)

        else:
            try:
                query = '''
                insert into teachers (tid) values({0})
                '''.format(flask.session['id'])
                g.conn.execute(query)
                flask.session['is_teacher'] = True
            except:
                pass
            return flask.redirect(flask.url_for('main_teacher'))


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

        # use token to get user profile from google oauth api
        http_auth = credentials.authorize(httplib2.Http())
        userinfo_client = apiclient.discovery.build('oauth2', 'v2', http_auth)
        user = userinfo_client.userinfo().v2().me().get().execute()

        # if 'columbia.edu' not in user['email']:
        #    return flask.redirect(flask.url_for('bademail'))

        um = users_model.Users(g.conn)

        flask.session['google_user'] = user
        flask.session['id'] = um.get_or_create_user(user)

        # now add is_student and is_teacher to flask.session
        im = index_model.Index(g.conn, flask.session['id'])
        flask.session['is_student'] = True if im.is_student() else False
        flask.session['is_teacher'] = True if im.is_teacher() else False

        redirect = flask.session['redirect']
        flask.session.pop('redirect', None)
        return flask.redirect(redirect)


@app.route('/oauth/logout', methods=['POST', 'GET'])
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
        PORT = int(os.environ.get('PORT') or PORT)
        print 'running on %s:%d' % (HOST, PORT)
        app.secret_key = str(uuid.uuid4())
        app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

    run()

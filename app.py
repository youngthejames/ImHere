#!/usr/bin/env python2.7

import os
from flask import Flask, render_template, request, g

tmpl_dir = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'templates')
app = Flask(__name__, template_folder=tmpl_dir)


@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'GET':
        return render_template('login.html')
        #return redirect('/login')
    else:
        return render_template('index.html')


@app.route('/login')
def login():
    return render_template('login.html')


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

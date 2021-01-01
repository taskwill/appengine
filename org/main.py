from flask import Flask, render_template
import os

app = Flask(__name__)

@app.before_request
def sorry():
    maintenance = False
    if maintenance:
        return 'Sorry. The service is temporarily unavailable.', 503

static = '/static'
db_user = os.environ.get('CLOUD_SQL_USERNAME')
db_password = os.environ.get('CLOUD_SQL_PASSWORD')
db_name = 'org'
db_connection_name = os.environ.get('CLOUD_SQL_CONNECTION_NAME')

@app.route('/')
def index(): return render_template('oindex.html', static=static)

# list, filter, search, mine, post, work

if __name__ == '__main__': app.run(host='127.0.0.1', port=8080, debug=True)
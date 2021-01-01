import firebase_admin, os, sqlalchemy, datetime, sqlalchemy, pandas as pd, random, numpy as np, sys
from uuid import uuid4
from flask import request as req, jsonify
from firebase_admin import auth
from paypalcheckoutsdk.core import PayPalHttpClient, SandboxEnvironment

def uuid(): return uuid4().hex

def user_id():
    try: return auth.verify_id_token(req.headers['Authorization'].split(' ').pop())['uid']
    except: return None

def safe(contents): return contents.replace('script', 'scrypt')

db_user = os.environ.get('CLOUD_SQL_USERNAME')
db_password = os.environ.get('CLOUD_SQL_PASSWORD')
db_name = 'main'
db_connection_name = os.environ.get('CLOUD_SQL_CONNECTION_NAME')
firebase_admin.initialize_app(options={'projectId': 'taskwill'})
if os.environ.get('GAE_ENV') == 'standard':
    query = {'unix_socket': '/cloudsql/{}'.format(db_connection_name)}
    url = sqlalchemy.engine.url.URL(drivername='mysql+pymysql', username=db_user, password=db_password, database=db_name, query=query)
else:
    url = sqlalchemy.engine.url.URL(drivername='mysql+pymysql', username=db_user, password=db_password, database=db_name, host='127.0.0.1')
db = sqlalchemy.create_engine(url, pool_size=5, max_overflow=2, pool_timeout=30, pool_recycle=1800)

class PayPalClient:
    def __init__(self):
        sandbox = True
        if sandbox:
            self.client_id = ''
            self.client_secret = ''
            self.environment = SandboxEnvironment(client_id=self.client_id, client_secret=self.client_secret)
        else: 
            self.client_id = ''
            self.client_secret = ''
            self.environment = LiveEnvironment(client_id=self.client_id, client_secret=self.client_secret)
        self.client = PayPalHttpClient(self.environment)
    
    def object_to_json(self, json_data):
        result = {}
        if sys.version_info[0] < 3: itr = json_data.__dict__.iteritems()
        else: itr = json_data.__dict__.items()
        for key,value in itr:
            if key.startswith("__"): continue
            result[key] = self.array_to_json_array(value) if isinstance(value, list) else\
                        self.object_to_json(value) if not self.is_primittive(value) else value
        return result
    
    def array_to_json_array(self, json_array):
        result =[]
        if isinstance(json_array, list):
            for item in json_array:
                result.append(self.object_to_json(item) if  not self.is_primittive(item) \
                              else self.array_to_json_array(item) if isinstance(item, list) else item)
        return result
    
    def is_primittive(self, data):
        return isinstance(data, str) or isinstance(data, unicode) or isinstance(data, int)
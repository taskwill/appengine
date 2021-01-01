from handlers.common import uuid, user_id, jsonify, db, req, datetime, safe, sqlalchemy

def create_request():
    with db.connect() as conn:
        stmt = sqlalchemy.text('INSERT INTO requests(request_id, user_id) VALUES (:request_id, :user_id)')
        conn.execute(stmt, request_id=uuid(), user_id=user_id())
    return jsonify(success=True)

def fetch_requests():
    before = req.values.get('before')
    before = before.replace('T', ' ').replace('Z', '')
    source = req.values.get('source')
    source = '!(removed IS NULL)' if source == 'trash' else 'removed IS NULL'
    with db.connect() as conn:
        stmt = sqlalchemy.text('SELECT request_id, contents, created FROM requests WHERE user_id=:user_id AND ' + source + ' AND deleted IS NULL '
                               'AND created < :before ORDER BY created DESC LIMIT 50')
        requests = conn.execute(stmt, user_id=user_id(), before=before).fetchall()
    return jsonify([{'request_id': request[0], 'contents': request[1], 'created': request[2].strftime('%Y-%m-%dT%H:%M:%S.%fZ')} for request in requests])

def fetch_payments():
    request_id = req.values.get('request_id')
    now = datetime.datetime.utcnow()
    with db.connect() as conn:
        stmt = sqlalchemy.text('SELECT payment_id, created, amount, hour, deadline, canceled from payments WHERE request_id=:request_id AND '
                               ':user_id IN (SELECT user_id FROM requests WHERE request_id=:request_id) ORDER BY created')
        data = conn.execute(stmt, request_id=request_id, user_id=user_id()).fetchall()
    payments = [{'payment_id': item[0], 'created': item[1].strftime('%Y-%m-%dT%H:%M:%S.%fZ'), 'twc': item[2]//100, 'hour': item[3],
                 'refundable': item[4] > now and not item[5]} for item in data]
    return jsonify(payments)

def active_requests(): # not used
    with db.connect() as conn:
        stmt = sqlalchemy.text('SELECT request_id, contents, created FROM requests WHERE user_id=:user_id AND removed IS NULL AND deleted IS NULL '
                               'AND 0 < (SELECT COUNT(*) FROM payments WHERE payments.request_id=requests.request_id AND deadline > current_timestamp(6) '
                               'AND canceled IS NULL) ORDER BY created DESC')
        requests = conn.execute(stmt, user_id=user_id()).fetchall()
    return jsonify([{'request_id': request[0], 'contents': request[1], 'created': request[2].strftime('%Y-%m-%dT%H:%M:%S.%fZ')} for request in requests])

def search_requests():
    query = req.values.get('query').replace("　", "").split(' ')
    query = ' '.join(['+'+q for q in query if len(q) > 1])
    with db.connect() as conn:
        stmt = sqlalchemy.text('SELECT request_id, contents, created FROM requests WHERE user_id=:user_id AND deleted IS NULL '
                               'AND MATCH(contents) AGAINST(:query IN BOOLEAN MODE) ORDER BY created DESC')
        requests = conn.execute(stmt, user_id=user_id(), query=query).fetchall()
    return jsonify([{'request_id': request[0], 'contents': request[1], 'created': request[2].strftime('%Y-%m-%dT%H:%M:%S.%fZ')} for request in requests])

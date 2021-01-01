from handlers.common import uuid, user_id, jsonify, db, req, datetime, safe, sqlalchemy

def fetch_request():
    request_id = req.values.get('request_id')
    with db.connect() as conn:
        stmt = sqlalchemy.text('SELECT request_id, contents, removed FROM requests WHERE '
                               'request_id=:request_id AND user_id=:user_id AND deleted IS NULL LIMIT 1')
        request = conn.execute(stmt, user_id=user_id(), request_id=request_id).fetchone()
        stmt = sqlalchemy.text('SELECT contents FROM tasks WHERE request_id=:request_id AND contents IS NOT NULL AND '
                               ':user_id IN (SELECT user_id FROM requests WHERE request_id=:request_id AND user_id=:user_id) ORDER BY created DESC')
        replies = conn.execute(stmt, request_id=request_id, user_id=user_id()).fetchall()
        stmt = sqlalchemy.text('SELECT COUNT(*) FROM payments WHERE :user_id IN (SELECT user_id FROM requests WHERE '
                               'request_id=:request_id AND user_id=:user_id) AND request_id=:request_id '
                               'AND current_timestamp(6) < deadline AND CANCELED IS NULL')
        removable = conn.execute(stmt, user_id=user_id(), request_id=request_id).fetchone()[0] == 0
        stmt = sqlalchemy.text('SELECT COUNT(*) FROM tasks WHERE request_id=:request_id AND '
                               ':user_id IN (SELECT user_id FROM requests WHERE request_id=:request_id)')
        views = conn.execute(stmt, request_id=request_id, user_id=user_id()).fetchone()[0]
        stmt = sqlalchemy.text('SELECT balance FROM users WHERE user_id=:user_id LIMIT 1')
        balance = conn.execute(stmt, user_id=user_id()).fetchone()[0]//100
    if request is None: return jsonify({'exists': False})
    replies = [{'contents': reply[0]} for reply in replies if reply[0].strip()]
    return jsonify({'request_id': request[0], 'contents': request[1], 'removed': request[2],
                    'replies': replies, 'removable': removable, 'views': views, 'exists': True, 'balance': balance})

def remove_request():
    request_id = req.values.get('request_id')
    with db.connect() as conn:
        stmt = sqlalchemy.text('UPDATE requests SET removed=CURRENT_TIMESTAMP(6) WHERE request_id=:request_id AND user_id=:user_id LIMIT 1')
        conn.execute(stmt, request_id=request_id, user_id=user_id())
    return jsonify([{'status': 'successful'}])

def delete_request():
    request_id = req.values.get('request_id')
    with db.connect() as conn:
        stmt = sqlalchemy.text('UPDATE requests SET deleted=CURRENT_TIMESTAMP(6) WHERE request_id=:request_id AND user_id=:user_id LIMIT 1')
        conn.execute(stmt, request_id=request_id, user_id=user_id())
    return jsonify([{'status': 'successful'}])

def update_request():
    request_id = req.values.get('request_id');
    contents = req.values.get('contents');
    with db.connect() as conn:
        stmt = sqlalchemy.text('UPDATE requests SET contents=:contents WHERE request_id=:request_id AND user_id=:user_id LIMIT 1')
        conn.execute(stmt, contents=safe(contents), user_id=user_id(), request_id=request_id)
    return jsonify([{'status': 'successful'}])

def fetch_works():
    request_id = req.values.get('request_id')
    now = datetime.datetime.utcnow()
    with db.connect() as conn:
        stmt = sqlalchemy.text('SELECT work_id, created, amount, hour, deadline, canceled FROM works WHERE request_id=:request_id AND '
                               ':user_id IN (SELECT user_id FROM requests WHERE request_id=:request_id) ORDER BY created')
        data = conn.execute(stmt, request_id=request_id, user_id=user_id()).fetchall()
    works = [{'id': item[0], 'created': item[1].strftime('%Y-%m-%dT%H:%M:%S.%fZ'), 'twc': item[2], 'hour': item[3],
              'refundable': item[4] > now and not item[5]} for item in data]
    return jsonify({'works': works})

def restore_request():
    request_id = req.values.get('request_id')
    with db.connect() as conn:
        stmt = sqlalchemy.text('UPDATE requests SET removed=NULL WHERE request_id=:request_id AND user_id=:user_id LIMIT 1')
        conn.execute(stmt, request_id=request_id, user_id=user_id())
    return jsonify([{'status': 'successful'}])

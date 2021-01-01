from handlers.common import uuid, user_id, jsonify, db, req, datetime, safe, sqlalchemy, random, np

def create_task():
    if not user_id(): return 'Unauthorized', 401
    # if the user is suspicious, reject it.
    with db.connect() as conn:
        currency = random.choices(['twc', 'usd'], weights=[1, 2])[0]
        currency = 'usd'
        stmt = sqlalchemy.text('SELECT weight, COUNT(*) FROM payments WHERE deadline > current_timestamp(6) AND canceled IS NULL GROUP BY weight')
        data = conn.execute(stmt).fetchall()
        weights, counts = np.array(data).astype(float).T
        weight = int(random.choices(weights, weights*counts)[0])
        stmt = sqlalchemy.text('SELECT request_id FROM payments WHERE weight=:weight AND '
                               'deadline > current_timestamp(6) AND canceled IS NULL ORDER BY RAND() LIMIT 10')
        requests = conn.execute(stmt, weight=weight).fetchall()
        request_id = random.choice(requests)[0]
        stmt = sqlalchemy.text('INSERT INTO tasks(task_id, user_id, request_id) VALUES (:task_id, :user_id, :request_id)')
        conn.execute(stmt, task_id=uuid(), user_id=user_id(), request_id=request_id)
    return jsonify([{'status': 'successful'}])

def fetch_tasks():
    with db.connect() as conn:
        stmt = sqlalchemy.text('SELECT task_id, requests.contents, tasks.contents FROM tasks INNER JOIN requests USING (request_id) '
                               'WHERE tasks.user_id=:user_id AND 0 < (SELECT COUNT(*) FROM payments WHERE payments.request_id=requests.request_id AND '
                               'deadline > current_timestamp(6) AND canceled IS NULL) ORDER BY tasks.created DESC')
        tasks = conn.execute(stmt, user_id=user_id()).fetchall()
    return jsonify([{'task_id': task[0], 'request_contents': task[1], 'task_contents': task[2]} for task in tasks])

def update_task():
    contents = req.values.get('contents')
    contents = safe(contents) if contents.strip() else None
    task_id = req.values.get('item_id')
    with db.connect() as conn:
        stmt = sqlalchemy.text('UPDATE tasks SET contents=:contents WHERE task_id=:task_id AND user_id=:user_id LIMIT 1')
        conn.execute(stmt, contents=contents, user_id=user_id(), task_id=task_id)
    return jsonify([{'status': 'successful'}])

def create_pair():
    if not user_id(): return 'Unauthorized', 401
    # if the user is suspicious, reject it.
    with db.connect() as conn:
        stmt = sqlalchemy.text('SELECT task_id FROM tasks WHERE contents IS NOT NULL AND 0 < (SELECT COUNT(*) FROM payments '
                               'WHERE payments.request_id=tasks.request_id AND deadline > current_timestamp(6) '
                               'AND canceled IS NULL) ORDER BY RAND() LIMIT 10')
        zero_tasks = conn.execute(stmt, user_id=user_id()).fetchall()
        zero_task_id = random.choice(zero_tasks)[0]
        stmt = sqlalchemy.text('SELECT task_id FROM tasks WHERE contents IS NOT NULL AND 0 < (SELECT COUNT(*) FROM payments '
                               'WHERE request_id=request_id AND deadline > current_timestamp(6) AND canceled IS NULL) AND task_id!=:zero_task_id '
                               'ORDER BY RAND() LIMIT 10')
        one_tasks = conn.execute(stmt, user_id=user_id(), zero_task_id=zero_task_id).fetchall()
        one_task_id = random.choice(one_tasks)[0]
        stmt = sqlalchemy.text('INSERT INTO pairs(pair_id, user_id, zero_task_id, one_task_id) VALUES (:pair_id, :user_id, :zero_task_id, :one_task_id)')
        conn.execute(stmt, pair_id=uuid(), user_id=user_id(), zero_task_id=zero_task_id, one_task_id=one_task_id)
    return jsonify([{'status': 'successful'}])

def fetch_pairs():
    with db.connect() as conn:
        stmt = sqlalchemy.text('SELECT pair_id FROM pairs WHERE user_id=:user_id AND 0 < (SELECT COUNT(*) FROM payments WHERE request_id IN '
                               '(SELECT request_id FROM tasks WHERE task_id=zero_task_id) AND deadline > current_timestamp(6) AND canceled IS NULL) '
                               'AND 0 < (SELECT COUNT(*) FROM payments WHERE request_id IN (SELECT request_id FROM tasks WHERE task_id=one_task_id) '
                               'AND deadline > current_timestamp(6) AND canceled IS NULL) ORDER BY created DESC')
        pairs = conn.execute(stmt, user_id=user_id()).fetchall()
        pairs = [row[0] for row in pairs]
        if not pairs: return jsonify([])
        stmt = sqlalchemy.text('SELECT pair_id, zero_requests.contents, zero_tasks.contents, zero_requests.contents, one_tasks.contents, which '
                               'FROM pairs INNER JOIN tasks as zero_tasks ON pairs.zero_task_id=zero_tasks.task_id '
                               'INNER JOIN tasks as one_tasks ON pairs.one_task_id=one_tasks.task_id '
                               'INNER JOIN requests as zero_requests ON zero_tasks.request_id=zero_requests.request_id '
                               'INNER JOIN requests as one_requests ON one_tasks.request_id=one_requests.request_id '
                               'WHERE pair_id IN :pairs')
        pairs = conn.execute(stmt, pairs=pairs).fetchall()
        pairs = [{'pair_id': row[0], 'zero_request_contents': row[1], 'zero_task_contents': row[2],
                  'one_request_contents': row[3], 'one_task_contents': row[4], 'which': row[5]} for row in pairs]
    return jsonify(pairs)

def update_pair():
    which = req.values.get('which')
    pair_id = req.values.get('pair_id')
    with db.connect() as conn:
        stmt = sqlalchemy.text('UPDATE pairs SET which=:which WHERE pair_id=:pair_id AND user_id=:user_id LIMIT 1')
        conn.execute(stmt, which=which, user_id=user_id(), pair_id=pair_id)
    return jsonify([{'status': 'successful'}])

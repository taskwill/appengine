from handlers.common import uuid, user_id, jsonify, db, req, datetime, safe, sqlalchemy

def cancel():
    payment_id = req.values.get('payment_id'); canceled = datetime.datetime.utcnow();
    with db.connect() as conn:
        stmt = sqlalchemy.text('SELECT user_id FROM requests WHERE request_id IN (SELECT request_id FROM payments WHERE payment_id=:payment_id) LIMIT 1')
        user_has_payment = conn.execute(stmt, payment_id=payment_id).fetchone()[0] == user_id()
        if not user_has_payment: return 'Bad request', 400
        stmt = sqlalchemy.text('SELECT created, deadline FROM payments WHERE payment_id=:payment_id LIMIT 1')
        created, deadline = conn.execute(stmt, payment_id=payment_id).fetchone()
        if not deadline > canceled > created: return 'Bad request', 400
        stmt = sqlalchemy.text('UPDATE payments SET canceled=:canceled WHERE payment_id=:payment_id LIMIT 1')
        conn.execute(stmt, canceled=canceled, payment_id=payment_id)
    return jsonify([{'status': 'successful'}])

def cancel_payment():
    payment_id = req.values.get('payment_id'); canceled = datetime.datetime.utcnow(); stripe.api_key = stripe_api_key
    with db.connect() as conn:
        stmt = sqlalchemy.text('SELECT request_id FROM payments WHERE payment_id=:payment_id')
        request_id = conn.execute(stmt, payment_id=payment_id).fetchone()[0]
        stmt = sqlalchemy.text('SELECT user_id FROM requests WHERE request_id=:request_id')
        user_has_payment = conn.execute(stmt, request_id=request_id).fetchone()[0] == user_id()
        if not user_has_payment: return 'Bad request', 400
        stmt = sqlalchemy.text('SELECT amount, created, deadline, charge_id from payments WHERE payment_id=:payment_id LIMIT 1')
        amount, created, deadline, charge_id = conn.execute(stmt, payment_id=payment_id).fetchone()
        if not deadline > canceled > created: return 'Bad request', 400
        amount = int(amount*(deadline-canceled)/(deadline-created))
        refund = stripe.Refund.create(charge=charge_id, amount=amount)
        stmt = sqlalchemy.text('UPDATE payments SET canceled=:canceled, refund_id=:refund_id WHERE payment_id=:payment_id LIMIT 1')
        conn.execute(stmt, canceled=canceled, refund_id=refund.id, payment_id=payment_id)
    return jsonify([{'status': 'successful'}])

def submit():
    request_id = req.values.get('request_id'); twc = int(req.values.get('twc')); hour = int(req.values.get('hour'))
    if twc not in [1, 2, 5, 10, 20] or hour not in [1, 3, 6, 12, 24]: return 'Bad request', 400
    amount = twc * 100;  created = datetime.datetime.utcnow();  deadline = created + datetime.timedelta(hours=hour)
    created = created.strftime('%Y-%m-%d %H:%M:%S.%f');  deadline = deadline.strftime('%Y-%m-%d %H:%M:%S.%f')
    weight = amount * 24 // hour
    with db.connect() as conn:
        stmt = sqlalchemy.text('SELECT user_id FROM requests WHERE request_id=:request_id LIMIT 1')
        user_has_request = conn.execute(stmt, request_id=request_id).fetchone()[0] == user_id()
        if not user_has_request: return 'Bad request', 400
        stmt = sqlalchemy.text('SELECT balance FROM users WHERE user_id=:user_id')
        balance = conn.execute(stmt, user_id=user_id()).fetchone()[0]
        if type(balance) is not int or amount > balance: return 'Bad request', 400
        stmt = sqlalchemy.text('INSERT INTO payments (payment_id, request_id, created, deadline, amount, hour, weight) '
                               'VALUES (:payment_id, :request_id, :created, :deadline, :amount, :hour, :weight)')
        conn.execute(stmt, payment_id=uuid(), request_id=request_id, created=created, deadline=deadline, amount=amount, hour=hour, weight=weight)
        stmt = sqlalchemy.text('UPDATE users SET balance=:balance WHERE user_id=:user_id LIMIT 1')
        conn.execute(stmt, balance=balance-amount, user_id=user_id())
    return jsonify([{'status': 'successful'}])

def submit_payment():
    payment_id = uuid(); request_id = req.values.get('request_id'); usd = int(req.values.get('usd')); hour = int(req.values.get('hour'))
    if usd not in [1, 2, 5, 10, 20] or hour not in [1, 3, 6, 12, 24]: return 'Bad request', 400
    amount = usd * 100;  created = datetime.datetime.utcnow();  deadline = created + datetime.timedelta(hours=hour)
    created = created.strftime('%Y-%m-%d %H:%M:%S.%f');  deadline = deadline.strftime('%Y-%m-%d %H:%M:%S.%f')
    currency = 'usd'; weight = amount * 24 // hour; stripe.api_key = stripe_api_key
    metadata = {'payment_id': payment_id, 'user_id': user_id(), 'request_id': request_id}
    with db.connect() as conn:
        stmt = sqlalchemy.text('SELECT user_id FROM requests WHERE request_id=:request_id')
        user_has_request = conn.execute(stmt, request_id=request_id).fetchone()[0] == user_id()
        if not user_has_request: return 'Bad request', 400
        stmt = sqlalchemy.text('SELECT customer_id FROM users WHERE user_id=:user_id LIMIT 1')
        result = conn.execute(stmt, user_id=user_id()).fetchone()
        if not result: return 'Bad request', 400
        customer_id = result[0]
        stmt = sqlalchemy.text('INSERT INTO payments(payment_id, request_id, user_id, created, deadline, amount, hour, currency, weight) '
                               'VALUES (:payment_id, :request_id, :user_id, :created, :deadline, :amount, :hour, :currency, :weight)')
        conn.execute(stmt, payment_id=payment_id, request_id=request_id, user_id=user_id(), created=created,
                     deadline=deadline, amount=amount, hour=hour, currency=currency, weight=weight)
        charge = stripe.Charge.create(amount=amount, currency='usd', customer=customer_id, metadata=metadata)
        stmt = sqlalchemy.text('UPDATE payments SET charge_id=:charge_id WHERE payment_id=:payment_id LIMIT 1')
        conn.execute(stmt, charge_id=charge.id, payment_id=payment_id)
    return jsonify([{'status': 'successful'}])

import json
from handlers.common import uuid, user_id, jsonify, db, req, datetime, sqlalchemy, pd, PayPalClient
from paypalcheckoutsdk.orders import OrdersGetRequest

class GetOrder(PayPalClient):
    def get_order(self, order_id):
        request = OrdersGetRequest(order_id)
        response = self.client.execute(request)
        print('Status Code: ', response.status_code)
        print('Status: ', response.result.status)
        print('Order ID: ', response.result.id)
        print('Intent: ', response.result.intent)
        print('Links:')
        for link in response.result.links:
            print('\t{}: {}\tCall Type: {}'.format(link.rel, link.href, link.method))
            print('Gross Amount: {} {}'.format(response.result.purchase_units[0].amount.currency_code, response.result.purchase_units[0].amount.value))

def pay_usd():
    order_id = json.loads(req.get_data().decode('utf-8'))['orderID']
    GetOrder().get_order(order_id)
    return 'Failed'

def customer_id():
    with db.connect() as conn:
        stmt = sqlalchemy.text('SELECT customer_id FROM users WHERE user_id=:user_id LIMIT 1')
        result = conn.execute(stmt, user_id=user_id()).fetchone()
    return jsonify({'customer_id': result[0] if result else None})

def save_card():
    token = req.values.get('token')
    id_token = req.headers['Authorization'].split(' ').pop()
    email = auth.verify_id_token(id_token)['email']
    stripe.api_key = stripe_api_key
    with db.connect() as conn:
        stmt = sqlalchemy.text('SELECT customer_id FROM users WHERE user_id=:user_id LIMIT 1')
        result = conn.execute(stmt, user_id=user_id()).fetchone()
        customer_id = result[0] if result else None
        if customer_id is None:
            customer = stripe.Customer.create(source=token, email=email, metadata={'user_id': user_id()})
            stmt = sqlalchemy.text('INSERT INTO users(user_id, customer_id) VALUES (:user_id, :customer_id) '
                                   'ON DUPLICATE KEY UPDATE customer_id=:customer_id')
            conn.execute(stmt, user_id=user_id(), customer_id=customer.id)
        else:
            stripe.Customer.modify(customer_id, source=token)
    return jsonify({'status': 'successful'})

def download_data():
    with db.connect() as conn:
        stmt = sqlalchemy.text('SELECT user_id, api_key, customer_id FROM users WHERE user_id=:user_id LIMIT 1')
        user_data = conn.execute(stmt, user_id=user_id()).fetchall()
        stmt = sqlalchemy.text('SELECT request_id, contents, created, removed FROM requests '
                               'WHERE user_id=:user_id AND deleted IS NULL ORDER BY created DESC')
        request_data = conn.execute(stmt, user_id=user_id()).fetchall()
    user_data = pd.DataFrame(list(user_data), columns=['user_id', 'api_key', 'customer_id']).to_csv(index=False)
    time = '%Y-%m-%dT%H:%M:%S.%fZ'
    request_data = [(row[0], row[1], row[2].strftime(time), row[3].strftime(time) if row[3] else None) for row in request_data]
    request_data = pd.DataFrame(request_data, columns=['request_id', 'contents', 'created', 'removed']).to_csv(index=False)
    return jsonify({'user_data': user_data, 'request_data': request_data})

def delete_account():
    with db.connect() as conn:
        stmt = sqlalchemy.text('UPDATE users SET deleted=CURRENT_TIMESTAMP(6) WHERE user_id=:user_id LIMIT 1')
        conn.execute(stmt, user_id=user_id())
    return jsonify([{'status': 'successful'}])
from flask import Flask, request, jsonify
from flask_pydanql_api import PydanqlAPI, Endpoint
from pydanql.model import ObjectBaseModel
from pydanql.table import Table
from datetime import datetime
from flask_jwt_extended import create_access_token, verify_jwt_in_request, get_jwt_identity

class Car(ObjectBaseModel):
    brand: str
    model: str
    year: int
    color: str
    miles: float
    owner: str

    def miles_per_year(self):
        current_year = datetime.now().year
        years_since_manufacture = current_year - self.year + 1
        return float(self.miles / years_since_manufacture)

    def description(self):
        return f"A {self.color} {self.model} build by {self.brand}"


class Cars(Endpoint):
    slug = 'cars' # part of the url to accesse the table 
    model = Car # The object for table entries
    allowed_query_fields = ['brand', 'color', 'year', 'owner']
    visible_fields = ['owner', 'brand', 'color', 'year', 'model', 'slug', 'miles_per_year', 'description']

    @staticmethod
    def _filter(query_type, query_table):
        verify_jwt_in_request()
        current_user = get_jwt_identity()
        if query_type == 'find':
            return {'owner': current_user}
        if query_type == 'get':
            return {'owner': current_user}
        if query_type == 'create':
            return {'owner': current_user}
        if query_type == 'delete':
            return {'owner': current_user}

        return jsonify({'error': 'Not todo', 'detail': 'todo'}), 405


app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'super-secret'
app.config['PYDANQL_API_DB'] = {
    'database': 'testdb',
    'user': 'testuser',
    'password': 'testpass',
    'host': 'localhost',
    'port': '5432'
}
app.config['PYDANQL_API_ENDPOINTS'] = [Cars]

PydanqlAPI(app)

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username', None)
    password = request.json.get('password', None)

    # In a real-world app, you'd validate these credentials against a database
    if password != 'password':
        return jsonify({'login': False}), 401

    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token), 200

if __name__ == '__main__':
    app.run(debug=True)

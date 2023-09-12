from flask import Flask, request, jsonify
from flask_pydanql_api import PydanqlAPI, Endpoint
from pydanql.model import ObjectBaseModel
from datetime import datetime
from flask_jwt_extended import create_access_token, verify_jwt_in_request, get_jwt_identity, JWTManager


class Book(ObjectBaseModel):
    """This is a basic Pydanql model for books"""
    title: str
    author: str
    year: int
    owner: str

    def years_since_published(self) -> int:
        """Custom method to calculate the years since the book is published"""
        current_year = datetime.now().year
        return current_year - self.year + 1

    def description(self) -> str:
        """Custom method that generates a description"""
        return f"The Book \"{self.title}\" by {self.author} was published in the year {self.year}."


class Books(Endpoint):
    """Use the endpoint class for advanced configuration"""

    # part of the url to accesse the table  /<slug>/find?title__like=Lord
    slug = 'books'

    # The object for table entries
    model = Book

    # Fields from the model that can be queried
    allowed_query_fields = ['title', 'author', 'year']

    # Fields that are exposed in the result
    visible_fields = ['title', 'author', 'year', 'owner']

    @staticmethod
    def _filter(query_type: str, query_table: str):
        verify_jwt_in_request()
        if query_type in ['find', 'get', 'create', 'delete']:
            return {'owner': get_jwt_identity()}


app = Flask(__name__)

# Setup JWTManager
app.config['JWT_SECRET_KEY'] = 'super-secret'
JWTManager(app)

# Setup FlaskPydanqlAPI
app.config['PYDANQL_API_DB'] = {
    'database': 'testdb',
    'user': 'testuser',
    'password': 'testpass',
    'host': 'localhost',
    'port': '5432'
}
app.config['PYDANQL_API_ENDPOINTS'] = [Books]
PydanqlAPI(app)


@app.route('/login', methods=['POST'])
def login():
    """Custom route to handle the login with JWTManager"""
    if request.json is None:
        return jsonify({"error": "Bad Request", "message": "No JSON payload provided"}), 400

    username = request.json.get('username', None)
    password = request.json.get('password', None)
    
    # In a real-world app, you'd validate these credentials against a database
    if password != 'password':
        return jsonify({'login': False}), 401

    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token), 200


if __name__ == '__main__':
    app.run(debug=True)

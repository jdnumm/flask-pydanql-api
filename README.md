
# Flask-PydanqlAPI

## Overview

Flask-PydanqlAPI is a Flask extension that offers seamless integration with the Pydanql library, simplifying interactions with PostgreSQL databases. This extension automates the generation of RESTful API endpoints for your database models, offering optional features like JWT authentication and query filtering.

⚠️ **Early Version Warning**: This is an early version of the Flask-PydanqlAPI extension and is subject to changes. Although it is fully functional, future versions may introduce breaking changes. Your feedback is highly appreciated!

## Features

- Simple CRUD operations through Pydanql models
- Optional JWT Authentication
- Customizable query and return fields
- Optional support for additional filtering on queries

## Getting Started

### Basic Setup

Here's a minimal example to show how to set up the Flask-PydanqlAPI extension without authentication and custom filtering.

```python
from flask import Flask
from flask_pydanql_api import PydanqlAPI
from pydanql.model import ObjectBaseModel

class Car(ObjectBaseModel):
    brand: str
    model: str
    year: int
    color: str

app = Flask(__name__)

app.config['DB'] = {
    'database': 'testdb',
    'user': 'testuser',
    'password': 'testpass',
    'host': 'localhost',
    'port': '5432'
}

app.config['TABLES'] = {
    'cars': {
        'query': ['brand', 'color', 'year'],
        'return': ['id', 'brand', 'color', 'year', 'model'],
        'model': Car
    }
}

PydanqlAPI(app)

if __name__ == '__main__':
    app.run(debug=True)
```

### Advanced Setup with JWT and Filtering

Here's an example that includes JWT authentication and custom filtering.

```python
from flask import Flask, request, jsonify
from flask_pydanql_api import PydanqlAPI
from pydanql.model import ObjectBaseModel
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


def filter(query_type, query_table):
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

app.config['DB'] = {
    'database': 'testdb',
    'user': 'testuser',
    'password': 'testpass',
    'host': 'localhost',
    'port': '5432'
}

app.config['JWT_SECRET_KEY'] = 'super-secret'

app.config['TABLES'] = {
            'cars': {
                'query': ['brand', 'color', 'year', 'owner'],
                'return': ['id', 'owner', 'brand', 'color', 'year', 'model', 'slug', 'miles_per_year', 'description'],
                'model': Car,
                'filter': filter
            }
        }

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

```

## Contributing

We are open to contributions. Please fork the repository and submit your pull requests!

## License

Flask-PydanqlAPI is licensed under the MIT license.

# Flask-PydanqlAPI: Create RESTful endpoints automatically

## Overview

Flask-PydanqlAPI is a Flask extension designed to simplify the creation and management of RESTful APIs backed by PostgreSQL databases. Utilizing the [Pydanql](https://github.com/jdnumm/pydanql) library, this extension automates CRUD operations and provides a host of optional features for a more customized experience.

## Features

- **Automated CRUD Operations**: Create RESTful endpoints automatically from your Pydanql models, making it easier to handle Create, Read, Update, and Delete operations.
  
- **Query Customization**: Flexibility to customize which fields are queriable and which are returned in the response, letting you optimize the API according to your needs.

- **Advanced Filtering**: Add an extra layer of control over the data you retrieve through advanced query filters, enabling more precise data retrieval.

- **Extendable Authentication**: Although JWT authentication is not natively supported, you can easily integrate it by utilizing the filter options available.

## Getting Started

Here's a minimal example to show how to set up the Flask-PydanqlAPI extension without authentication and custom filtering.

```python
# Easily create a full-fledged API with all CRUD actions. Create, Read, Update
# and Delete. Advanced search options, extensible, and even many more.
# 
# GET Books from /books/find?year__range=1950,1960&title__like=Lord

from flask import Flask
from flask_pydanql_api import PydanqlAPI, Endpoint
from pydanql.model import ObjectBaseModel

app = Flask(__name__)


# Define youre Model 
class Book(ObjectBaseModel):
    title: str
    author: str
    year: int


# Define youre API-Endpoint
class Books(Endpoint):
    slug = 'books'
    model = Book


# Connect to your postgreSQL Database
app.config['PYDANQL_API_DB'] = { 'database': ..., 'user': ..., 'password': ... }
app.config['PYDANQL_API_ENDPOINTS'] = [Books]

PydanqlAPI(app)

if __name__ == '__main__':
    app.run(debug=True)
```

## PostgreSQL Setup

Create a user and a database

```BASH
psql postgres # Connect to your database
```

```SQL
CREATE DATABASE testdb;
CREATE USER testuser WITH PASSWORD 'testpass';
GRANT ALL PRIVILEGES ON DATABASE testdb TO testuser;
```

## Documentation

⚠️ **Early Version Warning**: This is an early version of the Flask-PydanqlAPI and is subject to changes. Although it is fully functional, future versions may introduce breaking changes. Your feedback is highly appreciated!

### API Endpoints

#### Find

- **URL**: `/<table>/find`
- **Method**: `GET`
  
  - **Query Parameters**:
    - `offset` (integer, optional): Offset for pagination.
    - `count` (integer, optional): Number of records to fetch.
    - `sort` (string, optional): Sorting key.
  
  - **Field Query Filters**:
    - `[field]` (Type depends on the field): Direct match.
    - `[field]__range` (integer,integer): Range query.
    - `[field]__in` (comma-separated values): Inclusion in a set.
    - `[field]__gt` (Type depends on the field): Greater than query.
    - `[field]__lt` (Type depends on the field): Less than query.
    - `[field]__like` (string): SQL LIKE query.
  
- **Example**: 
  - Basic: `GET /books/find?offset=0&count=10`
  - Advanced: `GET /books/find?title__like=Harry&year__gt=2000`

- **Returns**: A list of books matching the query parameters.


#### Get a Single Entry

- **URL**: `/<table>/<entry_slug>`
- **Method**: `GET`
  
  - **Path Parameters**:
    - `table`: The table name (e.g., `books`).
    - `entry_slug`: The ID of the entry to fetch.

- **Example**: `GET /books/1234-5678-abcd`

- **Returns**: The book with the specified ID.


#### Delete a Entry

- **URL**: `/<table>/<entry_slug>`
- **Method**: `DELETE`
  
  - **Path Parameters**:
    - `table`: The table name (e.g., `books`).
    - `entry_slug`: The ID of the entry to delete.

- **Example**: `DELETE /books/1234-5678-abcd`

- **Returns**: A message indicating the status of the delete operation.


#### Create a New Entry

- **URL**: `/<table>/create`
- **Method**: `POST`
  
  - **Path Parameters**:
    - `table`: The table name (e.g., `books`).

  - **Data Payload**: JSON object representing the new book.

- **Example**: 
  ```bash
  curl -X POST /books/create -d '{"title":"New Book", "author":"Author Name", "year":2021}'
  ```
  
- **Returns**: Redirects to the new book entry.


#### Update a Entry

- **URL**: `/<table>/<slug>`
- **Method**: `PUT`

  - **Path Parameters**:
    - `table`: The table name (e.g., `books`).
    - `slug`: The slug identifier for the book to update.
  
  - **Data Payload**: JSON object representing the updated book.

- **Example**: 
  ```bash
  curl -X PUT /books/1234-5678-abcd -d '{"title":"Updated Book", "author":"Updated Author", "year":2022}'
  ```

- **Returns**: Redirects to the updated book entry.



### Defining API Endpoints and Models
#### ObjectBaseModel Class

The `ObjectBaseModel` serves as the base class for all models in this application. It includes some fundamental fields that are automatically included in every model derived from it.

##### Fields:

- `slug`: A unique string identifier for each object. The `slug` is auto-generated but can be manually overwritten if necessary.

##### Usage:

You can inherit from `ObjectBaseModel` when defining your models:

```python
from pydanql.model import ObjectBaseModel

class Book(ObjectBaseModel):
    title: str
    author: str
    year: int
```

#### Endpoint Class

The `Endpoint` class is used to define API endpoints for the Flask application. Each `Endpoint` corresponds to a database table and Pydantic model that defines the shape of the data.

##### Attributes:

- `slug`: A string that sets the URL path for the API endpoint. Must be unique among all endpoints.
- `model`: A Pydantic model class that specifies the structure of the data for this endpoint. This should be a subclass of `ObjectBaseModel`.
- `allowed_query_fields`: A list of fields that can be queried directly via the API.
- `visible_fields`: A list of fields that will be visible when fetching data via the API.

##### Usage:

To define an endpoint, subclass `Endpoint` and set the `slug` and `model` attributes:

```python
from flask_pydanql_api import Endpoint
from my_model import Book  # Assuming Book is a subclass of ObjectBaseModel

class Books(Endpoint):
    slug = 'books'
    model = Book
```

After defining your endpoints, you can register them to your Flask application using the `PydanqlAPI` class:

```python
from flask import Flask
from flask_pydanql_api import PydanqlAPI

app = Flask(__name__)
api = PydanqlAPI(app)
```

This will automatically generate RESTful routes for your `Endpoint` classes.


## Examples
### Advanced Setup with JWT and Filtering

Here's an example that includes JWT authentication and custom filtering.

```python
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
    visible_fields = ['slug', 'title', 'author', 'year', 'owner']

    @staticmethod
    def _filter(query_type: str, query_table: str):
        verify_jwt_in_request()
        if query_type in ['find', 'get', 'create', 'update', 'delete']:
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
```

## Contributing

We are open to contributions. Please fork the repository and submit your pull requests!

## License

Flask-PydanqlAPI is licensed under the MIT license.

from flask import Flask, g, jsonify, redirect, url_for, request
from pydanql.base import Database
from pydanql.table import Table, get_all_annotations
from uuid import uuid4
from pydantic import ValidationError, parse_obj_as
from functools import wraps


def register_routes(app: Flask):

    @app.before_request
    def before_request():
        g.pydanql_db = Database(**app.config['PYDANQL_API_DB'])
        g.pydanql_tables = {}
        for table in app.config['PYDANQL_API_ENDPOINTS']:
            # Add the table as a database attribute.
            setattr(g.pydanql_db, table.slug, Table(g.pydanql_db, table.model))
            # Add the configureation for later use in the routes.
            g.pydanql_tables[table.slug] = table

    @app.after_request
    def after_request(response):
        print("After request: Close Database!")
        g.pydanql_db.close()
        return response

    # Define the decorator function
    def extend_query_for(endpoint):
        def decorator(f):
            @wraps(f)  
            def wrapper(*args, **kwargs):
                table = kwargs.get('table')
                if table not in g.pydanql_tables:
                    return jsonify({'error': f'There is no endpoint named: {table}'}), 404
                filter_function = g.pydanql_tables[table]._filter
                if filter_function:
                    print(filter_function)
                    filter_result = filter_function(endpoint, table)
                    print(filter_result)
                    if isinstance(filter_result, dict):
                        kwargs['extendet_query_kwargs'] = filter_result
                return f(*args, **kwargs)
            return wrapper
        return decorator

    @app.route('/<table>/find', methods=['GET'])
    @extend_query_for('find')
    def find(table, extendet_query_kwargs={}):
        combined_args = list(request.args.items()) + list(extendet_query_kwargs.items())

        allowed_query_fields = g.pydanql_tables[table].allowed_query_fields+list(extendet_query_kwargs.keys())
        allowed_return_fields = g.pydanql_tables[table].visible_fields

        ModelClass = g.pydanql_tables[table].model
        model_fields = get_all_annotations(ModelClass)

        offset = request.args.get('offset', default=None, type=int)
        count = request.args.get('count', default=None, type=int)
        sort = request.args.get('sort', default=None, type=str)

        # Initialize empty dictionary for filters
        filters = {}

        for key, value in combined_args:
            if key in ['offset', 'count', 'sort']:
                continue  # Skip these keys

            if '__' in key:
                field, cmd = key.split('__')
                if field not in allowed_query_fields:
                    return jsonify({'error': f'Invalid field: {field}'}), 400

                if cmd == "range":
                    try:
                        low, high = map(int, value.split(","))
                    except ValueError:
                        return jsonify({'error': f'Invalid range value for {field}'}), 400
                    filters[field] = {'range': [low, high]}

                elif cmd == "in":
                    try:
                        values = [parse_obj_as(model_fields[field], val) for val in value.split(",")]
                    except ValidationError as e:
                        return jsonify({'error': f'Invalid in value for {field}', 'detail': e.errors()}), 400
                    filters[field] = {'in': values}

                elif cmd in ["gt", "lt"]:
                    try:
                        validated_value = parse_obj_as(model_fields[field], value)
                    except ValidationError as e:
                        return jsonify({'error': f'Invalid value for {field}', 'detail': e.errors()}), 400
                    filters[field] = {cmd: validated_value}

                elif cmd == "like":
                    filters[field] = {'like': f"%{value}%"}

                else:
                    return jsonify({'error': f'Invalid command: {cmd}'}), 400

            else:
                if key not in allowed_query_fields:
                    return jsonify({'error': f'Invalid field: {key}'}), 400
                try:
                    validated_value = parse_obj_as(model_fields[key], value)
                except ValidationError as e:
                    return jsonify({'error': f'Invalid value for {key}', 'detail': e.errors()}), 400
                filters[key] = validated_value

        entrys = getattr(g.pydanql_db, table).find_many(offset=offset, count=count, sort=sort, **filters)

        results = [{
            **{k: v for k, v in entry.dict().items() if k in allowed_return_fields}, 
            **{m: getattr(entry, m)() for m in dir(entry) if m in allowed_return_fields and callable(getattr(entry, m, None))}}
            for entry in entrys
        ]

        return jsonify(results=results)

    @app.route('/<table>/<entry_id>', methods=['DELETE'])
    @extend_query_for('delete')
    def delete(table, entry_id, extendet_query_kwargs={}):

        try:
            # Find the entry to delete
            entry_to_delete = getattr(g.pydanql_db, table).find_one(slug=entry_id, **extendet_query_kwargs)

            # Check if the entry exists
            if not entry_to_delete:
                return jsonify({'error': f'No entry found with id {entry_id}'}), 404  # Not Found

            # Delete the entry
            getattr(g.pydanql_db, table).delete(entry_to_delete)

            return jsonify({'success': f'Entry with id {entry_id} successfully deleted'}), 200  # OK

        except Exception as e:
            # Log the exception for debugging
            print(str(e))
            return jsonify({'error': 'Internal Server Error'}), 500  # Internal Server Error

    @app.route('/<table>/<entry_id>', methods=['GET'])
    @extend_query_for('get')
    def get(table, entry_id, extendet_query_kwargs={}):

        allowed_return_fields = g.pydanql_tables[table].visible_fields

        ModelClass = g.pydanql_tables[table].model

        try:
            # Find the entry
            entry = getattr(g.pydanql_db, table).find_one(slug=entry_id, **extendet_query_kwargs)

            # Check if the entry exists
            if not entry:
                return jsonify({'error': f'No entry found with id {entry_id}'}), 404  # Not Found

            # Serialize the entry and filter the fields
            result = {
                **{k: v for k, v in entry.dict().items() if k in allowed_return_fields}, 
                **{m: getattr(entry, m)() for m in dir(entry) if m in allowed_return_fields and callable(getattr(entry, m, None))}}

            return jsonify(result), 200  # 200 is for OK

        except Exception as e:
            # Log the exception for debugging
            print(str(e))
            return jsonify({'error': 'Internal Server Error'}), 500  # Internal Server Error

    @app.route('/<table>/create', methods=['POST'])
    @extend_query_for('create')
    def create(table, extendet_query_kwargs={}):
        
        if request.json is None:
            return jsonify({"error": "Bad Request", "message": "No JSON payload provided"}), 400

        ModelClass = g.pydanql_tables[table].model

        try:
            # Validate and parse incoming JSON payload
            data = request.json
            new_entry = ModelClass(**{**data, **extendet_query_kwargs})

        except ValidationError as e:
            return jsonify({'error': 'Invalid data', 'detail': e.errors()}), 400

        try:
            # Generate a unique identifier for the entry
            new_entry.slug = uuid4().hex

            # Add the new entry to the database
            getattr(g.pydanql_db, table).add(new_entry)

            # Commit the changes (if needed depending on your ORM)
            # g.pydanql_db.commit()

            # Return the created entry
            return redirect(url_for('get', table=table, entry_id=new_entry.slug))

        except Exception as e:
            # Log the exception for debugging
            print(str(e))
            return jsonify({'error': 'Internal Server Error'}), 500

        return jsonify('boom'), 400

    @app.route('/<table>/<slug>', methods=['PUT'])
    @extend_query_for('update')
    def update(table, slug, extendet_query_kwargs={}):
        ModelClass = g.pydanql_tables[table].model

        data = request.json
        existing_entry = getattr(g.pydanql_db, table).find_one(slug=slug, **extendet_query_kwargs)

        if not existing_entry:
            return jsonify({'error': 'Entry not found'}), 404

        updated_data = {**existing_entry.dict(), **data}
        try:
            new_entry = ModelClass(**updated_data)
        except ValidationError as e:
            return jsonify({'error': 'Invalid data', 'details': e.errors()}), 400

        getattr(g.pydanql_db, table).replace(new_entry)

        return redirect(url_for('get', table=table, entry_id=new_entry.slug))

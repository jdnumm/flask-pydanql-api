from flask import Flask
from pydanql.table import get_all_annotations
import inspect


class PydanqlAPI:

    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask):
        # Initialize your extension with the given app

        # You can add configuration options here if needed
        app.config.setdefault('MY_EXTENSION_OPTION', 'default_value')

        # Registering routes
        from .routes import register_routes
        register_routes(app)


class Endpoint():
    slug = None
    model = None
    allowed_query_fields = None
    visible_fields = None

    @staticmethod
    def _filter(query_type, query_table):
        return {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls.slug is None or cls.model is None:
            raise NotImplementedError("Endpoint subclasses must define 'slug' and 'model' attributes")

        # Get all annotated fields from cls.model
        fields = list(get_all_annotations(cls.model).keys())

        # Get all methods from cls.model, filtering out special/magic methods
        # and methods defined in parent classes
        methods = [name for name, member in inspect.getmembers(cls.model) 
                   if inspect.isfunction(member) 
                   and not (name.startswith('__') and name.endswith('__')) 
                   and member.__qualname__.startswith(cls.model.__name__ + '.')]

        # Set cls.visible_fields and cls.allowed_query_fields to the model fields if they are None
        cls.visible_fields = fields + methods if cls.visible_fields is None else cls.visible_fields
        cls.allowed_query_fields = fields + methods if cls.allowed_query_fields is None else cls.allowed_query_fields

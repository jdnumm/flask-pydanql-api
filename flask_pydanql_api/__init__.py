from flask import Flask, g

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

        # You can also add a blueprint here if you want
        # app.register_blueprint(my_blueprint)


class Endpoint():
    slug = None
    model = None
    allowed_query_fields = []
    visible_fields = []

    def _filter(query_type, query_table):
        return {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls.slug is None or cls.model is None:
            raise NotImplementedError("Endpoint subclasses must define 'slug' and 'model' attributes")

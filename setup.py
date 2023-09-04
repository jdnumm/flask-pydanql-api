from setuptools import setup

setup(
    name='Flask-MyExtension',
    version='0.0.1-alpha',
    packages=['flask_pydanql_api'],
    include_package_data=True,
    install_requires=[
        'Flask',
    ],
)
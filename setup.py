from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='Flask-Pydanql-API',
    version='0.0.1-alpha',
    packages=find_packages(),
    author='Daniel Nümm',
    author_email='oss@blacktre.es',
    description='',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://blacktre.es',
    project_urls={},
    include_package_data=True,
    install_requires=[
        'Flask',
        'pydanql'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)


#!/usr/bin/env bash

case "$1" in
        run) 
            pipenv run flask run --debug
        ;;
        shell) 
            pipenv shell
        ;;
        edit) 
            pipenv run $EDITOR .
        ;;
        setup) 
            pipenv install --dev
        ;;
        build)
            rm -rf build
            rm -rf dist
            python setup.py sdist bdist_wheel
        ;;
        distribute)
            twine upload dist/*
        ;;
        *) echo "Use one of the following args: run, shell, edit, setup, build, distribute"
        ;;
esac
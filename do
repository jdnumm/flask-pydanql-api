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
        *) echo "Use one of the following args: run, shell, edit, setup"
        ;;
esac
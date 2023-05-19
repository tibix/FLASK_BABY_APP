# FLASK_BABY_APP

## Installation via docker
 - Clone the repo
 - Make sure you have docker-desktop or docker engine installed
 - Run ```docker compose up -d```
 - Enjoy your app:
    - Webapp: http://localhost:81
    - phpMyAdmin: http://localhost:8081

## Running the application as standalone
 - clone the repo
 - edit line 12 in ```webapp/website/__init__.py``` and adjust it to your setup
 - activate the virtual environment with _pipenv_ and run ```pipenv install```
 - while inside of ```webapp/``` you can run ```flask run``` and enjoy your app on http://localhost:81

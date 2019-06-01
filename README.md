# Course-Monitor
A script which monitors the enrollment status of courses of HKUST and keeps history data in an incremental way.

## Before You Start

Create a file 

    touch ./server/server/settings_local.py

Inside this file, add the following dict

    cors_headers = {
        "Access-Control-Allow-Origin": "http://<ip and port of your frontend server>",
        "Access-Control-Allow-Methods": "GET"
    }

## Start

For the first time, run

    pip3 install -r requirements.txt
    python server/manage.py migrate

To run the backend server locally, execute

    python server/manage.py runserver

To run remotely, 

    python server/manage.py runserver 0.0.0.0:8000

# Course-Monitor
A script which monitors the enrollment status of courses of HKUST and keeps history data in an incremental way.

## Before You Start

Create a `.env` file in the root folder of this repo (i.e. next to this README)

    touch .env

Inside this file, add the following variable to indicate the URL where the frontend page is hosted.

    DATASERVER_REACT_APP_ORIGIN=<some origin>,<another origin seperated by comma>,<as many as you want>,<for example http://localhost:5000>

## Start

For the first time, run

    pip3 install -r requirements.txt
    python server/manage.py migrate

To run the backend server locally, execute

    python server/manage.py runserver

To run remotely, 

    python server/manage.py runserver 0.0.0.0:8000

## Related Project

[Course-Monitor-Web](https://github.com/fhfuih/Course-Monitor-Web) - The frontend of course monitor project

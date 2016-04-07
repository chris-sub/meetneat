#Setup

##Start API Server
From a Terminal, navigate to the root folder of the application and enter the following:
python views.py

##Start Client Server
From a Terminal, navigate to the Client folder of the application and enter the following:
python -m SimpleHTTPServer 8000

##Accessing the Server
Once both servers are active, navigate to http://localhost:8000 in your browser


##Notes
*The Client was built using AngularJS on the Bootstrap framework
*The API was built using Python and the Flask library, with a SQLite database to store data
*To truly illustrate the separation of the API from the client, they should be run on different ports
*The Client interfce does not make use of every endpoint but they are available for consumption

##Dependencies
Flask
Flask-cors
redis
oauth2client
sqlalchemy
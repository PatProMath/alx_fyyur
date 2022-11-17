import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

#Some configuration in .flaskenv and .env files

# Connect to the database
#Get the value of the environment variables
user = 'DB_USR'
password = 'DB_PASSWD'
host = 'DB_HOST'
database_uri = 'DB_URL'

DATABASE_URI = os.getenv(database_uri)
print(DATABASE_URI)
# IMPLEMENT DATABASE URI
SQLALCHEMY_DATABASE_URI = os.getenv(database_uri, 'postgresql://postgres@localhost:5432/postgres')

#Removes the significant overhead in starting the application
SQLALCHEMY_TRACK_MODIFICATIONS = False
#Allows me see the SQL queries being printed on the terminal
SQLALCHEMY_ECH0 = True
#Ensure it is created in development folder

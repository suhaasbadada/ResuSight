import os
from flask import Flask
from flask_pymongo import PyMongo

app=Flask(__name__)

# Mongo Config
app.config['MONGO_URI']=os.getenv('MONGO_URL')
mongo = PyMongo(app)
mongo.init_app(app)

@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__=='__main__':
    app.run(debug=True)
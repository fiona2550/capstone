import os
from sqlalchemy import Column, String, Integer, create_engine, Date, Float
from flask_sqlalchemy import SQLAlchemy
import json
from datetime import date
#from config import database_setup


db = SQLAlchemy()

database_path = os.environ['DATABASE_URL']

def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()
    
'''
db_drop_and_create_all()
    drops the database tables and starts fresh
'''

def db_drop_and_create_all():
    db.drop_all()
    db.create_all()    
    db_init_records()

def db_init_records():
    '''this will initialize the database with some test records.'''

    actor_init = (Actors(
        name = 'Fiona',
        gender = 'Female',
        age = 24
        ))

    movie_init = (Movies(
        title = 'The Philadelphia Story',
        release_date = '1940-12-26'
        ))

 
    movie_init.actors = [actor_init]
    actor_init.movies = [movie_init]
    actor_init.insert()
    movie_init.insert()
    db.session.commit()
    '''
Movie
'''
# set up many-to-to many relationship    
Rate = db.Table('Rate', db.Model.metadata,
    db.Column('actor_id' , db.Integer, 
                db.ForeignKey('actors.actor_id')),
    db.Column('movie_id', db.Integer, 
                db.ForeignKey('movies.movie_id'))
)
   
class Movies(db.Model):  
    __tablename__ = 'movies'
    
    movie_id = Column(Integer, primary_key=True)
    title = Column(String)
    release_date = Column(Date)
    actors = db.relationship('Actors', secondary=Rate, 
                            backref=db.backref('Rate', lazy=True))

    def __init__(self, title, release_date):
        self.title = title
        self.release_date = release_date    
        
    def insert(self):
        db.session.add(self)
        db.session.commit()
  
    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.movie_id,
            'title': self.title,
            'release_date': self.release_date
        }        
'''
Actors
'''

class Actors(db.Model):  
    __tablename__ = 'actors'
    
    actor_id = Column(Integer, primary_key=True)
    name = Column(String)
    gender = Column(String)
    age = Column(Integer)
    
    def __init__(self, name, gender, age):
        self.name = name
        self.gender = gender
        self.age = age

    def insert(self):
        db.session.add(self)
        db.session.commit()
  
    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        
    def format(self):
        return {
            'id': self.actor_id,
            'name': self.name,
            'gender': self.gender,
            'age': self.age
        }
		
#db_drop_and_create_all()
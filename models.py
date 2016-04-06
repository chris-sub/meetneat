from sqlalchemy import Column,Integer,String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from passlib.apps import custom_app_context as pwd_context
import random, string
from itsdangerous import(TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)

Base = declarative_base()
secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(32), index=True)
    picture = Column(String)
    email = Column(String)
    password_hash = Column(String(64))
    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)
    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)
    def generate_auth_token(self, expiration=3600):
    	s = Serializer(secret_key, expires_in = expiration)
    	return s.dumps({'id': self.id })
    @staticmethod
    def verify_auth_token(token):
    	s = Serializer(secret_key)
    	try:
    		data = s.loads(token)
    	except SignatureExpired:
    		#Valid Token, but expired
    		return None
    	except BadSignature:
    		#Invalid Token
    		return None
    	user_id = data['id']
    	return user_id
    @property
    def serialize(self):
        return {'id':self.id, 'username':self.username, 'picture':self.picture, 'email':self.email}
    

class Request(Base):
    __tablename__ = 'Request'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    location_string = Column(String)
    longitude = Column(String)
    latitude = Column(String)
    meal_time = Column(Integer)
    meal_type = Column(String)
    filled = Column(Integer)
    @property
    def serialize(self):
        return {'id':self.id, 'user_id':self.user_id, 'location_string':self.location_string, 'latitude':self.latitude, 'longitude':self.longitude, 'meal_type':self.meal_type, 'meal_time':self.meal_time, 'filled' :self.filled}
    

class Proposal(Base):
    __tablename__ = 'Proposal'
    id = Column(Integer, primary_key=True)
    user_proposed_to = Column(Integer)
    user_proposed_from = Column(Integer)
    request_id = Column(Integer)
    filled = Column(Integer)
    @property
    def serialize(self):
        return {'id':self.id, 'user_proposed_from':self.user_proposed_from, 'user_proposed_to':self.user_proposed_to, 'request_id':self.request_id, 'filled' :self.filled}

class MealDate(Base):
    __tablename__ = 'MealDate'
    id = Column(Integer, primary_key=True)
    user_1 = Column(Integer)
    user_2 = Column(Integer)
    restaurant_name = Column(String)
    restaurant_address = Column(String)
    restaurant_picture = Column(String)
    meal_time = Column(Integer)
    @property
    def serialize(self):
        return {'id':self.id, 'user_1':self.user_1, 'user_2':self.user_2, 'restaurant_name':self.restaurant_name, 'restaurant_address' :self.restaurant_address, 'restaurant_picture' :self.restaurant_picture, 'meal_time' :self.meal_time}



engine = create_engine('sqlite:///meetneat.db')
 

Base.metadata.create_all(engine)
    

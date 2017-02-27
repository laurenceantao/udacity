from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from puppies import Base, Shelter, Puppy
import datetime
from sqlalchemy import desc

engine = create_engine('sqlite:///puppyshelter.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

print('1. Puppies in alphabetical order ascending')
query = session.query(Puppy).order_by(Puppy.name).all()
for item in query:
	print(item.name)

print('2. Puppies younger than 6 months, youngest to oldest')
last_six_months = datetime.datetime.now() - datetime.timedelta(days=365.25/2)
query = session.query(Puppy).filter(Puppy.dateOfBirth > last_six_months).order_by(desc(Puppy.dateOfBirth))
for item in query:
	print(item.name + '		' + str(item.dateOfBirth))

print('3. Puppies by weight ascending')
query = session.query(Puppy).order_by(Puppy.weight)
for item in query:
	print(item.name + '		' + str(item.weight))

print('4. Puppies grouped by shelter')
query = session.query(Puppy, Shelter).join(Shelter).order_by(Puppy.shelter_id).all()
for item in query:
	print(item.Puppy.name + '		' + str(item.Shelter.name))
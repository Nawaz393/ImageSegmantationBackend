# from pymodm import  fields, MongoModel,connect

from mongoengine import Document, StringField, IntField, connect
try:
    # Connect to MongoDB database
    connect("SegmantationDb",host="mongodb+srv://root:12345678.@cluster0.eldclyy.mongodb.net",alias="user_db")
    print("Successfully connected to the database")
except Exception as e:
    print("Error in connecting to the database:", e)


class Image(Document):
    userId=StringField()
    imagePath=StringField()
    maskPath=   StringField()
    imageType=StringField()
    meta={'db_alias':'user_db'}


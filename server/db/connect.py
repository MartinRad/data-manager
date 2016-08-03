# -*-coding:Utf-8 -*
import pymongo
from pymongo import MongoClient 

def write():
    PRODUCTION_URI = 'mongodb://owner:rad0109@ds019123.mlab.com:19123/heroku_sf4njt68'
    client=MongoClient(PRODUCTION_URI)
    return client['heroku_sf4njt68']

def read():
    READONLY_URI = 'mongodb://reader:reader@ds019123.mlab.com:19123/heroku_sf4njt68'
    client=MongoClient(READONLY_URI)
    return client['heroku_sf4njt68']

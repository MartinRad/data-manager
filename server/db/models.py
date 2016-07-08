# -*-coding:Utf-8 -*
import pymongo
from pymongo import MongoClient 
import datetime
import time
import json
from server.server import db


def connect(read_only=False):
    if read_only:
        READONLY_URI = 'mongodb://reader:reader@ds019123.mlab.com:19123/heroku_sf4njt68'
        print("connecting to my mongo db (read only)...")
        client=MongoClient(READONLY_URI)
    else:
        PRODUCTION_URI = 'mongodb://owner:rad0109@ds019123.mlab.com:19123/heroku_sf4njt68'
        print("connecting to my mongo db ...")
        client=MongoClient(PRODUCTION_URI)
    return client
        
def connect_to_database(client,db='heroku_sf4njt68'):
    db=client[db]
    return db


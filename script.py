# -*-coding:Utf-8 -*
import pymongo
from pymongo import MongoClient 
import datetime
import time
import json
import operator

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

def prod_connect(read_only=False):
    if read_only:
        READONLY_URI = 'mongodb://reader:reader@ds011472.mlab.com:11472/heroku_bx4sjs9t'
        print("connecting to my mongo db (read only)...")
        client=MongoClient(READONLY_URI)
    else:
        PRODUCTION_URI = 'mongodb://vincent:20100monet@ds011472.mlab.com:11472/heroku_bx4sjs9t'
        print("connecting to my mongo db ...")
        client=MongoClient(PRODUCTION_URI)
    return client

        
def connect_to_database(client,db='heroku_sf4njt68'):
    db=client[db]
    return db

client=connect()
prod_client=prod_connect()
db=connect_to_database(client)
db_prod=connect_to_database(prod_client,'heroku_bx4sjs9t')

collection_names=db.collection_names()
prod_collection_names=db_prod.collection_names()


def print_all_documents(db,collection_name):
    all_docs=[]
    for item in db.get_collection(collection_name).find():
        print(item)
        all_docs.append(item)
    return all_docs

columns_to_use=db.get_collection("ColumnsToUse")
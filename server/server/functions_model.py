# -*- coding: utf-8 -*-
"""
Created on Fri Mar 25 16:18:46 2016

@author: radagent
"""

########## PACKAGES IMPORT #######

import pandas as pd
import requests
import sys
import numpy as np
import datetime
import json
import uuid
import operator
from server.db import models
from bson import ObjectId


############## VARIABLES SET-UP ####################

collection_for_parametres="CollectionForParametres"
collection_for_columns="CollectionForColumns"
collection_for_functions="CollectionForFunctions"

actions=["view","edit","create","create_several","close_values"]
variables_for_admin_collection=["name_collection","table_td","name_column","type_column","position_column"]+actions

###################################
################# ADMIN COLLECTIONS
###################################

def get_all_documents(db,name_collection):
    all_docs=[]
    for item in db.get_collection(name_collection).find():
        all_docs.append(item)
    return all_docs


def order_columns_position(db, collection):
    bulk=db.get_collection(collection_for_parametres).initialize_ordered_bulk_op()
    columns=collection["columns"]
    columns_order={k:columns[k]["position"] for k in columns}
    sorted_dico = sorted(columns_order.items(), key=operator.itemgetter(1))
    for k in range(len(sorted_dico)):
        column_id=sorted_dico[k][0]
        bulk.find({"_id":collection["_id"]}).update({'$set':{"columns."+str(column_id)+".position":k+1}})
    try:
        result= bulk.execute()
    except:
        0
    return 0

def edit_collection(db, collection,request):
    bulk=db.get_collection(collection_for_parametres).initialize_ordered_bulk_op()
    columns_id=list(collection["columns"].keys())
    name_collection=request.form.get("name_collection")
    table_td=request.form.get("table_td")
    name_column_all=dict(zip(columns_id,request.form.getlist("name_column")))
    type_column_all=dict(zip(columns_id,request.form.getlist("type_column")))
    position_column_all=dict(zip(columns_id,request.form.getlist("position_column")))
    bulk.find({"_id":collection["_id"]}).update({'$set':{"name_collection":name_collection,"table_td":table_td}})
    for column_id in columns_id :
        bulk.find({"_id":collection["_id"]}).update({'$set':{"columns."+str(column_id)+".name":name_column_all[column_id],"columns."+str(column_id)+".alias":name_column_all[column_id],"columns."+str(column_id)+".type":type_column_all[column_id],"columns."+str(column_id)+".position":position_column_all[column_id]}})
    for action in actions :
        list_for_action=request.form.getlist(action)
        for column_id in columns_id :
            if column_id in list_for_action :
                bulk.find({"_id":collection["_id"]}).update({'$set':{"columns."+str(column_id)+"."+action:True}})
            else :
                bulk.find({"_id":collection["_id"]}).update({'$set':{"columns."+str(column_id)+"."+action:False}})
    
    result= bulk.execute()
    return 0    

def create_new_collection(db,request):
    # Create collection parameter
    set_up={}
    set_up["name_collection"]=request.form.get("name_collection")
    set_up["table_td"]=request.form.get("table_td")
    set_up ["created_at"]=datetime.datetime.now()
    set_up["functions_to_apply"]=request.form.getlist("functions_to_apply")
    columns_to_use=request.form.getlist("columns_to_use")
    set_up["columns"]={}
    k=0
    for column_id in columns_to_use :
        set_up["columns"][column_id]=db.get_collection(collection_for_columns).find_one({"_id":ObjectId(column_id)})
        set_up["columns"][column_id]["position"]=k
        k=k+1
        set_up["columns"][column_id].pop("values")

    if not db.get_collection(collection_for_parametres).find_one({"name_collection" : set_up["name_collection"]}):
        result=db.get_collection(collection_for_parametres).insert_one(set_up)
        collection_id=result.inserted_id
        db.create_collection(str(collection_id))
    # Create collection
    return 0

def add_new_column(db,collection,request):
    column_id=request.form.get("column_to_add")
    if not column_id=='other':
        new_column=db.get_collection(collection_for_columns).find_one({"_id":ObjectId(column_id)})
    else :    
        new_column={
                    "name" : "NewColumn",
                    "alias" : "NewColumn",
                    "type" : "string",
                    "view" : False,
                    "create" : False,
                    "create_several" : False,
                    "edit" : False,
                    "close_values" : False,
        }
        result=db.get_collection(collection_for_columns).insert_one(new_column)
        column_id=result.inserted_id
    new_column["position"]=len(collection["columns"])+1
    db.get_collection(collection_for_parametres).update_one({"_id":collection["_id"]},{"$set" :{"columns."+str(column_id) : new_column}})

    bulk=db.get_collection(str(collection["_id"])).initialize_ordered_bulk_op()
    bulk.find({}).update({'$set': {str(column_id) : ""}})
    try :
        result= bulk.execute()
    except :
        result = 0
    return 0

def delete_column(db,collection,request):
    columns_to_delete=request.form.getlist("list_deleted")
    columns=collection["columns"]
    for column_id in columns_to_delete:
        columns.pop(column_id)
        db.get_collection(collection_for_parametres).update_one({"_id":collection["_id"]},{"$unset" :{"columns."+str(column_id):"" }})
        bulk=db.get_collection(str(collection["_id"])).initialize_ordered_bulk_op()
        bulk.find({}).update({'$unset': {column_id : ""}})
        try :
            result= bulk.execute()
        except :
            result = 0
    order_columns_position(db, collection)
    return 0

def get_columns_order(db,collection):
    columns=collection["columns"]
    columns_order={k:int(columns[k]["position"]) for k in columns}
    columns_order = sorted(columns_order.items(), key=operator.itemgetter(1))
    return columns_order

def get_columns_for(db,collection, actions):
    columns_order=get_columns_order(db,collection)
    dict_columns_for={}
    columns=collection["columns"]
    for action in actions :
        dict_columns_for[action]=[]
        for item in columns_order :
            try :
                if columns[item[0]][action] :
                    dict_columns_for[action].append(item[0])
            except :
                0
    dict_columns_for["order"]=list(columns_order[k][0] for k in range(len(columns_order)))
    return dict_columns_for

def get_collection(db,name_collection):
    collection=db.get_collection(collection_for_parametres).find_one({"name_collection" : name_collection})
    return collection


def get_column_name(db,collection,column_id):
    return db.get_collection(collection_for_parametres).find({"_id":collection["_id"]})["columns"][ObjectId(column_id)]["name"]

def view_collection(db,collection):
    active_collection=db.get_collection(str(collection["_id"]))
    dict_columns_for=get_columns_for(db,collection,actions)
    columns_for_view=dict_columns_for["view"]
    columns_for_order=dict_columns_for["order"]
    result=active_collection.find().sort({column_id:1 for column_id in columns_for_order})
    data=[]
    dict_columns_name={}
    for item in result:
        set_up={}
        for column_id in item :
            if not column_id in dict_columns_name :
                dict_columns_name[column_id]=get_column_name(db,collection,column_id)
            set_up[dict_columns_name[column_id]]=item[column_id]
        data.append(set_up)
    return data






















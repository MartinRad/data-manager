# -*-coding:Utf-8 -*
import sys
import os
from flask import request, abort, redirect, url_for, render_template
from server.server import app
from server.db import connect
from server.server.functions_model import *
import pandas as pd
from flask.ext.basicauth import BasicAuth


basic_auth = BasicAuth(app)

db = connect.write()

@app.route('/hello')
def hello_world():
    try:
        return "hello"
    except HTTPException as e:
        raise e
    except:
        print(("Unexpected error:", sys.exc_info()))
        abort(500)


@app.route('/',methods=['GET', 'POST'])
@basic_auth.required
def navigate():
    collection_names=[]
<<<<<<< HEAD
    for item in db.collection_for_parametres.find():
        collection_names.append(item["name_collection"])
=======
    for item in db.get_collection(collection_for_parametres).find():
        collection_names.append(item.get("name_collection"))
>>>>>>> 367169641c56033121d528f7489ba142ef949bb3
    if request.method == 'POST':
        for collection_name in collection_names :
            if request.form['btn']== collection_name :
                return redirect(url_for('admin',name_collection=collection_name))
        if request.form['btn']== "CREATE NEW COLLECTION" :
                return redirect(url_for('create_collection'))
    return render_template('home.html',collection_names=collection_names)

@app.route('/create',methods=['GET', 'POST'])
@basic_auth.required
def create_collection():
    all_functions=get_all_documents(db,collection_for_functions)
    all_columns=get_all_documents(db,collection_for_columns)
    if request.method == 'POST':
        if request.form['btn']== "CREATE" :
            create_new_collection(db,request)
            name_collection=request.form.get("name_collection")
            return redirect(url_for('admin',name_collection=name_collection))
        if request.form['btn']== "CANCEL" :
            return redirect(url_for('navigate'))
    return render_template('create_collection.html',all_functions=all_functions, all_columns=all_columns)



@app.route('/admin/<name_collection>',methods=['GET', 'POST'])
@basic_auth.required
def admin(name_collection):
    all_columns=get_all_documents(db,collection_for_columns)
    collection=get_collection(db,name_collection)
    dict_columns_for=get_columns_for(db,collection,actions)
    if request.method == 'POST':
        if request.form['btn']== 'VIEW' :
            return redirect(url_for('main_view',name_collection=name_collection))
        if request.form['btn']== 'SAVE' :
            edit_collection(db, collection,request)
            name_collection=request.form.get("name_collection")
            return redirect(url_for('admin',name_collection=name_collection))
        #elif request.form['btn']== 'ORDER COLUMNS' :
            #return redirect(url_for('admin_reorder',collection=collection))
        elif request.form['btn']== 'DELETE COLUMN' :
            delete_column(db,collection,request)
            return redirect(url_for('admin',name_collection=name_collection))
        elif request.form['btn']== 'ADD' :
            add_new_column(db,collection,request)
            return redirect(url_for('admin',name_collection=name_collection))

    return render_template('admin.html',collection=collection,message="",dict_columns_for=dict_columns_for,actions=actions,all_columns=all_columns)



@app.route('/view/<name_collection>',methods=['GET', 'POST'])
@basic_auth.required    
def main_view(name_collection):
    now=datetime.datetime.now()
    delta=datetime.timedelta(seconds=120)
    collection=get_collection(db,name_collection)
    dict_columns_for=get_columns_for(db,collection,actions)
    data=view_collection(db,collection)
    is_active_id=str(db.get_collection("CollectionForColumns").find_one({'name':'is_active'})['_id'])
    created_at_id=str(db.get_collection("CollectionForColumns").find_one({'name':'created_at'})['_id'])
    if request.method == 'POST':
        if request.form['btn']== 'EDIT' :
            return redirect(url_for('edit',name_collection=name_collection))
        elif request.form['btn']== 'SEND' :
            table_td=get_table_td(db,db.get_collection(collection))
            is_ok=synchronyse_collection_with_td(db,collection,database_td,table_td) 
            return render_template('main_view.html',collection=collection,dict_columns_for=dict_columns_for,data=data,data_view=data_view,data_index=data_index,message=is_ok,now=now,delta=delta)
        elif request.form['btn']== 'CREATE' :
            return redirect(url_for('create',name_collection=name_collection))            
        elif request.form['btn']== 'CHECK' :
            update_collection_dates(db,data,collection)
            return redirect(url_for('main_view',collection=collection))            
    return render_template('view.html',collection=collection,data=data,dict_columns_for=dict_columns_for,message="",now=now,delta=delta,is_active_id=is_active_id,created_at_id=created_at_id)




@app.route('/edit/<name_collection>',methods=['GET', 'POST'])
@basic_auth.required    
def edit(name_collection):
    now=datetime.datetime.now()
    delta=datetime.timedelta(seconds=120)
    collection=get_collection(db,name_collection)
    dict_columns_for=get_columns_for(db,collection,actions)
    data=view_collection(db,collection)
    is_active_id=str(db.get_collection("CollectionForColumns").find_one({'name':'is_active'})['_id'])
    created_at_id=str(db.get_collection("CollectionForColumns").find_one({'name':'created_at'})['_id'])
    if request.method == 'POST':
        if request.form['btn']== 'SAVE' :
            result =edit_collection(db,data,collection,request)
            data,data_view=get_collection(db,collection,{})
            update_collection_dates(db,data,collection)
            return redirect(url_for('main_view',collection=collection))
        elif request.form['btn']== 'VIEW' :
            return redirect(url_for('main_view',collection=collection))
        elif request.form['btn'] == 'DELETE' :
            delete_collection(db,data,collection,request)
            data,data_view=get_collection(db,collection,{})
            #update_collection_dates(db,data,collection)
            return redirect(url_for('main_view',collection=collection))
    return render_template('edit.html',collection=collection,data=data,dict_columns_for=dict_columns_for,message="",now=now,delta=delta,is_active_id=is_active_id,created_at_id=created_at_id)

@app.route('/create/<name_collection>',methods=['GET', 'POST'])   
@basic_auth.required 
def create(name_collection):
    collection=get_collection(db,name_collection)
    values_for_columns={}
    for item in db.get_collection(collection_for_columns).find() :
        values_for_columns[str(item["_id"])]=item
    dict_columns_for=get_columns_for(db,collection,actions)
    if request.method == 'POST':
        if request.form['btn']== 'CREATE' :
            create_multiple_documents(db,collection,dict_columns_for,request)
            return redirect(url_for('main_view',name_collection=name_collection))
        elif request.form['btn']== 'CANCEL' :
            return redirect(url_for('main_view',collection=collection))
    return render_template('create.html',collection=collection,values_for_columns=values_for_columns,dict_columns_for=dict_columns_for,message="")
























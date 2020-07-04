# Cloud Firestore
import firebase_admin
from firebase_admin import credentials, db, firestore

import configparser
import numpy as np
import cv2
from datetime import datetime

from clan_sheet import *

config = configparser.ConfigParser()
config.read('config.ini')
# config.read('test_config.ini')
cred = credentials.Certificate(config.get('cloud-firestore', 'firebase_key')) # Service Account Key Address
firebase_admin.initialize_app(cred, {
    'databaseURL' : config.get('cloud-firestore', 'url') # Firebase Url
})
db = firestore.client()


def create_line_user(name, group_id, user_id):

    initial_score = 5
    doc_ref = db.collection("line_user")
    keys = ['name', 'group_id', 'user_id', 'data', 'score', 'search_self_record']
    values =[name, group_id, user_id, [], initial_score, False]
    records = dict(zip(keys, values))
    doc_ref.add(records)


def delete_line_user(user_id):
    
    doc_ref = db.collection("arena_record")
    results = doc_ref.where('provider','array_contains', user_id).stream()
    for item in results:
        data_id = item.id
        data = item.to_dict()
        doc = doc_ref.document(data_id)
        data['provider'].remove(user_id)
        field_updates = {'provider': data['provider']}
        doc.update(field_updates)
    
    doc_ref = db.collection("line_user")
    docs = doc_ref.where('user_id', '==', user_id).stream()
    for doc in docs:
        doc.reference.delete()

def update_user_database(user_id, status):
    
    doc_ref = db.collection("line_user")
    results = doc_ref.where('user_id', '==', user_id).stream()
    for item in results:
        doc = doc_ref.document(item.id)
        field_updates = {'search_self_record': status}
        doc.update(field_updates)


def update_line_user(user_id, data_id):

    doc_ref = db.collection("line_user")
    results = doc_ref.where('user_id', '==', user_id).stream()
    for item in results:
        doc = doc_ref.document(item.id)
        data = item.to_dict()
        if data_id not in data['data']:
            data['data'].append(data_id)
            field_updates = {'data': data['data'], 'score': data['score']+5}
            doc.update(field_updates)


def create_line_group(group_name, group_id):

    doc_ref = db.collection("line_group")
    keys = ['group_name', 'group_id', 'sheet_url', 'group_admin', 'group_member']
    values =[group_name, group_id, '', {}, {}]
    group = dict(zip(keys, values))
    doc_ref.add(group)


def delete_line_group(group_id):

    doc_ref = db.collection("line_group")
    docs = doc_ref.where('group_id', '==', group_id).stream()
    for doc in docs:
        doc.reference.delete()


def search_line_group(group_id):
    
    doc_ref = db.collection("line_group")
    # group_id = 'C1f08f2cc641df24f803b133691e46e92'
    results = doc_ref.where('group_id', '==', group_id).stream()

    return results

def update_line_group(group_id, user_id, user_name):
    
    doc_ref = db.collection("line_user")
    results = doc_ref.where('name', '==', user_name).stream()
    
    find = False
    for item in results:
        find = True
        doc = doc_ref.document(item.id)
        field_updates = {'group_id': group_id}
        doc.update(field_updates)

    if find == False:
        create_line_user(user_name, group_id, user_id)

    
    doc_ref = db.collection("line_group")
    results = doc_ref.where('group_id','==', group_id).stream()
    for item in results:
        # print(u'{} => {}'.format(item.id, item.to_dict()))
        data_id = item.id
        data = item.to_dict()

    if user_name in data['group_member']:
        reply_msg = '加入失敗，' + user_name + '，你已經在戰隊成員裡。'
    else:
        data['group_member'][user_name] = user_id
        doc = doc_ref.document(item.id)
        field_updates = {'group_member': data['group_member']}
        doc.update(field_updates)
        reply_msg = user_name + '，你成功加入戰隊成員。'

    # print(reply_msg)
    return reply_msg

def delete_line_group_member(group_id, user_id):

    group_id = 'C1f08f2cc641df24f803b133691e46e92'
    doc_ref = db.collection("line_group")
    results = doc_ref.where('group_id','==', group_id).stream()
    data = {}
    for item in results:
        data_id = item.id
        data = item.to_dict()

    for key,value in data['group_member'].items():
        if user_id == value:
            del data['group_member'][key]
            break
    
    doc = doc_ref.document(data_id)
    field_updates = {'group_member': data['group_member']}
    doc.update(field_updates)


def get_group_member(group_id):
    
    doc_ref = db.collection("line_group")
    results = doc_ref.where('group_id','==', group_id).stream()
    for item in results:
        # print(u'{} => {}'.format(item.id, item.to_dict()))
        # data_id = item.id
        data = item.to_dict()

    group_member = data['group_member']
    return group_member

def get_user_id(user_name):
    
    doc_ref = db.collection("line_user")
    results = doc_ref.where('name','==', user_name).stream()
    data = {}
    for item in results:
        data = item.to_dict()

    user_id = data['user_id']
    return user_id

def get_user_info(user_id):
    
    doc_ref = db.collection("line_user")
    results = doc_ref.where('user_id','==', user_id).stream()
    data = {}
    for item in results:
        data = item.to_dict()
    return data

def get_user_database(user_id):

    doc_ref = db.collection("line_user")
    results = doc_ref.where('user_id','==', user_id).stream()
    data = {}
    for item in results:
        data = item.to_dict()

    status = data['search_self_record']
    return status


def insert_arena_record(our, enemy, win, provider):

    doc_ref = db.collection("arena_record")
    ISOTIMEFORMAT = '%Y-%m-%d %H:%M:%S'
    nowTime = datetime.now().strftime(ISOTIMEFORMAT)

    keys = ['our', 'enemy', 'win', 'updated', 'good', 'bad', 'provider']
    values =[our , enemy , win, nowTime, 1, 0, [provider]]
    records = dict(zip(keys, values))

    return doc_ref.add(records)


def update_arena_record(data_id, data):
    
    doc_ref = db.collection('arena_record')
    doc = doc_ref.document(data_id)
    doc.update(data)


def find_arena_record(our, enemy, win, provider):
    
    status = ''
    ISOTIMEFORMAT = '%Y-%m-%d %H:%M:%S'
    nowTime = datetime.now().strftime(ISOTIMEFORMAT)
    
    doc_ref = db.collection('arena_record')
    results = doc_ref.where('our', '==', our).where('enemy', '==', enemy).stream()
    
    data_id = None
    find = False
    for item in results:
        find = True
        data_id = item.id
        data = item.to_dict()
        if win == data['win']:
            data['good'] += 1
        else:
            data['bad'] += 1

    if find == False:
        data_ref = insert_arena_record(our, enemy, win, provider)
        update_line_user(provider, data_ref[1].id)
        status = 'success'
    else:
        if provider not in data['provider']:
            update_line_user(provider, data_id)
            data['provider'].append(provider)
            field_updates = {'updated': nowTime, "good": data['good'], 'bad': data['bad'], 'provider': data['provider']}
            update_arena_record(data_id, field_updates)
            status = 'success'
        else:
            status = 'repeat'
    
    return status


def search_arena_record(enemy, user_id):
    
    way = 'global'

    doc_ref = db.collection("line_user")
    results = doc_ref.where('user_id','==', user_id).stream()
    data = {}
    for item in results:
        data = item.to_dict()
        if data['search_self_record'] == True:
            way = 'local'

    doc_ref = db.collection('arena_record')
    if way == 'global':
        results = doc_ref.where('enemy', '==', enemy).stream()
    else:
        results = doc_ref.where('enemy', '==', enemy).where('provider', 'array_contains', user_id).stream()

    record = []
    good = []
    bad = []
    find = False
    for item in results:
        find = True
        data = item.to_dict()
        record.append(data['our'])
        good.append(data['good'])
        bad.append(data['bad'])
        
    return record, good, bad


def sort_arena_record(record, good, bad):
    records = []
    for i in range(len(record)):
        score = int(good[i]) - 2*int(bad[i])
        records.append([record[i], good[i], bad[i], score])

    records= sorted(records, key = lambda s: s[3], reverse = True)

    record = []
    good = []
    bad = []
    for i in range(len(records)):
        record.append(records[i][0])
        good.append(records[i][1])
        bad.append(records[i][2])

    return record, good, bad
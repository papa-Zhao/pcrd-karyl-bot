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
cred = credentials.Certificate(config.get('cloud-firestore', 'firebase_key')) # Service Account Key Address
firebase_admin.initialize_app(cred, {
    'databaseURL' : config.get('cloud-firestore', 'url') # Firebase Url
})
db = firestore.client()

def create_line_user(name, group_id, user_id):

    initial_score = 5    
    doc_ref = db.collection("line_user")
    keys = ['name', 'group_id', 'user_id', 'data', 'group_data', 'group_notes', 'score', 'search_self_record']
    values =[name, [], user_id, {}, {}, {}, initial_score, False]
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

def update_line_user_data(user_id, data_id, win):
    
    status = ''
    doc_ref = db.collection("line_user")
    results = doc_ref.where('user_id', '==', user_id).stream()
    
    find = False
    for item in results:
        find = True
        doc = doc_ref.document(item.id)
        data = item.to_dict()
        try:
            if data['data'][data_id] != win:
                # print('change')
                status = 'change'
                data['data'][data_id] = win
                field_updates = {'data': data['data']}
                doc.update(field_updates)
                return status
        except KeyError:
            # print('KeyError')
            try:
                data['data'][data_id] = win
                field_updates = {'data': data['data'], 'score': data['score']+5}
                doc.update(field_updates)
            except KeyError:
                # print('Double KeyError')
                field_updates = {'data': {data_id: win}, 'score': data['score']+5}
                doc.update(field_updates)
            status = 'success'
            return status
        
        status = 'repeated'
        return status
    
def get_all_subscriber():
    
    user = []
    doc_ref = db.collection('news_subscriber')
    results = doc_ref.stream()
    for item in results:
        find = True
        data_id = item.id
        data = item.to_dict()
        user = data['token']
    
    return user

def get_group_arena_utmost_star(group_id):

    doc_ref = db.collection("line_group")
    results = doc_ref.where('group_id', '==', group_id).stream()
    status = None
    for item in results:
        data = item.to_dict()
        status = data['is_char_utmost_6x']

    return status


def update_group_arena_utmost_star(group_id, status):

    doc_ref = db.collection("line_group")
    results = doc_ref.where('group_id', '==', group_id).stream()
    for item in results:
        doc = doc_ref.document(item.id)
        field_updates = {'is_char_utmost_6x': status}
        doc.update(field_updates)

def update_user_arena_database(user_id, status):
    
    doc_ref = db.collection("line_user")
    results = doc_ref.where('user_id', '==', user_id).stream()
    for item in results:
        doc = doc_ref.document(item.id)
        field_updates = {'search_self_record': status}
        doc.update(field_updates)


def create_line_group(group_name, group_id):

    doc_ref = db.collection("line_group")
    keys = ['group_name', 'group_id', 'group_admin', 'group_member', 'data', 'is_char_utmost_6x', 'sheet_url']
    values =[group_name, group_id, {}, {}, {}, True, '']
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

def get_user_arena_database(user_id):

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

    keys = ['atk', 'def', 'updated', 'good', 'bad', 'provider']
    if win == True:
        values =[our, enemy, nowTime, 1, 0, {provider: win}]
    else:
        values =[our, enemy, nowTime, 0, 1, {provider: win}]
        
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
    results = doc_ref.where('atk', '==', our).where('def', '==', enemy).stream()
    
    data_id = None
    find = False
    for item in results:
        find = True
        data_id = item.id
        data = item.to_dict()
        if win == True:
            data['good'] += 1
        else:
            data['bad'] += 1

    if find == False:
        data_ref = insert_arena_record(our, enemy, win, provider)
        status = update_line_user_data(provider, data_ref[1].id, win)
    else:
        if provider not in data['provider']:
            status = update_line_user_data(provider, data_id, win)
            data['provider'][provider] = win
            field_updates = {'updated': nowTime, "good": data['good'], 'bad': data['bad'], 'provider': data['provider']}
            update_arena_record(data_id, field_updates)
        else:
            status = update_line_user_data(provider, data_id, win)
            # print('status = ', status)
            if status == 'change':
                # print('find_arena_record change')
                data['provider'][provider] = win
                if win == True:
                    data['bad'] -= 1
                else:
                    data['good'] -= 1
                field_updates = {'updated': nowTime, "good": data['good'], 'bad': data['bad'], 'provider': data['provider']}
                update_arena_record(data_id, field_updates)

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
    results = doc_ref.where('def', '==', enemy).stream()

    record, good, bad, provide = [], [], [], []
    find = False
    for item in results:
        find = True
        data = item.to_dict()
        try:
            if way == 'global':
                record.append(data['atk'])
                good.append(data['good'])
                bad.append(data['bad'])
                if user_id in data['provider']:
                    provide.append(data['provider'][user_id])
                else:
                    provide.append(None)
            
            if way == 'local' and data['provider'][user_id] == True:
                record.append(data['atk'])
                good.append(data['good'])
                bad.append(data['bad'])
                provide.append(None)
        except KeyError:
            print('')
        
    return record, good, bad, provide


def sort_user_arena_record(record, good, bad, provide):
    
    records = []
    for i in range(len(record)):
        score = int(good[i]) - 2 * int(bad[i])
        records.append([record[i], good[i], bad[i], provide[i], score])

    records= sorted(records, key = lambda s: s[4], reverse = True)

    record, good, bad, provide = [], [], [], []
    for i in range(len(records)):
        record.append(records[i][0])
        good.append(records[i][1])
        bad.append(records[i][2])
        provide.append(records[i][3])

    return record, good, bad, provide


def sort_arena_record(record, good, bad):
    
    records = []
    for i in range(len(record)):
        score = int(good[i]) - 2 * int(bad[i])
        records.append([record[i], good[i], bad[i], score])

    records= sorted(records, key = lambda s: s[3], reverse = True)

    record, good, bad = [], [], []
    for i in range(len(records)):
        record.append(records[i][0])
        good.append(records[i][1])
        bad.append(records[i][2])

    return record, good, bad


def insert_group_arena_record(our, enemy, win, group_id):

    doc_ref = db.collection("group_arena_record")
    ISOTIMEFORMAT = '%Y-%m-%d %H:%M:%S'
    nowTime = datetime.now().strftime(ISOTIMEFORMAT)

    keys = ['atk', 'def', 'updated', 'good', 'bad', 'group_id', 'notes']
    if win == True:
        values =[our, enemy, nowTime, 1, 0, group_id, []]
    else:
        values =[our, enemy, nowTime, 0, 1, group_id, []]

    records = dict(zip(keys, values))
    return doc_ref.add(records)


def update_line_group_data(group_id, data_id, win):

    doc_ref = db.collection("line_group")
    results = doc_ref.where('group_id', '==', group_id).stream()
    for item in results:
        doc = doc_ref.document(item.id)
        data = item.to_dict()
        try:
            if data['data'][data_id] == win:
                data['data'][data_id] = win
                field_updates = {'data': data['data']}
                doc.update(field_updates)
        except KeyError:
            field_updates = {'data': {data_id: win}}
            doc.update(field_updates)


def update_group_arena_record(data_id, data):
    
    doc_ref = db.collection('group_arena_record')
    doc = doc_ref.document(data_id)
    doc.update(data)


def find_group_arena_record(our, enemy, win, group_id):
    
    status = ''
    ISOTIMEFORMAT = '%Y-%m-%d %H:%M:%S'
    nowTime = datetime.now().strftime(ISOTIMEFORMAT)
    
    doc_ref = db.collection('group_arena_record')
    results = doc_ref.where('atk', '==', our).where('def', '==', enemy).where('group_id', '==', group_id).stream()
    
    data_id = None
    find = False
    for item in results:
        find = True
        data_id = item.id
        data = item.to_dict()
        if win == True:
            data['good'] += 1
        else:
            data['bad'] += 1

    if find == False:
        data_ref = insert_group_arena_record(our, enemy, win, group_id)
        update_line_group_data(group_id, data_ref[1].id, win)
        status = 'success'
    else:
        field_updates = {'updated': nowTime, "good": data['good'], 'bad': data['bad']}
        update_group_arena_record(data_id, field_updates)
        status = 'success'
    
    return status


def search_group_arena_record(enemy, group_id):
    
    doc_ref = db.collection('group_arena_record')
    results = doc_ref.where('def', '==', enemy).where('group_id', '==', group_id).stream()

    record, good, bad = [], [], []
    find = False
    for item in results:
        find = True
        data = item.to_dict()
        record.append(data['atk'])
        good.append(data['good'])
        bad.append(data['bad'])
        
    return record, good, bad


def insert_line_notify_subscriber(token, user_id):

    doc_ref = db.collection("news_subscriber")
    results = doc_ref.stream()
    for item in results:
        find = True
        data_id = item.id
        data = item.to_dict()
        doc = doc_ref.document(data_id)
        try:
            data['token'][user_id] = token
            field_updates = {'token': data['token']}
            doc.update(field_updates)
        except KeyError:
            field_updates = {'token': {user_id: token}}
            doc.update(field_updates)
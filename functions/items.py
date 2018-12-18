import firebase_admin
from firebase_admin import db
import flask
import numpy


def create_item(type, data):
    item = db.reference('items/{}/'.format(type)).push(data)
    return flask.jsonify({"success": True}), 201

def read_item_by_id_all(uid):
    items = db.reference('items/{}/').get()
    if not user:
        return "Resource is not found", 404
    return flask.jsonify(user)

def read_item_by_type_all(type):
    items = db.reference('items/{}'.format(type)).get()
    if items:
        return list(items.values())
    return None

def update_item(uid, type, tid, data):
    item = db.reference('items/{}/{}/'.format(uid, type)).child(tid).get()
    if not item:
        return "Resource is not found", 404
    req = data.json
    db.reference('items/{}/{}/'.format(uid, type)).child(tid).update(req)
    return flask.jsonify({"success": True})

def delete_item(uid, type, tid):
    item = db.reference('items/{}/{}/'.format(uid, type)).child(tid).get()
    if not item:
        return "Recource is not found", 404
    db.reference('items/{}/{}/'.format(uid, type)).child(tid).delete()
    return flask.jsonify({"success": True})

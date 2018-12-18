import firebase_admin
from firebase_admin import db
import flask

firebase_admin.initialize_app(options={
  "databaseURL": "https://barter-economy-223210.firebaseio.com"
})

def check_user(uid):
    user = db.reference('users/unknow/').child(uid).get()
    if user:
        return {"data": user, "role": "unknow"}
    user = db.reference('users/proposer/').child(uid).get()
    if user:
        return {"data": user, "role": "proposer"}
    user = db.reference('users/checker/').child(uid).get()
    if user:
        return {"data": user, "role": "checker"}
    user = db.reference('users/blocker/').child(uid).get()
    if user:
        return {"data": user, "role": "blocker"}
    return {"data": None, "role": None}

def check_proposer_by_uid(uid):
    return db.reference('proposers/').child(uid).get()

def check_proposer_by_link(link):
    proposers = db.reference('proposers/').get()
    print(proposers)
    for key, value in proposers.items():
        if value["link"] == link:
            return {"uid": key, "data": value}
    return None

def update_proposer(uid, data):
    proposer = db.reference('proposers/{}/'.format(uid)).get()
    if not proposer:
        return "Resource is not found", 404
    db.reference('proposers/{}/'.format(uid)).update(data)
    return flask.jsonify({"success": True})

def create_proposer(uid, data):
    user = db.reference('proposers/{}/'.format(uid)).set(data)
    return flask.jsonify({"success": True}), 201

def create_user(uid, data, type):
    user = db.reference('users/{}/{}'.format(type, uid)).set(data)
    return flask.jsonify({"success": True}), 201

def read_user(uid, type):
    user = db.reference('users/{}/{}/'.format(type, uid)).get()
    if not user:
        return "Resource is not found", 404
    return flask.jsonify(user)

def update_user(uid, data, type):
    user = db.reference('users/{}/{}/'.format(type, uid)).get()
    if not user:
        return "Resource is not found", 404
    db.reference('users/{}/{}/'.format(type, uid)).update(data)
    return flask.jsonify({"success": True})

def delete_user(uid, type):
    user = db.reference('users/{}/{}/'.format(type, uid)).get()
    if not user:
        return "Recource is not found", 404
    db.reference('users/{}/{}/'.format(type, uid)).delete()
    return flask.jsonify({"success": True})

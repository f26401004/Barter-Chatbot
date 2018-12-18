import flask
import json
import os
import requests

def send_text_message(to, message):
    
    post_message_url = "https://graph.facebook.com/v3.2/me/messages?access_token={token}".format(token=os.environ.get("ACCESS_TOKEN"))
    response_message = json.dumps({"recipient":{"id": to}, 
                                   "message":{"text": message}})
    send_res = requests.post(post_message_url, 
                        headers={"Content-Type": "application/json"}, 
                        data=response_message)
    print("[{}] Reply to {}: {}".format(send_res.status_code, to, message))
    return

def send_button_message(to, title, buttons):
    post_button_url = "https://graph.facebook.com/v3.2/me/messages?access_token={token}".format(token=os.environ.get("ACCESS_TOKEN"))
    response_button = json.dumps({
        "recipient": {
            "id": to
        }, 
        "message":{
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "button",
                    "text": title,
                    "buttons": buttons
                }
            }
        }
    })
    send_res = requests.post(post_button_url, 
                        headers={"Content-Type": "application/json"}, 
                        data=response_button)
    print(send_res.text)
    print("[{}] Reply to {}: {}".format(send_res.status_code, to, "button message"))

def send_quick_reply_message(to, title, replies):
    post_button_url = "https://graph.facebook.com/v3.2/me/messages?access_token={token}".format(token=os.environ.get("ACCESS_TOKEN"))
    response_button = json.dumps({
        "recipient": {
            "id": to
        }, 
        "message":{
            "text": title,
            "quick_replies": replies
        }
    })
    send_res = requests.post(post_button_url, 
                        headers={"Content-Type": "application/json"}, 
                        data=response_button)
    print(send_res.text)
    print("[{}] Reply to {}: {}".format(send_res.status_code, to, "button message"))

def send_image_message(to, image_url):
    post_image_url = "https://graph.facebook.com/v3.2/me/messages?access_token={token}".format(token=os.environ.get("ACCESS_TOKEN"))
    print(image_url)
    response_image = json.dumps({
        "recipient": {
            "id": to
        },
        "message": {
            "attachment": {
                "type": "image",
                "payload": {
                    "url": image_url,
                    "is_reusable": True
                }
            }
        }
    })
    send_res = requests.post(post_image_url, 
                        headers={"Content-Type": "application/json"}, 
                        data=response_image)
    print(send_res.text)
    print("[{}] Reply to {}: {}".format(send_res.status_code, to, "image message"))


def get_app_scoped_id(uid):
    post_url = "https://graph.facebook.com/{}".format(uid)
    send_res = requests.post(post_url, 
                        headers={"Content-Type": "application/json"}, 
                        data=response_button)

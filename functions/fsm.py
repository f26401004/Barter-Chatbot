import os
import requests
import datetime
import time
import operator
import users as user_db
import items as item_db
import facebook
from transitions.extensions import GraphMachine
from utils import send_text_message
from utils import send_button_message
from utils import send_quick_reply_message
from utils import send_image_message


class TocMachine(GraphMachine):
    def __init__(self, **machine_configs):
        self.machine = GraphMachine(
            model=self,
            **machine_configs
        )
        self.action = ["我想提議", "最近夯什麼", "我要檢舉"]
        self.type_list = ["食物或飲料", "3C 或電子產品", "衣物", "化妝用品", "書籍", "雜物"]


    def is_empty_string(self, event):
        if event.get('message'):
            text = event["message"]["text"]
            return text == os.environ.get("EMPTY_STRING")
        return False
    def is_empty_image(self, event):
        if not self.is_empty_string(event):
            return True
        if event.get("message") and event['message'].get("attachments"):
            flag = False
            for target in event["message"]["attachments"]:
                if target["type"] != "image":
                    flag = True
            return flag
        return False

    def is_not_digit(self, event):
        if event.get("message"):
            return not event["message"]["text"].isdigit()
        return False
    
    def is_unknow(self, event): 
        if event.get("message"):
            text = event["message"]["text"]
            if not text in self.action:
                return True
        return False
    def is_not_type_choose(self, event):
        if event.get("message"):
            text = event["message"]["text"]
            if text in self.type_list:
                return False
            return True
        return False
   
    def is_number_not_in_item_range(self, event):
        if event.get("message"):
            text = event["message"]["text"]
            sender_id = event["sender"]["id"]
            if text == os.environ.get("EMPTY_STRING"):
                return True
            # get sender from current state
            result = user_db.check_user(sender_id)
            if 'items' in result['data']['data']:
                # get sender current items
                items = result["data"]["data"]["items"]
                if not text.isdigit():
                    return False
                if int(text) > len(items) or int(text) < 1:
                    return True
                return False
        return False


   
    def on_enter_unknow(self, event):
        uid = event["sender"]["id"]
        # get sender current state
        result = user_db.check_user(uid)
        print(result)
        # store the data to items 
        if result["role"] == "proposer":
            data = {
                "proposer": uid,
                "name": result["data"]["data"]["name"],
                "description": result["data"]["data"]["description"],
                "number": result["data"]["data"]["number"],
                "image_url": result["data"]["data"]["image_url"],
                "timestamp": str(datetime.datetime.now())
            }
            item_db.create_item(result["data"]["data"]["type"], data)
            # remind user to pa attention on unfamiliar message
            send_text_message(uid, "資料輸入成功！近期請多注意陌生訊息！")
            # post the articles on page
            # exchanger = user_db.check_proposer_by_uid(uid)
            # post_content = '交換者{} \n 交換物 {} \n 交換物類別 {} \n 交換物敘述 {} \n 交換物數量 {} \n 交換者個人頁面 {}'.format(result["data"]["name"], result["data"]["data"]["name"], result["data"]["data"]["type"], result["data"]["data"]["description"], result["data"]["data"]["number"], exchanger["link"])
            # graph = facebook.GraphAPI(os.environ.get("PAGE_TOKEN"))
            # graph.put_object(os.environ.get("PAGE_ID"), "feed", message=post_content)
        elif result["role"] == "updater":
            item_db.update_item(uid, result["data"]["type"], result["data"]["tid"], result["data"]["data"]["item"])
        # elif result["role"] == "checker":
        # elif result["role"] == "blocker":
        # delete user from user current type
        if result["role"]:
            user_db.delete_user(uid, result["role"])
        # get sender name
        get_url = "https://graph.facebook.com/v3.2/{uid}?fields=name&access_token={token}".format(uid=uid, token=os.environ.get("ACCESS_TOKEN"))
        get_name_res = requests.get(get_url).json()
        print(get_name_res)
        # create user info in unknow
        user_db.create_user(uid, {"name": get_name_res["name"]}, "unknow")
        # say hello to sneder
        replies = []
        for target in self.action:
            replies.append({
                    "content_type": "text",
                    "title": target,
                    "payload": target
                })
        send_quick_reply_message(uid, "Hello, {}。歡迎使用 Barter！請輸入行為以繼續使用".format(get_name_res["name"]), replies)

    
    ##################################################
    # Proposer
    ##################################################
    
    def is_proposer_no_info(self, event):
        if event.get("message"):
            text = event["message"]["text"]
            uid = event["sender"]["id"]
            if text == self.action[0]:
                # get sender from unknow state
                result = user_db.check_user(uid)
                # check proposer credit
                proposer_info = user_db.check_proposer_by_uid(uid)
                if proposer_info:
                    return False
                # establish proposer data
                info = {
                    "name": result["data"]["name"],
                    "link": "",
                    "credit": 100
                }
                user_db.create_proposer(uid, info)
                proposer_info = user_db.check_proposer_by_uid(uid)
                # update the user to proposer state 1
                data = {
                    "name": result["data"]["name"],
                    "state": "proposer_state1",
                    "data": {
                    }
                }
                user_db.create_user(uid, data, "proposer")
                # delete sender from unknow state
                user_db.delete_user(uid, "unknow")
            return text == self.action[0]
        return False

    def is_proposer_with_info(self, event):
        if event.get("message"):
            text = event["message"]["text"]
            uid = event["sender"]["id"]
            if text == self.action[0]:
                # get sender from unknow state
                result = user_db.check_user(uid)
                # check proposer credit
                proposer_info = user_db.check_proposer_by_uid(uid)
                if not proposer_info:
                    return False
                if proposer_info["credit"] < 80 and proposer_info["credit"] >= 60:
                    send_text_message(uid, "你的信用程度目前低於 80，低於 60 後將無法使用本服務！")
                elif proposer_info["credit"] < 60:
                    send_text_message(uid, "你的信用程度目前低於 60，無法使用本服務！")
                    return False
                # update the user to proposer state 2
                data = {
                    "name": result["data"]["name"],
                    "state": "proposer_state2",
                    "data": {
                        "name": "",
                        "description": "",
                        "number": 0,
                        "type": ""
                    }
                }
                user_db.create_user(uid, data, "proposer")
                # delete sender from unknow state
                user_db.delete_user(uid, "unknow")
            return text == self.action[0]
        return False

    def on_enter_proposer_state1(self, event):
        print("On proposer state 1")
        sender_id = event["sender"]["id"]
        send_text_message(sender_id, "請輸入你的個人頁面 link")

    def is_proposer_link(self, event):
        if event.get("message"):
            uid = event["sender"]["id"]
            text = event["message"]["text"]
            if text == os.environ.get("EMPTY_STRING"):
                return False
            # check url link works
            res = requests.get(text)
            if res.status_code != 200:
                return False
            # get sender from unknow state
            result = user_db.check_user(uid)
            # get proposer credit
            proposer_info = user_db.check_proposer_by_uid(uid)
            # update the user to proposer state 2
            data = {
                "name": result["data"]["name"],
                "state": "proposer_state2",
                "data": {
                    "name": "",
                    "description": "",
                    "number": 0,
                    "type": ""
                }
            }
            user_db.update_user(uid, data, "proposer")
            # update proposer info
            proposer_info["link"] = text
            user_db.update_proposer(uid, proposer_info)
            return True
        return False

    def on_enter_proposer_state2(self, event):
        print("On proposer state 2")
        sender_id = event["sender"]["id"]
        send_text_message(sender_id, "請輸入要拿來交換的物品")

    
    def is_proposer_item_name(self, event):
        if event.get("message"):
            text = event["message"]["text"]
            uid = event["sender"]["id"]
            if text == os.environ.get("EMPTY_STRING"):
                return False
            # get sender from current state
            result = user_db.check_user(uid)
            # update the user to proposer state 3
            result["data"]["data"]["name"] = text
            data = {
                "name": result["data"]["name"],
                "state": "proposer_state3",
                "data": result["data"]["data"]
            }
            user_db.update_user(uid, data, "proposer")
            return True
        return False
    
    def on_enter_proposer_state3(self, event):
        print("On proposer state 3")
        sender_id = event["sender"]["id"]
        replies = []
        for target in self.type_list:
            replies.append({
                    "content_type": "text",
                    "title": target,
                    "payload": target
                })
        send_quick_reply_message(sender_id, "請選擇你物品的類別", replies)
    
    def is_proposer_item_type(self, event):
        if event.get("message"):
            text = event["message"]["text"]
            uid = event["sender"]["id"]
            if text == os.environ.get("EMPTY_STRING"):
                return False
            if self.is_not_type_choose(event):
                return False
            # get sender from current state
            result = user_db.check_user(uid)
            # update the user to proposer state 4
            result["data"]["data"]["type"] = text
            data = {
                "name": result["data"]["name"],
                "state": "proposer_state4",
                "data": result["data"]["data"]
            }
            user_db.update_user(uid, data, "proposer")
            return True
        return False

        
    def on_enter_proposer_state4(self, event):
        print("On proposer state 4")
        sender_id = event["sender"]["id"]
        send_text_message(sender_id, "請輸入物品的數量")

    def is_proposer_item_number(self, event):
        if event.get("message"):
            text = event["message"]["text"]
            uid = event["sender"]["id"]
            if text == os.environ.get("EMPTY_STRING"):
                return False
            if self.is_not_digit(event):
                return False
            # get sender from unknow state
            result = user_db.check_user(uid)
            # update the user to proposer state 5
            result["data"]["data"]["number"] = text
            data = {
                "name": result["data"]["name"],
                "state": "proposer_state5",
                "data": result["data"]["data"]
            }
            user_db.update_user(uid, data, "proposer")
            return True
        return False

    def on_enter_proposer_state5(self, event):
        print("On proposer state 5")
        sender_id = event["sender"]["id"]
        send_text_message(sender_id, "請描述你的物品")

    def is_proposer_item_description(self, event):
        if event.get("message"):
            text = event["message"]["text"]
            uid = event["sender"]["id"]
            if text == os.environ.get("EMPTY_STRING"):
                return False
            # get sender from database
            result = user_db.check_user(uid)
            # update the user to proposer state 6
            result["data"]["data"]["description"] = text
            data = {
                "name": result["data"]["name"],
                "state": "proposer_state6",
                "data": result["data"]["data"]
            }
            user_db.update_user(uid, data, "proposer")
            return True
        return False

    def on_enter_proposer_state6(self, event):
        print("On proposer state 6")
        sender_id = event["sender"]["id"]
        send_text_message(sender_id, "請上傳一張交換物的照片")

    def is_proposer_item_image(self, event):
        if event.get("message") and event["message"].get("attachments"):
            print(event["message"]["attachments"])
            uid = event["sender"]["id"]
            if self.is_empty_image(event):
                return False
            # get sender from database
            result = user_db.check_user(uid)
            all_image = []
            for target in event["message"]["attachments"]:
                all_image.append(target["payload"]["url"])
            result["data"]["data"]["image_url"] = all_image
            data = {
                "name": result["data"]["name"],
                "state": "unknow",
                "data": result["data"]["data"]
            }
            user_db.update_user(uid, data, "proposer")
            return True
        return False
            

    ##################################################
    # Checker
    ##################################################
    
    def is_checker(self, event):
        if event.get("message"):
            text = event["message"]["text"]
            uid = event["sender"]["id"]
            if text == self.action[1]:
                # get sender from unknow state
                result = user_db.check_user(uid)
                print(result)
                # update the user to checker state 1
                data = {
                    "name": result["data"]["name"],
                    "state": "checker_state1",
                    "data": {}
                }
                user_db.create_user(uid, data, "checker")
                # delete sender from unknow state
                user_db.delete_user(uid, "unknow")
            return text == self.action[1]
        return False

    def on_enter_checker_state1(self, event):
        print("On checker state 1")
        sender_id = event["sender"]["id"]
        replies = []
        for target in self.type_list:
            replies.append({
                    "content_type": "text",
                    "title": target,
                    "payload": target
                })
        send_quick_reply_message(sender_id, "請選擇你感興趣的物品類別", replies)

    def is_checker_item_type(self, event):
        if event.get("message"):
            text = event["message"]["text"]
            uid = event["sender"]["id"]
            if text == os.environ.get("EMPTY_STRING"):
                return False
            if self.is_not_type_choose(event):
                return False
            # get sender from current state
            result = user_db.check_user(uid)
            # get all type and filter out top five according to timestamp
            items = item_db.read_item_by_type_all(text)
            print(items)
            if items: 
                items = sorted(items, key=lambda x: time.strptime(x["timestamp"], '%Y-%m-%d %H:%M:%S.%f'), reverse=True)
                items = items[:5]
            # update the user to checker state 2
            data = {
                "name": result["data"]["name"],
                "state": "checker_state2",
                "data": {
                    "type": text,
                    "items": items
                }
            }
            user_db.update_user(uid, data, "checker")
            return True
        return False

    def on_enter_checker_state2(self, event):
        print("On checker state2")
        sender_id = event["sender"]["id"]
        # get sender from current state
        result = user_db.check_user(sender_id)
        if 'items' in result['data']['data']:
            items = result["data"]["data"]["items"]
            send_text_message(sender_id, "最新的訊息如下")
            for index, value in enumerate(items):
                send_text_message(sender_id, "▍編號 {} \n▍名稱：{} \n▍數量：{} \n▍描述：\n    {}".format(index + 1, value["name"], value["number"], value["description"]))
                for url in value["image_url"]:
                    send_image_message(sender_id, url)
            replies = []
            for index, value in enumerate(items):
                replies.append({
                        "content_type": "text",
                        "title": index + 1,
                        "payload": index + 1
                    })
            send_quick_reply_message(sender_id, "請選擇編號(編號後的數字)以獲取交換者的資訊", replies)
        else:
            send_text_message(sender_id, "目前沒有任何新資訊！")
            # go to next state
            self.advance(event)



    def is_checker_item_number(self, event):
        if event.get("message"):
            text = event["message"]["text"]
            sender_id = event["sender"]["id"]
            if text == os.environ.get("EMPTY_STRING"):
                return False
            # get sender from current state
            result = user_db.check_user(sender_id)
            if 'items' in result['data']['data']:
                # get sender current items
                items = result["data"]["data"]["items"]
                if not text.isdigit():
                    return False
                if int(text) > len(items) or int(text) < 1:
                    return False
                print("get exchanger info")
                exchanger = user_db.check_proposer_by_uid(items[int(text) - 1]["proposer"])
                send_text_message(sender_id, "交換者資訊如下")
                send_text_message(sender_id, "▍姓名：{}\n▍信用程度 {}\n▍個人頁面 link\n{}".format(exchanger["name"], exchanger["credit"], exchanger["link"]))
                return True
        return False

    def is_blocker(self, event):
        if event.get("message"):
            text = event["message"]["text"]
            return text == self.action[2]
        return False

    def on_enter_blocker_state1(self, event):
        print("On blocker state 1")
        sender_id = event["sender"]["id"]
        response = send_text_message(sender_id, "請輸入交換者的個人頁面 link")

    def is_blocked_info(self, event):
        if event.get("message"):
            text = event["message"]["text"]
            uid = event["sender"]["id"]
            # check url link works
            res = requests.get(text)
            if res.status_code != 200:
                return False
            # get proposer info
            proposer_info = user_db.check_proposer_by_link(text)
            if proposer_info:
                proposer_info["data"]["credit"] = int(proposer_info["data"]["credit"]) - 5
                # decrese proposer credit
                user_db.update_proposer(proposer_info["uid"], proposer_info["data"])
                send_text_message(uid, "檢舉成功！")
            else:
                send_text_message(uid, "該使用者不存在！")
            return True

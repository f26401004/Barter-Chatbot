import flask
import json
import os
import users as user_db
from fsm import TocMachine

app = flask.Flask(__name__)
# define machine
machine = TocMachine(
    states=[
        'initial',
        'unknow',
        'proposer_state1',
        'proposer_state2',
        'proposer_state3',
        'proposer_state4',
        'proposer_state5',
        'proposer_state6',
        "checker_state1",
        "checker_state2",
        "blocker_state1"
    ],
    transitions=[
        {
            'trigger': 'advance',
            'source': 'initial',
            'dest': 'unknow'
        },
        {
            'trigger': 'advance',
            'source': 'unknow',
            'dest': 'unknow',
            'conditions': 'is_unknow'
        },
        {
            'trigger': 'advance',
            'source': 'proposer_state1',
            'dest': 'proposer_state1',
            'conditions': 'is_empty_string'
        },
        {
            'trigger': 'advance',
            'source': 'unknow',
            'dest': 'proposer_state1',
            'conditions': 'is_proposer_no_info'
        },
        {
            'trigger': 'advance',
            'source': 'proposer_state2',
            'dest': 'proposer_state2',
            'conditions': 'is_empty_string'
        },
        {
            'trigger': 'advance',
            'source': 'unknow',
            'dest': 'proposer_state2',
            'conditions': 'is_proposer_with_info'
        },
        {
            'trigger': 'advance',
            'source': 'proposer_state1',
            'dest': 'proposer_state2',
            'conditions': 'is_proposer_link'
        },
        {
            'trigger': 'advance',
            'source': 'proposer_state3',
            'dest': 'proposer_state3',
            'conditions': 'is_empty_string'
        },
        {
            'trigger': 'advance',
            'source': 'proposer_state3',
            'dest': 'proposer_state3',
            'conditions': 'is_not_type_choose'
        },
        {
            'trigger': 'advance',
            'source': 'proposer_state2',
            'dest': 'proposer_state3',
            'conditions': 'is_proposer_item_name'
        },
        {
            'trigger': 'advance',
            'source': 'proposer_state4',
            'dest': 'proposer_state4',
            'conditions': 'is_empty_string'
        },
        {
            'trigger': 'advance',
            'source': 'proposer_state4',
            'dest': 'proposer_state4',
            'conditions': 'is_not_digit'
        },
        {
            'trigger': 'advance',
            'source': 'proposer_state3',
            'dest': 'proposer_state4',
            'conditions': 'is_proposer_item_type'
        },
        {
            'trigger': 'advance',
            'source': 'proposer_state5',
            'dest': 'proposer_state5',
            'conditions': 'is_empty_string'
        },
        {
            "trigger": "advance",
            "source": "proposer_state4",
            "dest": "proposer_state5",
            "conditions": "is_proposer_item_number"
        },
        {
            "trigger": "advance",
            "source": "proposer_state5",
            "dest": "proposer_state6",
            "conditions": "is_proposer_item_description"
        },
        {
            'trigger': 'advance',
            'source': 'proposer_state6',
            'dest': 'proposer_state6',
            'conditions': 'is_empty_image'
        },
        {
            "trigger": "advance",
            "source": "proposer_state6",
            "dest": "unknow",
            "conditions": "is_proposer_item_image"
        },
        {
            'trigger': 'advance',
            'source': 'checker_state1',
            'dest': 'checker_state1',
            'conditions': 'is_empty_string'
        }, 
        {
            "trigger": 'advance',
            "source": "checker_state1",
            "dest": "checker_state1",
            "conditions": 'is_not_type_choose'
        },
        {
            "trigger": "advance",
            "source": "unknow",
            "dest": "checker_state1",
            "conditions": "is_checker"
        },
        {
            "trigger": "advance",
            "source": "checker_state2",
            "dest": "checker_state2",
            "conditions": "is_number_not_in_item_range"
        },
        {
            "trigger": "advance",
            "source": "checker_state1",
            "dest": "checker_state2",
            "conditions": "is_checker_item_type"
        },
       {
            "trigger": "advance",
            "source": "checker_state2",
            "dest": "unknow",
            "conditions": "is_checker_item_number"
        },
        {
            "trigger": "advance",
            "source": "unknow",
            "dest": "blocker_state1",
            "conditions": "is_blocker"
        },
        {
            'trigger': 'advance',
            'source': 'blocker_state1',
            'dest': 'blocker_state1',
            'unless': 'is_empty_string'
        },
        {
            "trigger": "advance",
            "source": "blocker_state1",
            "dest": "unknow",
            "conditions": "is_blocked_info"
        }
    ],
    initial="initial",
    auto_transitions=False,
    show_conditions=True
)


@app.route("/webhook", methods=["GET"])
def setup_webhook(path=""):
    VERIFY_TOKEN = "f6481601-ae65-4c60-b6d3-d51ef284a896"
    mode = flask.request.args.get("hub.mode")
    token = flask.request.args.get("hub.verify_token")
    challenge = flask.request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("WEBHOOK_VERIFIED")
        return challenge
    else:
        return

@app.route("/webhook", methods=["POST"])
def webhook_handler(path=""):
    message_entries = json.loads(flask.request.data.decode('utf8'))['entry']
    for entry in message_entries:
        messagings = entry["messaging"]
        for message in messagings:
            sender_uid = message["sender"]["id"]
            if message.get('message') and message['message'].get('text'):
                text = message['message']['text']
                print("{} says {}".format(sender_uid, text))
                # check current user state
                result = user_db.check_user(sender_uid)
                print(machine.state)
                if result["role"] != "unknow" and result["role"]:
                    machine.state = result["data"]["state"]
                elif result["role"] == "unknow":
                    machine.state = "unknow"
                machine.advance(message)
            else:
                message['message']['text'] = os.environ.get("EMPTY_STRING")
                machine.advance(message)
        
    return "OK"

@app.route('/show-fsm', methods=["GET"])
def show_fsm(path=""):
    machine.get_graph().draw('fsm.png', prog="dot", format="png")
    return flask.send_file('./fsm.png', mimetype="image/png")

app.run(debug=True)

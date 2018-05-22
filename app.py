import random
import requests
import core_engine
from core_engine import Members
from flask import Flask, request

 
app = Flask(__name__)
ACCESS_TOKEN = 'EAAFRHrTy7U0BAJWebipgZAUCCMPggc8aV5RldgjpPZCD1IZACIwAmvkPfkYMQy8ZASAXkaIaJEi7H7f5eEddYUC4ovdw3vlaY9UzAuBZAZBHr7mhKImfcu6smyrZBfuXUP8aQA7ZB0VoH9mfL0qJCXaVUX0KmC5LesJ7aPVDP1ABVAZDZD'
VERIFY_TOKEN = 'EROS_TOKEN'
#bot = Bot(ACCESS_TOKEN)

payload = {}

#We will receive messages that Facebook sends our bot at this endpoint 
@app.route("/webhook", methods=['GET', 'POST'])
def receive_message():
    if request.method == 'GET':
        """Before allowing people to message your bot, Facebook has implemented a verify token
        that confirms all requests that your bot receives came from Facebook.""" 
        token_sent = request.args.get("hub.verify_token")
        return verify_fb_token(token_sent)
    #if the request was not get, it must be POST and we can just proceed with sending a message back to user
    else:
        # get whatever message a user sent the bot
       output = request.get_json()
       print (output)
       placeHolderFbId='16093421424752501'
       member_ref=core_engine.Members(placeHolderFbId)
       member = member_ref.get_member()
       #print(member.get().to_dict().get('fb_id'))
       conversation = member_ref.get_active_conversation(member)
       for event in output['entry']:
          messaging = event['messaging']
          for message in messaging:
            sender_id = message['sender']['id']
            if message.get('message'):
                #Facebook Messenger ID for user so we know where to send response back to
                reciever_id = 1609342142475258
                #core_engine.verify_member_state(sender_id)
                sender_msg = message['message'].get('text')
                if not conversation:
                    # Prompt member if he needs help of wants to do something sele
                    quick_reply_response = message['message'].get('quick_reply')
                    #member=core_engine.Members(placeHolderFbId).get_member()
                    if quick_reply_response:
                        print(quick_reply_response['payload'])
                        sender_msg = 'User has choosen the category. Inside conversation'
                        payload = form_payload('plain_message',sender_msg,reciever_id)
                    else :
                        payload = form_payload('welcome_buttons',sender_msg,reciever_id)
                    # This means that either this is the first time member is interacting with the platform.
                else:
                    #Log the conversation. Get the other party id and send it to them.
                    payload = form_payload('plain_message',sender_msg,reciever_id)
                    print(conversation.to_dict()['helper_ref'].get().to_dict()['fb_id'])
                #print(payload)
            elif message.get('postback'):
                #These are responses to the button
                user_response = message['postback'].get('payload')
                sender_msg = message['postback'].get('title')
                if user_response == 'seekingAdvice':
                    print("Member is seeking help now...")
                    sender_msg='What are you shopping for?'
                    payload = form_payload('shopping_category_quick_replies',sender_msg,sender_id)
                elif user_response =='other':
                    print("Member wants to do something else, present other options")
                    payload = form_payload('other_buttons',sender_msg,sender_id)
                elif user_response =='expertRegsteration':
                    print("Member wants to register as expert")
                    sender_msg = 'Please visit http://concier.org to register as expert'
                    payload = form_payload('plain_message',sender_msg,sender_id)
                elif user_response =='faq':
                    print("Member wants to see FAQ")
                    payload = form_payload('plain_message',sender_msg,sender_id)
                elif user_response =='electronics' or user_response =='computers' or user_response =='house_hold_items'or user_response =='other_items':
                    print("Member choosen category")
                    sender_msg = 'I can connect you to {} expert. Before that, can you tell me exactly what you are looking for?'.format(sender_msg)
                    payload = form_payload('plain_message',sender_msg,sender_id)
                    #conversation.add_conversation(member)
                else :
                    print("Some other option choosen")
                    sender_msg = 'User has selected: '+sender_msg
                    payload = form_payload('plain_message',sender_msg,sender_id)
            send_message(payload)
    return "Message Processed"
 
def verify_fb_token(token_sent):
    #take token sent by facebook and verify it matches the verify token you sent
    #if they match, allow the request, else return an error 
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'

def send_message(payload):
    #sends user the text message provided via input response parameter
    #bot.send_text_message(recipient_id, response)
    auth = {
    'access_token':ACCESS_TOKEN
    }
    request_endpoint = 'https://graph.facebook.com/v2.6/me/messages'
    response = requests.post(
        request_endpoint,
        params=auth,
        json=payload
        )
    result = response.json()
    return result

def form_payload(response_type,text_message,recipient_id):
    payload['recipient'] = {
        'id': recipient_id
        }
    if response_type =='plain_message':
        payload['notification_type'] = 'REGULAR'
        payload['message'] = {
        'text' : text_message
        }
    elif response_type =='welcome_buttons':
        #payload['notification_type'] = 'REGULAR'
        payload['message'] = {
            "attachment":{
                "type":"template",
                "payload":{
                    "template_type":"button",
                    "text":"Hey stranger! How can I help?",
                    "buttons":[
                    {
                    "type":"postback",
                    "title":"Get shopping advice?",
                    "payload":"seekingAdvice"
                    },
                    {
                    "type":"postback",
                    "title":"Other?",
                    "payload":"other"
                    }
                    ]
                }
            }
        }
    elif response_type =='other_buttons':
        payload['message'] = {
            "attachment":{
                "type":"template",
                "payload":{
                    "template_type":"button",
                    "text":"Other things you can do?",
                    "buttons":[
                    {
                    "type":"postback",
                    "title":"Register as expert?",
                    "payload":"expertRegsteration"
                    },
                    {
                    "type":"postback",
                    "title":"FAQ",
                    "payload":"faq"
                    }
                    ]
                }
            }
        }
    elif response_type =='shopping_category_buttons':
        payload['message'] = {
            "attachment":{
                "type":"template",
                "payload":{
                    "template_type":"button",
                    "text":text_message,
                    "buttons":[
                    {
                    "type":"postback",
                    "title":"Electronics",
                    "payload":"electronics"
                    },
                    {
                    "type":"postback",
                    "title":"Computers",
                    "payload":"computers"
                    },
                    {
                    "type":"postback",
                    "title":"Household Items",
                    "payload":"house_hold_items"
                    }
                    ]
                }
            }
        }
    elif response_type =='shopping_category_quick_replies':
        payload['message'] = {
        'text' : text_message,
        "quick_replies":[
            {
            "content_type":"text",
            "title":"Phone",
            "payload":"phone"
            },
            {
            "content_type":"text",
            "title":"Electronics",
            "payload":"electronics"
            },
            {
            "content_type":"text",
            "title":"Computers",
            "payload":"computers"
            },
            {
            "content_type":"text",
            "title":"Household Items",
            "payload":"house_hold_items"
            }
            ]
        }
    return payload

if __name__ == "__main__":
    app.run()
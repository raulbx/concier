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
       #print (output)
       placeHolderFbId='16093421424752501'
       for event in output['entry']:
          messaging = event['messaging']
          for message in messaging:
            sender_id = message['sender']['id']
            #placeHolderFbId=sender_id
            member_ref=core_engine.Members(sender_id)
            member = member_ref.get_member()
            #print(member.get().to_dict().get('fb_id'))
            #conversation = member_ref.get_active_conversation(member)
            conversation_ref = member_ref.get_active_conversation_ref(member)
            if message.get('message'):
                #Facebook Messenger ID for user so we know where to send response back to
                #reciever_id = 1609342142475258
                reciever_id=sender_id
                #core_engine.verify_member_state(sender_id)
                sender_msg = message['message'].get('text')
                if not conversation_ref:
                    # Prompt member if he needs help of wants to do something sele
                    quick_reply_response = message['message'].get('quick_reply')
                    #member=core_engine.Members(placeHolderFbId).get_member()
                    if quick_reply_response:
                        #print(quick_reply_response['payload'])
                        #sender_msg = 'User has choosen the category. Inside conversation'
                        sender_msg = 'I can connect you to {} expert. Please share what are you looking for?  More descriptive the better!'.format(sender_msg)
                        conversation_ref = member_ref.add_conversation(member)
                        payload = form_payload('plain_message',sender_msg,sender_id)
                    else :
                        payload = form_payload('welcome_buttons',sender_msg,sender_id)
                        # This means that this is the first time member is interacting with the platform.
                else:
                    #Log the conversation. Get the other party id and send it to them.
                    conversation = conversation_ref.get()
                    #quick_reply_response = message['message'].get('quick_reply')
                    payload_message = message['message']['quick_reply'].get('payload')
                    if conversation.to_dict().get('active'):
                        print("Send the message to the counter party")
                        sender_msg ="I am sending this message to counter party"
                        # Get the counter party from the conversation
                        counter_party = 'YP....'
                        payload = form_payload('plain_message',sender_msg,counter_party)
                    elif conversation.to_dict().get('conversation_state') == 'identify_timeframe':
                        # Ask user about his time frame for the purchase. Log the question. Move the conversation in Identify price state
                        conversation_ref.update({'conversation_state':'identify_price'})
                        conversation_ref.update({'question':sender_msg})
                        member_ref.log_message(member,conversation_ref,sender_msg)
                        sender_msg = "How soon do you want to buy this product?"
                        payload = form_payload('shopping_timeframe_quick_replies',sender_msg,sender_id)
                    elif conversation.to_dict().get('conversation_state') == 'identify_price':
                         # Ask user about price for his purchase. Log the timeframe. Move the conversation in find expert state
                        conversation_ref.update({'conversation_state':'find_expert'})
                        conversation_ref.update({'time_frame':payload_message})
                        member_ref.log_message(member,conversation_ref,sender_msg)
                        sender_msg = "What price range do you have in mind?"
                        payload = form_payload('shopping_price_quick_replies',sender_msg,sender_id)
                    elif conversation.to_dict().get('conversation_state') == 'find_expert':
                        # Reach this state after all the member question onboarding is complete.
                        member_ref.log_message(member,conversation_ref,sender_msg)
                        conversation_ref.update({'max_price':payload_message})
                        sender_msg = "Thanks. Let me find an expert, who can help you make a decision."
                        payload = form_payload('plain_message',sender_msg,sender_id)
                        #Broadcast this message, to the community of experts
                        # Get all the experts for this expertise 
                        query_results = member_ref.get_experts('electronics').get()
                        for result in query_results:
                            print(result.to_dict()['member'][0].get())
                            #for expert_ref in result.to_dict()['member']:
                             #   print ('Expert Reference is: '.format(expert_ref.get()))
                                #print('ID {} and {}'.format(result.id, result.to_dict()['member']))
                        #se
                    #print(conversation.to_dict()['helper_ref'].get().to_dict()['fb_id'])
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
                elif user_response =='manage_account':
                    print("Member wants to manage account")
                    payload = form_payload('plain_message',sender_msg,sender_id)
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
                    "text":"Hey there! How can I help?",
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
                    "title":"Register as expert",
                    "payload":"expertRegsteration"
                    },
                    {
                    "type":"postback",
                    "title":"Manage Account",
                    "payload":"manage_account"
                    },
                    {
                    "type":"postback",
                    "title":"Something else",
                    "payload":"something_else"
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
                    },
                    {
                    "type":"postback",
                    "title":"Other",
                    "payload":"Other_items"
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
    elif response_type =='shopping_timeframe_quick_replies':
        payload['message'] = {
        'text' : text_message,
        "quick_replies":[
            {
            "content_type":"text",
            "title":"Less than 24 hours",
            "payload":"24 hours"
            },
            {
            "content_type":"text",
            "title":"One week",
            "payload":"one week"
            },
            {
            "content_type":"text",
            "title":"One month",
            "payload":"one month"
            },
            {
            "content_type":"text",
            "title":"Don't have a timeframe",
            "payload":"no timeframe"
            }
            ]
        }
    elif response_type =='shopping_price_quick_replies':
        payload['message'] = {
        'text' : text_message,
        "quick_replies":[
            {
            "content_type":"text",
            "title":"Do not know",
            "payload":"no price in mind"
            },
            {
            "content_type":"text",
            "title":"Specify max amount",
            "payload":"max_price"
            }
            ]
        }
    return payload

if __name__ == "__main__":
    app.run()
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
       for event in output['entry']:
          messaging = event['messaging']
          for message in messaging:
            if message.get('message'):
                #Facebook Messenger ID for user so we know where to send response back to
                sender_id = message['sender']['id']
                reciever_id = 1609342142475258
                placeHolderFbId='16093421424752505'
                #core_engine.verify_member_state(sender_id)
                sender_msg = message['message'].get('text')
                #member=core_engine.Members(placeHolderFbId).get_member()
                member_obj=core_engine.Members(placeHolderFbId)
                member = member_obj.get_member()
                #print(member.get().to_dict().get('fb_id'))
                conversation = member_obj.get_active_conversation(member)
                if not conversation: 
                    print("No conversations")
                    # Prompt if help needed or else

                    # This means that either this is the first time member is interacting with the 
                else:
                    #Log the conversation. Get the other party id and send it to them.
                    print(conversation.to_dict()['helper_ref'].get().to_dict()['fb_id'])

                #sender_msg = active_count
                '''
                Member found or added. Check the converstation. If there is no conversation, then this person is either an expert signing up or a new person needing help.
                Ask them if they need help? If yes, then mark them as helpee, and start the conversation thread. 
                After initial conversation, broadcast the message to all the helpers. The first helper to aggree to will be paired with the helpee. Continue the conversation, and continue using the coins.
                '''
                
                if message['message'].get('text'):
                   # response_sent_text = core_engine.fbrespond(sender_id, message['message'].get('seq'))
                    # Tony ID: 1720043658018350
                    # Rahul's ID: 1609342142475258
                    # This is where the concier Engine fits in
                    # Below method should be able to broadcast message as well. 
                    send_message(reciever_id, sender_msg)
                #if user sends us a GIF, photo,video, or any other non-text item
                if message['message'].get('attachments'):
                    response_sent_nontext = get_message()
                    send_message(recipient_id, response_sent_nontext)
    return "Message Processed"
 
def verify_fb_token(token_sent):
    #take token sent by facebook and verify it matches the verify token you sent
    #if they match, allow the request, else return an error 
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'

def send_message(recipient_id, response):
    #sends user the text message provided via input response parameter
    #bot.send_text_message(recipient_id, response)
    auth = {
    'access_token':ACCESS_TOKEN
    }
    payload['recipient'] = {
    'id': recipient_id
    }
    payload['notification_type'] = 'REGULAR'
    payload['message'] = {
    'text' : response,
    'quick_replies':[
    {'content_type':'text',
    'title':'Need Help?',
    'payload':'helpee'}
    ]
    }
    request_endpoint = 'https://graph.facebook.com/v2.6/me/messages'
    response = requests.post(
        request_endpoint,
        params=auth,
        json=payload
        )
    result = response.json()
    return result

if __name__ == "__main__":
    app.run()
payload = {}

def fb_payload(response_type,response,recipient_id,conversation_id):
	payload['recipient'] = {
	'id': recipient_id
	}
	if response_type =='plain_message':
		payload['notification_type'] = 'REGULAR'
		payload['message'] = {
		'text' : response
		}
	elif response_type =='welcome_user':
		payload['message'] = {
            "attachment":{
                "type":"template",
                "payload":{
                    "template_type":"button",
                    "text":response,
                    "buttons":[
                    {
                    "type":"postback",
                    "title":"Get shopping advice?",
                    "payload":"seekingAdvice:"+conversation_id
                    },
                    {
                    "type":"postback",
                    "title":"Other?",
                    "payload":"other:"+conversation_id
                    }
                    ]
                }
            }
        }
	return payload
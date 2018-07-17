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
    elif response_type =='shopping_category_quick_replies':
        payload['message'] = {
            'text' : text_message,
            "quick_replies":[{
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
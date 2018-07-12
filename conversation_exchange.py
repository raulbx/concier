import core_engine

class Exchange(object):

	def __init__(self, member_identifier, source):
		self.member_identifier = member_identifier
		self.source = source

	def get_action(self):
		print("Member Identifier is {}".format(self.member_identifier))
		sender_msg = "This is new"
		return form_payload('plain_message',sender_msg,self.member_identifier,conversation_id)

	def start_conversation(self):
		print("Starting Conversation")

	def form_payload(response_type,text_message,recipient_id,conversation_id):
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
    elif response_type =='choose_expertise_category':
        #payload['notification_type'] = 'REGULAR'
        payload['message'] = {
            "attachment":{
                "type":"template",
                "payload":{
                    "template_type":"button",
                    "text":"What kind of products you know well?",
                    "buttons":[
                    {
                    "type":"postback",
                    "title":"Phone",
                    "payload":"phone"
                    },
                    {
                    "type":"postback",
                    "title":"Electronics",
                    "payload":"electronics"
                    },
                    {
                    "type":"postback",
                    "title":"Computers",
                    "payload":"computers"
                    }
                    ]
                }
            }
        }
    elif response_type =='broadcast_to_experts':
        #payload['notification_type'] = 'REGULAR'
        payload['message'] = {
            "attachment":{
                "type":"template",
                "payload":{
                    "template_type":"button",
                    "text":text_message,
                    "buttons":[
                    {
                    "type":"postback",
                    "title":"YES",
                    "payload":"acceptAssignment:"+conversation_id
                    },
                    {
                    "type":"postback",
                    "title":"NO",
                    "payload":"declineAssignment:"+conversation_id
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
                    "title":"Household Item",
                    "payload":"house hold item"
                    },
                    {
                    "type":"postback",
                    "title":"Other",
                    "payload":"other item"
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
            "title":"Max $1000",
            "payload":"$1000"
            },
            {
            "content_type":"text",
            "title":"Max $500",
            "payload":"$500"
            },
            {
            "content_type":"text",
            "title":"Max $100",
            "payload":"$100"
            },
            {
            "content_type":"text",
            "title":"Price doesn't matter",
            "payload":"Price doesn't matter"
            }
            ]
        }
    return payload
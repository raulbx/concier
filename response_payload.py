payload = {}

def fb_payload(conversation_state,response,recipient_id,conversation_id,next_state):
    payload['recipient'] = {
    'id': recipient_id
    }
    if conversation_state =='default_message':
        payload['notification_type'] = 'REGULAR'
        payload['message'] = {
        'text' : response,
        'metadata':next_state
        }
    elif conversation_state =='welcome_user':
        payload['message'] = {
        "metadata":"ask_product_category",
            "attachment":{
                "type":"template",
                "payload":{
                    "template_type":"button",
                    "text":'How can I help you?',
                    "buttons":[
                    {
                    "type":"postback",
                    "title":"Get shopping advice?",
                    "payload":"ask_product_category:"+conversation_id
                    },
                    {
                    "type":"postback",
                    "title":"Other?",
                    "payload":"welcomeOtherOption:"+conversation_id
                    }
                    ]
                }
            }
        }
    elif conversation_state =='ask_product_category':
        payload['message'] = {
        'text' : 'What are you shopping for?',
        "metadata":"record_category_understand_need",
        "quick_replies":[
            {
            "content_type":"text",
            "title":"Phone",
            "payload":"record_category_understand_need:"+conversation_id
            },
            {
            "content_type":"text",
            "title":"Electronics",
            "payload":"record_category_understand_need:"+conversation_id
            },
            {
            "content_type":"text",
            "title":"Computers",
            "payload":"record_category_understand_need:"+conversation_id
            },
            {
            "content_type":"text",
            "title":"Household Items",
            "payload":"record_category_understand_need:"+conversation_id
            }
            ]
        }
    elif conversation_state == 'record_category_understand_need':
        payload['notification_type'] = 'REGULAR'
        payload['message'] = {
        'text' : 'I can connect you to an expert, who is knows about $arg1. Please share what are you looking for?  More descriptive the better!',
        'metadata':'record_need_ask_time_frame'
        }
    elif conversation_state =='record_need_ask_time_frame':
        payload['message'] = {
        'text' : 'How soon do you want to buy this product?',
        "metadata":"record_time_frame_ask_price",
        "quick_replies":[
            {
            "content_type":"text",
            "title":"Less than 24 hours",
            "payload":"record_time_frame_ask_price:"+conversation_id
            },
            {
            "content_type":"text",
            "title":"One week",
            "payload":"record_time_frame_ask_price:"+conversation_id
            },
            {
            "content_type":"text",
            "title":"One month",
            "payload":"record_time_frame_ask_price:"+conversation_id
            },
            {
            "content_type":"text",
            "title":"Don't have a timeframe",
            "payload":"record_time_frame_ask_price:"+conversation_id
            }
            ]
        }
    elif conversation_state =='record_time_frame_ask_price':
        payload['message'] = {
        'text' : 'What price range do you have in mind?',
         "metadata":"record_price_thank_user",
        "quick_replies":[
            {
            "content_type":"text",
            "title":"Do not know",
            "payload":"record_price_thank_user:"+conversation_id
            },
            {
            "content_type":"text",
            "title":"$1000 Max",
            "payload":"record_price_thank_user:"+conversation_id
            },
            {
            "content_type":"text",
            "title":"$500 Max",
            "payload":"record_price_thank_user:"+conversation_id
            },
            {
            "content_type":"text",
            "title":"$100 Max",
            "payload":"record_price_thank_user:"+conversation_id
            },
            {
            "content_type":"text",
            "title":"Price doesn't matter",
            "payload":"record_price_thank_user:"+conversation_id
            }
            ]
        }
    elif conversation_state == 'record_price_thank_user':
        payload['notification_type'] = 'REGULAR'
        payload['message'] = {
        'text' : 'Thanks. Let me find an expert, who can help you make a decision.',
        'metadata':''
        }
    elif conversation_state =='other_buttons':
        payload['message'] = {
            "attachment":{
                "type":"template",
                "payload":{
                    "template_type":"button",
                    "text":response,
                    "buttons":[
                    {
                    "type":"postback",
                    "title":"Register as expert",
                    "payload":"registerExpert:"+conversation_id
                    },
                    {
                    "type":"postback",
                    "title":"Manage Account",
                    "payload":"manageAccount:"+conversation_id
                    },
                    {
                    "type":"postback",
                    "title":"Something else",
                    "payload":"somethingElse:"+conversation_id
                    }
                    ]
                }
            }
        }
    elif conversation_state =='choose_expertise_category':
        #payload['notification_type'] = 'REGULAR'
        payload['message'] = {
            "attachment":{
                "type":"template",
                "payload":{
                    "template_type":"button",
                    "text":response,
                    "buttons":[
                    {
                    "type":"postback",
                    "title":"Phone",
                    "payload":"confirmExpert:"+conversation_id
                    },
                    {
                    "type":"postback",
                    "title":"Electronics",
                    "payload":"confirmExpert:"+conversation_id
                    },
                    {
                    "type":"postback",
                    "title":"Computers",
                    "payload":"confirmExpert:"+conversation_id
                    }
                    ]
                }
            }
        }
    return payload
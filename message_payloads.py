payload = {}

def fb_payload(response_payload,response,recipient_id,conversation_id):
    payload['recipient'] = {
    'id': recipient_id
    }
    if response_payload =='plain_message':
        payload['notification_type'] = 'REGULAR'
        payload['message'] = {
        'text' : response
        }
    elif response_payload =='welcome_user':
        payload['message'] = {
        "metadata":"ask_product_category",
            "attachment":{
                "type":"template",
                "payload":{
                    "template_type":"button",
                    "text":response,
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
    elif response_payload =='shopping_category_quick_replies':
        payload['message'] = {
        'text' : response,
        "metadata":"record_category_understand_need",
        "quick_replies":[
            {
            "content_type":"text",
            "title":"Phone",
            "payload":"record_category_ask_time_frame:"+conversation_id
            },
            {
            "content_type":"text",
            "title":"Electronics",
            "payload":"record_category_ask_time_frame:"+conversation_id
            },
            {
            "content_type":"text",
            "title":"Computers",
            "payload":"record_category_ask_time_frame:"+conversation_id
            },
            {
            "content_type":"text",
            "title":"Household Items",
            "payload":"record_category_ask_time_frame:"+conversation_id
            }
            ]
        }
    elif response_payload =='shopping_timeframe_quick_replies':
        payload['message'] = {
        'text' : response,
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
    elif response_payload =='shopping_price_quick_replies':
        payload['message'] = {
        'text' : response,
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
    elif response_payload =='other_buttons':
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
    elif response_payload =='choose_expertise_category':
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
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
        "quick_replies":[
            {
            "content_type":"text",
            "title":"Phone",
            "payload":"categoryKnown:"+conversation_id
            },
            {
            "content_type":"text",
            "title":"Electronics",
            "payload":"categoryKnown:"+conversation_id
            },
            {
            "content_type":"text",
            "title":"Computers",
            "payload":"categoryKnown:"+conversation_id
            },
            {
            "content_type":"text",
            "title":"Household Items",
            "payload":"categoryKnown:"+conversation_id
            }
            ]
        }
    elif response_payload =='shopping_timeframe_quick_replies':
        payload['message'] = {
        'text' : response,
        "quick_replies":[
            {
            "content_type":"text",
            "title":"Less than 24 hours",
            "payload":"timeframeKnown:"+conversation_id
            },
            {
            "content_type":"text",
            "title":"One week",
            "payload":"timeframeKnown:"+conversation_id
            },
            {
            "content_type":"text",
            "title":"One month",
            "payload":"timeframeKnown:"+conversation_id
            },
            {
            "content_type":"text",
            "title":"Don't have a timeframe",
            "payload":"timeframeKnown:"+conversation_id
            }
            ]
        }
    elif response_payload =='shopping_price_quick_replies':
        payload['message'] = {
        'text' : response,
        "quick_replies":[
            {
            "content_type":"text",
            "title":"Do not know",
            "payload":"priceKnown:"+conversation_id
            },
            {
            "content_type":"text",
            "title":"$1000 Max",
            "payload":"priceKnown:"+conversation_id
            },
            {
            "content_type":"text",
            "title":"$500 Max",
            "payload":"priceKnown:"+conversation_id
            },
            {
            "content_type":"text",
            "title":"$100 Max",
            "payload":"priceKnown:"+conversation_id
            },
            {
            "content_type":"text",
            "title":"Price doesn't matter",
            "payload":"priceKnown:"+conversation_id
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
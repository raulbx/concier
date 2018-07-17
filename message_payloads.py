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
    elif response_type =='shopping_timeframe_quick_replies':
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
    elif response_type =='shopping_price_quick_replies':
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
            "title":"Max $1000",
            "payload":"priceKnown:"+conversation_id
            },
            {
            "content_type":"text",
            "title":"Max $500",
            "payload":"priceKnown:"+conversation_id
            },
            {
            "content_type":"text",
            "title":"Max $100",
            "payload":"priceKnown:"+conversation_id
            },
            {
            "content_type":"text",
            "title":"Price doesn't matter",
            "payload":"priceKnown:"+conversation_id
            }
            ]
        }
    return payload
payload = {}

def fb_payload(conversation_state,response,recipient_id,conversation_id):
    payload['recipient'] = {
    'id': recipient_id
    }
    if conversation_state =='default_state':
        payload['notification_type'] = 'REGULAR'
        payload['message'] = {
        'text' : response
        }
    elif conversation_state =='welcome_user':
        payload['message'] = {
        "metadata":"ask_product_category",
            "attachment":{
                "type":"template",
                "payload":{
                    "template_type":"button",
                    "text":'Hi I am Dave. Your personal shopping Concier. How can I help you?',
                    "buttons":[
                    {
                    "type":"postback",
                    "title":"Get shopping advice?",
                    "payload":"ask_product_category:"+conversation_id
                    },
                    {
                    "type":"postback",
                    "title":"Other?",
                    "payload":"other_buttons:"+conversation_id
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
        'text' : 'I can connect you to $arg1 expert. Please share what are you looking for?  More description the better!',
        'metadata':'record_need_ask_time_frame'
        }
        payload['platform'] = {
        'action':'record_category_set_future_state',
        'future_state':'record_need_ask_time_frame'
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
        payload['platform'] = {
        'action':'record_need'
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
        payload['platform'] = {
        'action':'record_time_frame'
        }
    elif conversation_state == 'record_price_thank_user':
        payload['notification_type'] = 'REGULAR'
        payload['message'] = {
        'text' : 'Thanks. Let me find an expert, who can help you make a decision.'
        }
        payload['platform'] = {
        'action':'record_price_and_broadcast_request',
        'future_state':'onboard_complete_waiting_for_expert'
        }
    elif conversation_state == 'onboard_complete_waiting_for_expert':
        payload['notification_type'] = 'REGULAR'
        payload['message'] = {
        'text' : 'Our expert search is on. We will be back soon with an expert to help you out.'
        }
        payload['platform'] = {
        'action':'set_future_state',
        'future_state':'onboard_complete_user_followed_up_once'
        }
    elif conversation_state == 'onboard_complete_user_followed_up_once':
        payload['notification_type'] = 'REGULAR'
        payload['message'] = {
        'text' : 'We are better than this. We are still looking. We will be back soon with an expert to help you out.'
        }
        payload['platform'] = {
        'action':'set_future_state',
        'future_state':'onboard_complete_user_followed_up_twice'
        }
    elif conversation_state =='other_buttons':
        payload['message'] = {
            "attachment":{
                "type":"template",
                "payload":{
                    "template_type":"button",
                    "text":'Other things you can do?',
                    "buttons":[
                    {
                    "type":"postback",
                    "title":"Register as expert",
                    "payload":"choose_expertise_category:"+conversation_id
                    },
                    {
                    "type":"postback",
                    "title":"Manage Account",
                    "payload":"manage_account:"+conversation_id
                    },
                    {
                    "type":"postback",
                    "title":"Something else",
                    "payload":"something_else:"+conversation_id
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
                    "text":'What kind of products you know well?',
                    "buttons":[
                    {
                    "type":"postback",
                    "title":"Phone",
                    "payload":"register_expert:"+conversation_id
                    },
                    {
                    "type":"postback",
                    "title":"Electronics",
                    "payload":"register_expert:"+conversation_id
                    },
                    {
                    "type":"postback",
                    "title":"Computers",
                    "payload":"register_expert:"+conversation_id
                    }
                    ]
                }
            }
        }
    elif conversation_state == 'register_expert':
        payload['notification_type'] = 'REGULAR'
        payload['message'] = {
        'text' : 'Great I have added you as an expert for $arg1.'
        }
        payload['platform'] = {
        'action':'add_expertise'
        }
    elif conversation_state == 'manage_account':
        payload['notification_type'] = 'REGULAR'
        payload['message'] = {
        'text' : 'Manage your account at http://concier.org/account'
        }
    elif conversation_state == 'something_else':
        payload['notification_type'] = 'REGULAR'
        payload['message'] = {
        'text' : 'Please type your message below. We will need to get our human to answer this.'
        }
    elif conversation_state =='broadcast_message':
        payload['message'] = {
            "attachment":{
                "type":"template",
                "payload":{
                    "template_type":"button",
                    "text":'We have a member, who is looking for an $arg1 item within $arg2. Members question is : $arg3. Do you want to help?',
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
    
    return payload
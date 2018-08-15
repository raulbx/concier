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
    if conversation_state =='conversation_initiated':
        payload['notification_type'] = 'REGULAR'
        payload['message'] = {
        'text' : 'Please choose an option above. For other queries leave a message and we will respond in few hours.'
        }
        payload['platform'] = {
        'action':'set_future_state',
        'future_state':'default_state'
        }
    elif conversation_state =='welcome_user':
        payload['message'] = {
        "metadata":"ask_product_category",
            "attachment":{
                "type":"template",
                "payload":{
                    "template_type":"button",
                    "text":'Hi '+ response+', I am your personal shopping Concier. How can I help you?',
                    "buttons":[
                    {
                    "type":"postback",
                    "title":"Get shopping help?",
                    "payload":"ask_product_category:"+conversation_id
                    },
                    {
                    "type":"postback",
                    "title":"Give shopping advise?",
                    "payload":"choose_expertise_category:"+conversation_id
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
        "quick_replies":[
            {
            "content_type":"text",
            "title":"Gadgets",
            "payload":"record_category_ask_specfic_product:"+conversation_id
            },
            {
            "content_type":"text",
            "title":"Computers",
            "payload":"record_category_ask_specfic_product:"+conversation_id
            },
            {
            "content_type":"text",
            "title":"Household Items",
            "payload":"record_category_ask_specfic_product:"+conversation_id
            },
            {
            "content_type":"text",
            "title":"Other",
            "payload":"record_category_ask_specfic_product:"+conversation_id
            }
            ]
        }
    elif conversation_state == 'record_category_ask_specfic_product':
        payload['notification_type'] = 'REGULAR'
        payload['message'] = {
        'text' : 'Which specific product under $arg1, are you shopping for?'
        }
        payload['platform'] = {
        'action':'record_value_set_future_state',
        'field':'product_category',
        'future_state':'record_specific_product_understand_need'
        }
    elif conversation_state == 'record_specific_product_understand_need':
        payload['notification_type'] = 'REGULAR'
        payload['message'] = {
        'text' : 'Can you describe why you need the product'
        }
        payload['platform'] = {
        'action':'record_value_set_future_state',
        'field':'specific_product',
        'future_state':'record_need_ask_time_frame'
        }
    elif conversation_state =='record_need_ask_time_frame':
        payload['message'] = {
        'text' : 'How soon do you want to buy this product?',
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
        'action':'record_value_set_future_state',
        'field':'user_need',
        'future_state':'record_time_frame_ask_price'
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
        'action':'record_value_set_future_state',
        'field':'time_frame',
        'future_state':'record_price_thank_user'
        }
    elif conversation_state == 'record_price_thank_user':
        payload['notification_type'] = 'REGULAR'
        payload['message'] = {
        'text' : 'Thanks. Let me find a community member, who can help you make a decision.'
        }
        payload['platform'] = {
        'action':'record_price_and_broadcast_request',
        'future_state':'onboard_complete_waiting_for_expert'
        }
    elif conversation_state == 'onboard_complete_waiting_for_expert':
        payload['notification_type'] = 'REGULAR'
        payload['message'] = {
        'text' : 'Our expert search is on. We will be back soon with an expert to help you.'
        }
        payload['platform'] = {
        'action':'set_future_state',
        'future_state':'onboard_complete_user_followed_up_once'
        }
    elif conversation_state == 'onboard_complete_user_followed_up_once':
        payload['notification_type'] = 'REGULAR'
        payload['message'] = {
        'text' : 'We are still looking. We will be back soon with an expert to help you out. We are usually better than this. '
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
                    "text":'You want to ',
                    "buttons":[
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
        payload['message'] = {
            "attachment":{
                "type":"template",
                "payload":{
                    "template_type":"button",
                    "text":'What kind of products you know well?',
                    "buttons":[
                    {
                    "type":"postback",
                    "title":"Gadgets",
                    "payload":"register_expert:"+conversation_id
                    },
                    {
                    "type":"postback",
                    "title":"Computers",
                    "payload":"register_expert:"+conversation_id
                    },
                    {
                    "type":"postback",
                    "title":"Household Items",
                    "payload":"register_expert:"+conversation_id
                    }
                    ]
                }
            }
        }
    elif conversation_state == 'register_expert':
        payload['notification_type'] = 'REGULAR'
        payload['message'] = {
        'text' : 'Great!! I have added you as an expert for $arg1.'
        }
        payload['platform'] = {
        'action':'add_expertise'
        }
    elif conversation_state == 'manage_account':
        payload['notification_type'] = 'REGULAR'
        payload['message'] = {
        'text' : 'Please visit concier.org to manage your account.'
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
                    "text":response,
                    "buttons":[
                    {
                    "type":"postback",
                    "title":"YES",
                    "payload":"agree_to_help:"+conversation_id
                    },
                    {
                    "type":"postback",
                    "title":"NO",
                    "payload":"decline_to_help:"+conversation_id
                    }
                    ]
                }
            }
        }
    elif conversation_state =='agree_to_help':
        payload['notification_type'] = 'REGULAR'
        payload['message'] = {
        'text' : 'Great. I am going to connect you to $arg1. \nCould you share for this need, what are the major products in the market, their price range, and how they differ?'
        }
        payload['platform'] = {
        'action':'assign_helper',
        'future_state':'connect_expert_to_user'
        }
    elif conversation_state =='connect_expert_to_user':
        payload['notification_type'] = 'REGULAR'
        payload['message'] = {
        'text' : response
        }
        payload['platform'] = {
        'action':'connect_expert_to_user',
        'future_state':'helper_helpee_matched'
        }
    elif conversation_state =='decline_to_help':
        payload['notification_type'] = 'REGULAR'
        payload['message'] = {
        'text' : 'Thanks for the quick response.'
        }
    elif conversation_state =='helper_helpee_matched':
        #payload['notification_type'] = 'REGULAR'
        payload['message'] = {
        'text' :response
        }
        payload['platform'] = {
        'action':'exchange_conversations'
        }
    elif conversation_state =='message_if_conversation_active':
        payload['message'] = {
            "attachment":{
                "type":"template",
                "payload":{
                    "template_type":"button",
                    "text":'Shopper is waiting for your answer.  Do you',
                    "buttons":[
                    {
                    "type":"postback",
                    "title":"Need more time (30 more minutes)",
                    "payload":"NEWSS:"+conversation_id
                    },
                    {
                    "type":"postback",
                    "title":"End conversation",
                    "payload":"NEWSS:"+conversation_id
                    }
                    ]
                }
            }
        }
    elif conversation_state =='conversation_ended_request_review':
        payload['message'] = {
            "attachment":{
                "type":"template",
                "payload":{
                    "template_type":"button",
                    "text":'This conversation has come to an end. Was this experience helpful?',
                    "buttons":[
                    {
                    "type":"postback",
                    "title":"👍 Good",
                    "payload":"conversation_review_requested:"+conversation_id
                    },
                    {
                    "type":"postback",
                    "title":"👎 Could have been better",
                    "payload":"conversation_review_requested:"+conversation_id
                    }
                    ]
                }
            }
        }
        payload['platform'] = {
        'action':'request_review_from_both_parties',
        'future_state':'conversation_review_requested'
        }
    elif conversation_state =='conversation_review_requested':
        payload['notification_type'] = 'REGULAR'
        payload['message'] = {
        'text' : 'Thank you for your valuable feedback. If at any time, you want to provide further feedback, please let us know!'
        }
        payload['platform'] = {
        'action':'record_review_close_the_conversation',
        'future_state':'conversation_closed'
        }
    elif conversation_state =='conversation_closed':
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
                    "title":"Get shopping help?",
                    "payload":"ask_product_category:"+conversation_id
                    },
                    {
                    "type":"postback",
                    "title":"Give shopping advise?",
                    "payload":"choose_expertise_category:"+conversation_id
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
    return payload
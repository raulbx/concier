def fb_payload(conversation_state,response,recipient_id,conversation_id,payload):
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
        'helper_next_state':'default_state',
        'helpee_next_state':'default_state',
        }
    elif conversation_state =='welcome_user':
        payload['message'] = {
            "attachment":{
                "type":"template",
                "payload":{
                    "template_type":"button",
                    "text":'Hi $arg1, I am your personal shopping Concier. How can I help you?\n\nAt any time, if you want to end the conversation, type #end and enter.',
                    "buttons":[
                    {
                    "type":"postback",
                    "title":"Get shopping help?",
                    "payload":"ask_product_category:"+conversation_id
                    },
                    {
                    "type":"postback",
                    "title":"Give shopping help?",
                    "payload":"choose_expertise_category:"+conversation_id
                    },
                    {
                    "type":"postback",
                    "title":"How can I help?",
                    "payload":"something_else:"+conversation_id
                    }
                    ]
                }
            }
        }
        payload['platform'] = {
        'action':'append_member_name'
        }
    elif conversation_state =='ask_product_category':
        payload['message'] = {
        'text' : 'What are you shopping for?',
        "quick_replies":[
            {
            "content_type":"text",
            "title":"Mobile",
            "payload":"record_category_ask_product:"+conversation_id
            },
            {
            "content_type":"text",
            "title":"Home",
            "payload":"record_category_ask_product:"+conversation_id
            },
            {
            "content_type":"text",
            "title":"Computer Related",
            "payload":"record_category_ask_product:"+conversation_id
            },
            {
            "content_type":"text",
            "title":"Other",
            "payload":"record_category_ask_product:"+conversation_id
            }
            ]
        }
        payload['platform'] = {
        'action':'remove_helper_ref_from_current_conversation'
        }
    elif conversation_state == 'record_category_ask_product':
        payload['message'] = {
        'text' : 'What kind of $arg1 product are you shopping for?'
        }
        payload['platform'] = {
        'current_conversation_state':'record_category_ask_product',
        'action':'get_specific_products',
        'field':'category',
        'helpee_next_state':'record_product_ask_specfic_product_brand'
        }
    elif conversation_state == 'record_product_ask_specfic_product_brand':
        payload['message'] = {
        'text' : 'Any specific product or brand in this category?'
        }
        payload['platform'] = {
        'current_conversation_state':'record_product_ask_specfic_product_brand',
        'action':'get_specific_products',
        'field':'product',
        'helpee_next_state':'record_specific_product_understand_need'
        }
    elif conversation_state == 'record_specific_product_understand_need':
        payload['notification_type'] = 'REGULAR'
        payload['message'] = {
        'text' : 'Can you describe why you need this product?\n\nPlease share your product need in more than 10 characters.'
        }
        payload['platform'] = {
        'action':'record_value_set_future_state',
        'field':'specific_product',
        'helpee_next_state':'record_need_ask_time_frame'
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
        'validate':'input_length_more_than_10',
        'validation__failure_message':'Please share your product need in more than 10 characters.',
        'helpee_next_state':'record_time_frame_ask_price'
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
        'helpee_next_state':'record_price_thank_user'
        }
    elif conversation_state == 'record_price_thank_user':
        payload['notification_type'] = 'REGULAR'
        payload['message'] = {
        'text' : 'Thank you. Let me find a community member, who can help you make a decision. At any time, if you want to cancel this request, type #end and enter.'
        }
        payload['platform'] = {
        'action':'record_price_and_broadcast_request',
        'helpee_next_state':'onboard_complete_waiting_for_expert'
        }
    elif conversation_state == 'onboard_complete_waiting_for_expert':
        payload['notification_type'] = 'REGULAR'
        payload['message'] = {
        'text' : 'Our search is on. We will be back soon with an community member to help you. If you want to cancel this request, type #end and enter.'
        }
        payload['platform'] = {
        'action':'set_future_state',
        'helpee_next_state':'onboard_complete_user_followed_up_once'
        }
    elif conversation_state == 'onboard_complete_user_followed_up_once':
        payload['notification_type'] = 'REGULAR'
        payload['message'] = {
        'text' : 'We are still looking. We will be back soon with an community member to help you out. If you want to cancel this request, type #end and enter.'
        }
        payload['platform'] = {
        'action':'set_future_state',
        'helpee_next_state':'onboard_complete_user_followed_up_twice'
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
        'text' : 'Which product did you buy recently and want to share your experience on?',
        "quick_replies":[
            {
            "content_type":"text",
            "title":"Mobiles",
            "payload":"register_expert:"+conversation_id
            },
            {
            "content_type":"text",
            "title":"Home",
            "payload":"register_expert:"+conversation_id
            },
            {
            "content_type":"text",
            "title":"Computer Related",
            "payload":"register_expert:"+conversation_id
            },
            {
            "content_type":"text",
            "title":"Other",
            "payload":"register_expert:"+conversation_id
            }
            ]
        }
        '''
        payload['message'] = {
            "attachment":{
                "type":"template",
                "payload":{
                    "template_type":"button",
                    "text":'Which product did you buy recently and want to share your experience on?',
                    "buttons":[
                    {
                    "type":"postback",
                    "title":"Mobile",
                    "payload":"register_expert:"+conversation_id
                    },
                    {
                    "type":"postback",
                    "title":"Home",
                    "payload":"register_expert:"+conversation_id
                    },
                    {
                    "type":"postback",
                    "title":"Computer Related",
                    "payload":"register_expert:"+conversation_id
                    }
                    ]
                }
            }
        }'''
        payload['platform'] = {
        'action':'remove_helpee_ref_from_current_conversation'
        }
    elif conversation_state == 'register_expert':
        payload['message'] = {
        'text' : 'What $arg1 product?'
        }
        payload['platform'] = {
        'current_conversation_state':'register_expert',
        'action':'get_specific_products',
        'helper_next_state':'add_expertise'
        }
    elif conversation_state == 'add_expertise':
        payload['notification_type'] = 'REGULAR'
        payload['message'] = {
        'text' : 'Great!! I have added you as an expert for $arg1. When a community user needs help with $arg1, we will contact you.'
        }
        payload['platform'] = {
        'action':'add_expertise',
        'field':'helper_product_category'
        }
    elif conversation_state == 'manage_account':
        payload['notification_type'] = 'REGULAR'
        payload['message'] = {
        'text' : 'Please visit concier.org to manage your account.'
        }
    elif conversation_state == 'something_else':
        payload['notification_type'] = 'REGULAR'
        payload['message'] = {
        'text' : 'Thank you for your message. Our concier admin will get back to you.'
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
        'text' : 'Thank you for agreeing to help a community member.\n\nBefore we connect you to the member, please answer some basic questions about your shopping experience on $arg1.\n\nWhat are the major products in the market that you are aware of?'
        }
        payload['platform'] = {
        'action':'assign_helper',
        'helper_next_state':'record_key_products_ask_price_range'
        }
    ### 5 Questions Begin
    elif conversation_state =='record_key_products_ask_price_range':
        payload['notification_type'] = 'REGULAR'
        payload['message'] = {
        'text' : 'What is the price range of these products?'
        }
        payload['platform'] = {
        'action':'record_value_set_future_state',
        'field':'expert_key_products_in_the_market',
        'helper_next_state':'record_price_range_ask_differences'
        }
    elif conversation_state =='record_price_range_ask_differences':
        payload['notification_type'] = 'REGULAR'
        payload['message'] = {
        'text' : 'What are the differences between these products?'
        }
        payload['platform'] = {
        'action':'record_value_set_future_state',
        'field':'expert_product_price_ranges',
        'helper_next_state':'record_product_differences_product_bought'
        }
    elif conversation_state =='record_product_differences_product_bought':
        payload['notification_type'] = 'REGULAR'
        payload['message'] = {
        'text' : 'What product did you buy'
        }
        payload['platform'] = {
        'action':'record_value_set_future_state',
        'field':'expert_product_differences',
        'helper_next_state':'record_product_bought_ask_why_product_bought'
        }
    elif conversation_state =='record_product_bought_ask_why_product_bought':
        payload['notification_type'] = 'REGULAR'
        payload['message'] = {
        'text' : 'Why did you buy this product'
        }
        payload['platform'] = {
        'action':'record_value_set_future_state',
        'field':'expert_what_product_bought',
        'helper_next_state':'record_why_product_bought_connect_expert_to_user'
        }
    elif conversation_state =='record_why_product_bought_connect_expert_to_user':
        payload['notification_type'] = 'REGULAR'
        payload['message'] = {
        'text' : 'Thank you. I am going to connect you to our community member, $arg1.\n\nCommunity member will have 12 hours to interact with you before you are released back to the community.\n\nAt any time, if you want to end the conversation, type #end and enter.'
        }
        payload['platform'] = {
        'action':'connect_expert_to_user',
        'field':'expert_why_product_bought',
        'helper_next_state':'helper_helpee_matched',
        'helpee_next_state':'helper_helpee_matched'
        }
### End of five questions
    elif conversation_state =='connect_expert_to_user':
        payload['notification_type'] = 'REGULAR'
        payload['message'] = {
        'text' : response
        }
        payload['platform'] = {
        'action':'connect_expert_to_user',
        'helper_next_state':'helper_helpee_matched',
        'helpee_next_state':'helper_helpee_matched'
        }
####this state is not required
    elif conversation_state =='decline_to_help':
        payload['notification_type'] = 'REGULAR'
        payload['message'] = {
        'text' : 'Thanks for the quick response.'
        }
        payload['platform'] = {
        'action':'decline_to_help'
        }
    elif conversation_state =='helper_helpee_matched':
        #payload['notification_type'] = 'REGULAR'
        payload['message'] = {
        'text' :response
        }
        payload['platform'] = {
        'action':'exchange_conversations'
        }
    elif conversation_state =='overdue_conversation':
        payload['notification_type'] = 'REGULAR'
        payload['message'] = {
        'text' :'I am sorry. We don\'t have a member who can help you now.  Please check back again in sometime, and ask again.'
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
                    "payload":"extend_conversation:"+conversation_id
                    },
                    {
                    "type":"postback",
                    "title":"End conversation",
                    "payload":"end_conversation:"+conversation_id
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
                    "title":"Not so good 👎",
                    "payload":"conversation_review_requested:"+conversation_id
                    }
                    ]
                }
            }
        }
        payload['platform'] = {
        'action':'request_review',
        'next_state':'conversation_review_requested'
        }
    elif conversation_state =='conversation_review_requested':
        payload['notification_type'] = 'REGULAR'
        payload['message'] = {
        'text' : 'Can you elaborate?'
        }
        payload['platform'] = {
        'action':'record_review',
        'next_state':'thank_user'
        }
    elif conversation_state =='thank_user':
        payload['notification_type'] = 'REGULAR'
        payload['message'] = {
        'text' : 'Thank you for your valuable feedback. If at any time, you want to provide further feedback, please let us know!'
        }
        payload['platform'] = {
        'action':'record_review',
        'next_state':'conversation_closed'
        }
    elif conversation_state =='conversation_closed':
        payload['platform'] = {
        'action':'start_new_conversation'
        }
    elif conversation_state =='validation_failure_response':
        payload['notification_type'] = 'REGULAR'
        payload['message'] = {
        'text' : response
        }
    return payload
def fb_messanger_payload(conversation_state,response,recipient_id,conversation_id,payload):
    if bot_state =='welcome_user':

    elif bot_state =='conversation_persistant_menut':
         payload['persistent_menu'] = {
            'locale':'default',
            'composer_input_disabled': False,
            'call_to_actions':[
                {
                'title':'My Account',
                'type':'nested',
                'call_to_actions':[
                    {
                    'title':'Pay Bill',
                    'type':'postback',
                    'payload':'PAYBILL_PAYLOAD'
                    },
                    {
                    'type':'web_url',
                    'title':'Latest News',
                    'url':'https://www.messenger.com/',
                    'webview_height_ratio':'full'
                    }
                ]
                }
            ]
        }

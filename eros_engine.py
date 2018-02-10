user_state = {
	'recipient_id':'',
	'fbseq':0,
	'active_question':0,
	'responder_id':''
}
responses = ['This is Eros Match. How can I help you?','Let me find someone, who can help you with it.',' is happy to help you with this purchase. Do you want to connect with him?','Great. I am going to connect you to ']
def fbrespond(recipient_id,sequence):
	response_message = 'This is empty'
	if user_state['recipient_id']== recipient_id :
		print("User interaction is in progress")
		if sequence > user_state['fbseq'] :
			#This is new message. Advance to the next question
			print (user_state)
			user_state['fbseq'] = sequence
			user_state['active_question'] = user_state['active_question'] + 1
			nextQID = user_state['active_question']
			print (user_state)
			response_message=responses[nextQID]
			return response_message
		else :
			print ('Message came twice')
	# they are already in conversation
	else :
		print ('First interaction')
		user_state['recipient_id'] = recipient_id
		response_message = responses[1]
		return response_message
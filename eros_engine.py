user_state = {
	'recipient_id':'',
	'question':0,
	'responder_id':''
}
responses = ['This is Eros. How can I help you?','Let me find someone, who can help you with it.',' is happy to help you with this purchase. Do you want to connect with him?','Great. I am going to connect you to ']
def fbrespond(recipient_id):
	response_message = 'This is empty'
	if user_state['recipient_id']== recipient_id :
		print("User interaction is in progress")
		nextQuestion=user_state['question']+1
		response_message=responses[nextQuestion]
		user_state['question']=nextQuestion
		return response_message
	# they are already in conversation
	else :
		print ('First interaction')
		user_state['recipient_id'] = recipient_id
		response_message = responses[1]
		return response_message
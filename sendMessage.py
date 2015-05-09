# Send a message given a phone number and text-body
from twilio.rest import TwilioRestClient 

def sendMessage(to_number, text): 

	ACCOUNT_SID = "" 
	AUTH_TOKEN = "" 
	twilioNumber = ""

	client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN) 

	message = client.sms.messages.create(
		to=to_number, 
		from_=twilioNumber, 
		body=text,  
	)

	print message.sid
# Return the help text
def list():
	return 'Note - All commands are case insensitive.\n\n'\
	'STOP - Unsubscribe from this service.\n\n' \
	'START - Subscribe to this service. This command does nothing unless you have previously stopped the service.\n\n'\
	'LIST - See this list of commands.\n\n'\
	'REGISTER - Register your phone number. You must provide a first and last name. Example: REGISTER JOHN SMITH.\n\n'\
	'JOB - Usage: JOB WHAT from TOWN_1 to TOWN_2 in X days. '\
	'The issuer will be notified when another user claims this job, and when it is completed. Note that X must be a valid integer, '\
	'and all parameters (WHAT, TOWN_1, TOWN_2, and X) must be supplied.\n\n'\
	'ACCEPT - Accept a job. You must provide the job ID. Example: ACCEPT 1243.\n\n'\
	'COMPLETE - Mark a job you have accepted as completed. You must provide the job ID. Example: COMPLETE 1243.\n\n'\
	'REQUEST - Request the currently pending jobs.\n\n'\
	'DUTIES - Request a list of jobs that you have accepted.'

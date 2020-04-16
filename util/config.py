import os, logging

logging_level = os.environ.get('LOGGING_LEVEL')
logging.basicConfig(level=logging_level)


first_run = os.environ.get('FIRST_RUN').lower()
if first_run == 'true':
	first_run = True 
elif first_run == 'false':
	first_run = False 
else:
	raise Exception("FIRST_RUN must be set to true or false.")
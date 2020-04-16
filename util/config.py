import os, logging

logging.basicConfig(level='INFO')

first_run = os.environ.get('FIRST_RUN').lower()
if first_run == 'true':
	first_run = True 
elif first_run == 'false':
	first_run = False 
else:
	raise Exception("FIRST_RUN must be set to true or false.")
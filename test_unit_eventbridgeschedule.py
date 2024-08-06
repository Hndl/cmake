import unittest
from handlefactory import * 
from typing import Final
import logging
from datetime import datetime




# Set up our logger
logging.basicConfig(level=logging.INFO,format='%(asctime)s:%(levelname)s:[%(module)s.%(funcName)s.%(lineno)d]:%(message)s')
logger = logging.getLogger()
logger.info(f'\n')


class TestHandlersFunctions(unittest.TestCase):

	def setUp(self):
		logger.info(f'\n************* App logging Below Relates to This Test ********************')
				
	
	

	def test_a_delete_event_schedule(self) :
		action = 'Delete'
		typeOf = 'EventBridgeSchedule'
		
		testDescription = f'{action} {typeOf} :: Test '
		for nodeId in range(13, 16):
			try:
				jcfg = self.getJson('./qa.json')	
				logger.info(f'{testDescription} - Started')
				self.executeTest(jcfg,action,typeOf,nodeId,testDescription)
				logger.info(f'{testDescription} - Complete')

			except Exception as eX:
				logger.error(f'{testDescription} - Exception: {eX}')

	
	def test_b_create_event_schedule(self) :
		action = 'Create'
		typeOf = 'EventBridgeSchedule'
		
		testDescription = f'{action} {typeOf} :: '

		for nodeId in range(13, 16):
			try:
				jcfg = self.getJson('./qa.json')
				jcfg['Create'][11]['arn'] = 'arn:aws:iam::905418456790:policy/vw-vindolanda-dev-AWSLambdaBasicExecutionRole'
				jcfg['Create'][8]['arn'] = 'arn:aws:iam::905418456790:role/vw-vindolanda-dev-dataprocessor-generic-a'
				jcfg['Create'][12]['arn'] = 'arn:aws:lambda:eu-north-1:905418456790:function:vw-vindolanda-dev-data-processor-generic'

				
				logger.info(f'{testDescription} - Started')
				self.executeTest(jcfg,action,typeOf,nodeId,testDescription)
				logger.info(f'{testDescription} - Complete')

				
			except Exception as eX:
				logger.error(f'{testDescription} - Exception: {eX}')

	
		#print(json.dumps(jcfg,indent=4))
				
	def getJson(self,f):
		cfgJson=None
		with open(f) as json_data:
			cfgJson = json.load(json_data)
			json_data.close()
		return cfgJson

	def executeTest(self,cfgJson, action,typeOf, nodeId, desc) :
		obj = cloudActionFactory(action, typeOf,cfgJson,cfgJson[action][nodeId])
		obj.init(cfgJson,cfgJson[action][nodeId])
		obj.execute()
		obj.final()
	

if __name__ == '__main__':
	unittest.main()

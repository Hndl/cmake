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
				
	
	

	def test_a_delete_lambda(self) :
		action = 'Delete'
		typeOf = 'Lambda'
		nodeId = 12
		testDescription = f'{action} {typeOf} :: Test '
		
		try:
			jcfg = self.getJson('./qa.json')	
			logger.info(f'{testDescription} - Started')
			self.executeTest(jcfg,action,typeOf,nodeId,testDescription)
			logger.info(f'{testDescription} - Complete')

		except Exception as eX:
			logger.error(f'{testDescription} - Exception: {eX}')

	
	def test_b_create_lambda(self) :
		action = 'Create'
		typeOf = 'Lambda'
		nodeId = 12
		testDescription = f'{action} {typeOf} :: '
		
		try:
			jcfg = self.getJson('./qa.json')
			jcfg['Create'][11]['arn'] = 'arn:aws:iam::905418456790:policy/vw-vindolanda-dev-AWSLambdaBasicExecutionRole'
			jcfg['Create'][8]['arn'] = 'arn:aws:iam::905418456790:role/vw-vindolanda-dev-dataprocessor-generic-a'

			
			logger.info(f'{testDescription} - Started')
			self.executeTest(jcfg,action,typeOf,nodeId,testDescription)
			logger.info(f'{testDescription} - Complete')

			print(json.dumps(jcfg,indent=4))
		except Exception as eX:
			logger.error(f'{testDescription} - Exception: {eX}')



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

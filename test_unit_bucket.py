import unittest
from handlefactory import * 
from typing import Final
import logging
from datetime import datetime




# Set up our logger
logging.basicConfig(level=logging.INFO,format='%(asctime)s:%(levelname)s:[%(module)s.%(funcName)s]:%(message)s')
logger = logging.getLogger()



class TestHandlersFunctions(unittest.TestCase):

	def setUp(self):
		logger.info(f'\n************* App logging Below Relates to This Test ********************')
				
	
	

	def test_a_delete_bucket(self) :
		action = 'Delete'
		typeOf = 'Bucket'
		nodeId = 0
		testDescription = f'{action} {typeOf} :: Test :: delete inbound bucket'
		
		try:
			jcfg = self.getJson('./qa.json')	
			logger.info(f'{testDescription} - Started')
			self.executeTest(jcfg,action,typeOf,nodeId,testDescription)
			logger.info(f'{testDescription} - Complete')

		except Exception as eX:
			logger.error(f'{testDescription} - Exception: {eX}')

	
	def test_b_create_bucket(self) :
		action = 'Create'
		typeOf = 'Bucket'
		nodeId = 0
		testDescription = f'{action} {typeOf} :: bucket-inbound :: Test'

		try:
			jcfg = self.getJson('./qa.json')
			logger.info(f'{testDescription} - Started')
			self.executeTest(jcfg,action,typeOf,nodeId,testDescription)
			logger.info(f'{testDescription} - Complete')

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

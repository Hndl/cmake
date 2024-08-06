import unittest
from handlefactory import * 
from typing import Final
import logging
from datetime import datetime




# Set up our logger
logging.basicConfig(level=logging.DEBUG,format='%(asctime)s:%(levelname)s:[%(module)s.%(funcName)s.%(lineno)d]:%(message)s')
logger = logging.getLogger()
logger.info(f'\n')


class TestBasicFunctions(unittest.TestCase):

	def setUp(self):
		logger.info(f'\n************* App logging Below Relates to This Test ********************')
				
	
	

	def test_ref_replacement(self) :
		accountId = '905418456790'
		action = 'Create'
		typeOf = 'Policy'
		nodeId = 11
		testDescription = f'{action} {typeOf} :: Test'
		
		try:
			jcfg = self.getJson('./qa.json')	
			
			jcfg['Create'][10]['arn'] = 'arn:aws:logs:eu-north-1:905418456790:log-group:/aws/lambda/vw/dev/vindolanda/lambda/dataprocessor-loggroup-a:*'
			jcfg['Create'][10]['areaArn'] = 'arn:aws:logs:eu-north-1:905418456790:*'

			logger.info(f'{testDescription} - Started')
			val =self.executeTest(jcfg,action,typeOf,nodeId,testDescription, 'Template')
			logger.info(f'{testDescription} \n {val}')
			
			logger.info(f'{testDescription} - Complete')
			
		except Exception as eX:
			logger.error(f'{testDescription} - Exception: {eX}')

	
		

	def getJson(self,f):
		cfgJson=None
		with open(f) as json_data:
			cfgJson = json.load(json_data)
			json_data.close()
		return cfgJson

	def executeTest(self,cfgJson, action,typeOf, nodeId, desc, attr) :
		obj = cloudActionFactory('default', 'default',cfgJson,cfgJson[action][nodeId])
		obj.init(cfgJson,cfgJson[action][nodeId])
		logger.info(f'\n************* test starts now *******************')

		bOK, val =  obj.getResourceConfiguration(attr,'None')
		return val

if __name__ == '__main__':
	unittest.main()

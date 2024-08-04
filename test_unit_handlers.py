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
				
	
	def test_a_delete_file(self) :
		action = 'Delete'
		typeOf = 'File'
		nodeId = 0
		testDescription = f'{action} {typeOf} :: Test :: Delete meteo master.csv'
		
		try:
			jcfg = self.getJson('./qa.json')	
			logger.info(f'{testDescription} - Started')
			self.executeTest(jcfg,action,typeOf,nodeId,testDescription)
			logger.info(f'{testDescription} - Complete')

		except Exception as eX:
			logger.error(f'{testDescription} - Exception: {eX}')

	def test_b_delete_bucket(self) :
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

	def test_c_delete_policy(self) :
		action = 'Delete'
		typeOf = 'Policy'
		nodeId = 4
		testDescription = f'{action} {typeOf} :: Test :: create bucket-inbound'
		
		try:
			jcfg = self.getJson('./qa.json')
			logger.info(f'{testDescription} - Started')
			self.executeTest(jcfg,action,typeOf,nodeId,testDescription)
			logger.info(f'{testDescription} - Complete')

		except Exception as eX:
			logger.error(f'{testDescription} - Exception: {eX}')

	def test_cc_delete_policy(self) :
		action = 'Delete'
		typeOf = 'Policy'
		nodeId = 5
		testDescription = f'{action} {typeOf} :: Test ::  '
		
		try:
			jcfg = self.getJson('./qa.json')
			logger.info(f'{testDescription} - Started')
			self.executeTest(jcfg,action,typeOf,nodeId,testDescription)
			logger.info(f'{testDescription} - Complete')

		except Exception as eX:
			logger.error(f'{testDescription} - Exception: {eX}')

	def test_ccc_delete_policy(self) :
		action = 'Delete'
		typeOf = 'Policy'
		nodeId = 6
		testDescription = f'{action} {typeOf}	-:: bucket-inbound :: Test'
		
		try:
			jcfg = self.getJson('./qa.json')
			logger.info(f'{testDescription} - Started')
			self.executeTest(jcfg,action,typeOf,nodeId,testDescription)
			logger.info(f'{testDescription} - Complete')

		except Exception as eX:
			logger.error(f'{testDescription} - Exception: {eX}')

	def test_cccc_delete_policy(self) :
		action = 'Delete'
		typeOf = 'Policy'
		nodeId = 8
		testDescription = f'{action} {typeOf}	-:: bucket-inbound :: Test'
		
		try:
			jcfg = self.getJson('./qa.json')
			logger.info(f'{testDescription} - Started')
			self.executeTest(jcfg,action,typeOf,nodeId,testDescription)
			logger.info(f'{testDescription} - Complete')

		except Exception as eX:
			logger.error(f'{testDescription} - Exception: {eX}')

	
	def test_d_create_bucket(self) :
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

	def test_e_create_file(self) :
		action = 'Create'
		typeOf = 'File'
		nodeId = 3
		testDescription = f'{action} {typeOf} :: Test'
		try:
			jcfg = self.getJson('./qa.json')
			logger.info(f'{testDescription} - Started')
			self.executeTest(jcfg,action,typeOf,nodeId,testDescription)
			logger.info(f'{testDescription} - Complete')

		except Exception as eX:
			logger.error(f'{testDescription} - Exception: {eX}')

	def test_e_create_policy(self) :
		action = 'Create'
		typeOf = 'Policy'
		nodeId = 4
		testDescription = f'{action} {typeOf} :: Test'
		
		try:
			jcfg = self.getJson('./qa.json')
			jcfg['Create'][0]['arn'] = f'arn:aws:s3:::vw-vindolanda-inbound'
			jcfg['Create'][1]['arn'] = f'arn:aws:s3:::vw-vindolanda-backup'
			jcfg['Create'][2]['arn'] = f'arn:aws:s3:::vw-vindolanda-master'

			logger.info(f'{testDescription} - Started')
			self.executeTest(jcfg,action,typeOf,nodeId,testDescription)
			logger.info(f'{testDescription} - Complete')

		except Exception as eX:
			logger.error(f'{testDescription} - Exception: {eX}')

	def test_ee_create_policy(self) :
		action = 'Create'
		typeOf = 'Policy'
		nodeId = 5
		testDescription = f'{action} {typeOf} :: Test'
		
		try:
			jcfg = self.getJson('./qa.json')
			jcfg['Create'][0]['arn'] = f'arn:aws:s3:::vw-vindolanda-inbound'
			jcfg['Create'][1]['arn'] = f'arn:aws:s3:::vw-vindolanda-backup'
			jcfg['Create'][2]['arn'] = f'arn:aws:s3:::vw-vindolanda-master'

			logger.info(f'{testDescription} - Started')
			self.executeTest(jcfg,action,typeOf,nodeId,testDescription)
			logger.info(f'{testDescription} - Complete')

		except Exception as eX:
			logger.error(f'{testDescription} - Exception: {eX}')

	def test_eeee_create_policy(self) :
		action = 'Create'
		typeOf = 'Policy'
		nodeId = 6
		testDescription = f'{action} {typeOf} :: Test'
		
		try:
			jcfg = self.getJson('./qa.json')
			jcfg['Create'][0]['arn'] = f'arn:aws:s3:::vw-vindolanda-inbound'
			jcfg['Create'][1]['arn'] = f'arn:aws:s3:::vw-vindolanda-backup'
			jcfg['Create'][2]['arn'] = f'arn:aws:s3:::vw-vindolanda-master'

			logger.info(f'{testDescription} - Started')
			self.executeTest(jcfg,action,typeOf,nodeId,testDescription)
			logger.info(f'{testDescription} - Complete')

		except Exception as eX:
			logger.error(f'{testDescription} - Exception: {eX}')

	def test_eeeee_create_policy(self) :
		action = 'Create'
		typeOf = 'Policy'
		nodeId = 7
		testDescription = f'{action} {typeOf} :: Test'
		
		try:
			jcfg = self.getJson('./qa.json')
			jcfg['Create'][0]['arn'] = f'arn:aws:s3:::vw-vindolanda-inbound'
			jcfg['Create'][1]['arn'] = f'arn:aws:s3:::vw-vindolanda-backup'
			jcfg['Create'][2]['arn'] = f'arn:aws:s3:::vw-vindolanda-master'

			logger.info(f'{testDescription} - Started')
			self.executeTest(jcfg,action,typeOf,nodeId,testDescription)
			logger.info(f'{testDescription} - Complete')

		except Exception as eX:
			logger.error(f'{testDescription} - Exception: {eX}')

	def test_f_delete_role(self) :
		action = 'Delete'
		typeOf = 'Role'
		nodeId = 7
		testDescription = f'{action} {typeOf} :: Test'
		try:
			jcfg = self.getJson('./qa.json')
			jcfg['Create'][0]['arn'] = f'arn:aws:s3:::vw-vindolanda-inbound'
			jcfg['Create'][1]['arn'] = f'arn:aws:s3:::vw-vindolanda-backup'
			jcfg['Create'][2]['arn'] = f'arn:aws:s3:::vw-vindolanda-master'
				
			logger.info(f'{testDescription} - Started')
			self.executeTest(jcfg,action,typeOf,nodeId,testDescription)
			logger.info(f'{testDescription} - Complete')

		except Exception as eX:
			logger.error(f'{testDescription} - Exception: {eX}')

	def test_g_create_role(self) :
		accountId = '905418456790'
		action = 'Create'
		typeOf = 'Role'
		nodeId = 8
		testDescription = f'{action} {typeOf} :: Test'
		
		try:
			jcfg = self.getJson('./qa.json')
			jcfg['Create'][0]['arn'] = f'arn:aws:s3:::vw-vindolanda-inbound'
			jcfg['Create'][1]['arn'] = f'arn:aws:s3:::vw-vindolanda-backup'
			jcfg['Create'][2]['arn'] = f'arn:aws:s3:::vw-vindolanda-master'
			jcfg['Create'][7]['arn'] = f'arn:aws:iam::{accountId}:policy/vw-vindolanda-dev-AWSLambdaBasicExecutionRole' #AWSLambdaBasicExecutionRole
			jcfg['Create'][4]['arn'] = f'arn:aws:iam::{accountId}:policy/vw-vindolanda-dev-dataprocessor-meteo' #policy-dataprocessor-meteo
			jcfg['Create'][5]['arn'] = f'arn:aws:iam::{accountId}:policy/vw-vindolanda-dev-dataprocessor-pico' #policy-dataprocessor-pico
			jcfg['Create'][6]['arn'] = f'arn:aws:iam::{accountId}:policy/vw-vindolanda-dev-dataprocessor-temphion' #policy-dataprocessor-temphion
				
			logger.info(f'{testDescription} - Started')
			self.executeTest(jcfg,action,typeOf,nodeId,testDescription)
			logger.info(f'{testDescription} - Complete')

		except Exception as eX:
			logger.error(f'{testDescription} - Exception: {eX}')

	def test_h_delete_user(self) :
		accountId = '905418456790'
		action = 'Delete'
		typeOf = 'User'
		nodeId = 9
		testDescription = f'{action} {typeOf} :: Test'
		
		try:
			jcfg = self.getJson('./qa.json')	
			logger.info(f'{testDescription} - Started')
			self.executeTest(jcfg,action,typeOf,nodeId,testDescription)
			logger.info(f'{testDescription} - Complete')
			#logger.info(f'\n{json.dumps(jcfg, indent=4)}')

		except Exception as eX:
			logger.error(f'{testDescription} - Exception: {eX}')

	def test_hh_delete_user(self) :
		accountId = '905418456790'
		action = 'Create'
		typeOf = 'User'
		nodeId = 9
		testDescription = f'{action} {typeOf} :: Test'
		
		try:
			jcfg = self.getJson('./qa.json')	
			logger.info(f'{testDescription} - Started')
			self.executeTest(jcfg,action,typeOf,nodeId,testDescription)
			logger.info(f'{testDescription} - Complete')
			logger.info(f'\n{json.dumps(jcfg, indent=4)}')

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

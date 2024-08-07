from typing import Final
from handlers import *

import json
import boto3
import logging


CONST_ERRMSG_MISSING_ATTR                    : Final[str]    = 'attribute not found in resource configuration'


logging.basicConfig(level=logging.INFO,format='%(asctime)s:%(levelname)s:[%(module)s.%(funcName)s]:%(message)s')
logger = logging.getLogger()

class DeleteLoggroup( CloudAction):
	def init(self, configuration : dict, resourceConfiguration : dict  ) -> bool:
		
		#self.client = boto3.client('logs')
		self.action = "Delete Loggroup"
		self.configuration = configuration
		self.resourceConfiguration = resourceConfiguration

		self.setFail()
		
		bOK, self.ref = self.getResourceConfiguration('ref',None)
		if (bOK == False or self.ref == None):
			raise ActionHandlerConfigurationException(f'ref {CONST_ERRMSG_MISSING_ATTR} {resourceConfiguration}') 

		bOK, self.id = self.getResourceConfiguration('id',None)
		if (bOK == False or self.id == None):
			raise ActionHandlerConfigurationException(f'id {CONST_ERRMSG_MISSING_ATTR} {resourceConfiguration}') 
		
		bOK, self.region = self.getResourceConfiguration('region',None)
		if (bOK == False or self.region == None):
			raise ActionHandlerConfigurationException(f'region {CONST_ERRMSG_MISSING_ATTR} {resourceConfiguration}') 

		bOK, self.awsSecretAccessKey = self.getResourceConfiguration('aws-secret-access-key',None)
		if (bOK == False or self.awsSecretAccessKey == None):
			raise ActionHandlerConfigurationException(f'aws-secret-access-key {CONST_ERRMSG_MISSING_ATTR} {resourceConfiguration}') 

		bOK, self.awsAccessKeyId = self.getResourceConfiguration('aws-access-key-id',None)
		if (bOK == False or self.awsAccessKeyId == None):
			raise ActionHandlerConfigurationException(f'aws-access-key-id {CONST_ERRMSG_MISSING_ATTR} {resourceConfiguration}') 

		self.client = boto3.client('logs',
									aws_access_key_id=self.awsAccessKeyId,
									aws_secret_access_key=self.awsSecretAccessKey,
									region_name=self.region)
		return
	

	def execute( self ):
		
		logStr = f'[{self.ref}]'	
		logger.info(f'{logStr}.Started')
		response = self.client.delete_log_group(logGroupName=self.id)
		
		if (self.getHTTPStatusCodeOK(response) == False):
			raise Exception(f'{logStr} Failed:{response}')
		
		self.setSuccess()

		logger.info(f'{logStr}.Done')

	def final( self) :
		pass

			


class CreateLoggroup( CloudAction):
	

	def init(self, configuration : dict, resourceConfiguration : dict  ) -> bool:
		
		#self.client = boto3.client('logs')
		#self.stsClient = boto3.client('sts')

		self.action = "Create Loggroup"
		self.configuration = configuration
		self.resourceConfiguration = resourceConfiguration

		self.setFail()

		#self.accountId = self.stsClient.get_caller_identity()['Account']
		
		bOK, self.ref = self.getResourceConfiguration('ref',None)
		if (bOK == False or self.ref == None):
			raise ActionHandlerConfigurationException(f'ref {CONST_ERRMSG_MISSING_ATTR} {resourceConfiguration}') 

		bOK, self.id= self.getResourceConfiguration('id',None)
		if (bOK == False or self.id == None):
			raise ActionHandlerConfigurationException(f'id {CONST_ERRMSG_MISSING_ATTR} {resourceConfiguration}') 

		bOK, self.groupClass = self.getResourceConfiguration('groupClass','STANDARD')

		bOK, self.retentionPeriod = self.getResourceConfiguration('retentionPeriod','1')
		self.retentionPeriod = int(self.retentionPeriod)
		
		bOK, self.tags = self.getResourceConfiguration('TagSet',None)
		if (self.tags != None):
			self.new_tags = json.loads(self.tags) 

		bOK, self.region = self.getResourceConfiguration('region',None)
		if (bOK == False or self.region == None):
			raise ActionHandlerConfigurationException(f'region {CONST_ERRMSG_MISSING_ATTR} {resourceConfiguration}') 

		bOK, self.awsSecretAccessKey = self.getResourceConfiguration('aws-secret-access-key',None)
		if (bOK == False or self.awsSecretAccessKey == None):
			raise ActionHandlerConfigurationException(f'aws-secret-access-key {CONST_ERRMSG_MISSING_ATTR} {resourceConfiguration}') 

		bOK, self.awsAccessKeyId = self.getResourceConfiguration('aws-access-key-id',None)
		if (bOK == False or self.awsAccessKeyId == None):
			raise ActionHandlerConfigurationException(f'aws-access-key-id {CONST_ERRMSG_MISSING_ATTR} {resourceConfiguration}') 

		self.client = boto3.client('logs',
									aws_access_key_id=self.awsAccessKeyId,
									aws_secret_access_key=self.awsSecretAccessKey,
									region_name=self.region)

		self.stsClient = boto3.client('sts',
									aws_access_key_id=self.awsAccessKeyId,
									aws_secret_access_key=self.awsSecretAccessKey,
									region_name=self.region)

		self.accountId = self.stsClient.get_caller_identity()['Account']

		return

	def makeARN(self):
		#arn:aws:logs:eu-north-1:851725181036:log-group:/aws/lambda/vw-vindolanda-qa-dataprocessor-generic:*
		return(f'arn:aws:logs:{self.region}:{self.accountId}:log-group:{self.id}:*')

	def makeAreaARN(self):
		#arn:aws:logs:eu-north-1:851725181036:*
		return(f'arn:aws:logs:{self.region}:{self.accountId}:*')

	def applyRetentionPeriod(self):

		logStr = f'[{self.ref}]'
		logger.info(f'{logStr}.Started')
		response = self.client.put_retention_policy(
    		logGroupName=self.id,
    		retentionInDays=self.retentionPeriod
		)

		#print(json.dumps(response,indent=4))
		if (self.getHTTPStatusCodeOK(response) == False):
			raise Exception(f'{logStr} Failed:{response}')

		logger.info(f'{logStr}.Done')

	def creteLogGroup(self):
		logStr = f'[{self.ref}]'
		logger.info(f'{logStr}.Started')

		response = self.client.create_log_group(
		    logGroupName=self.id,
		    logGroupClass=self.groupClass,
		    tags=self.new_tags
		)
		
		if (self.getHTTPStatusCodeOK(response) == False):
			raise Exception(f'{logStr} Failed:{response}')

		logger.info(f'{logStr}.Done')

	def execute(self ) :
		
		self.setResourceConfiguration('arn',self.makeARN())
		self.setResourceConfiguration('areaArn',self.makeAreaARN())
		self.creteLogGroup()
		self.applyRetentionPeriod()
		self.setSuccess()
		
		return True

	def final(self ) -> bool:
		pass

	
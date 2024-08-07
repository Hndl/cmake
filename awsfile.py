
import json
import boto3
import logging
from handlers import *

CONST_ERRMSG_MISSING_ATTR                    : Final[str]    = 'attribute not found in resource configuration'

logging.basicConfig(level=logging.INFO,format='%(asctime)s:%(levelname)s:[%(module)s.%(funcName)s]:%(message)s')
logger = logging.getLogger()

class DeleteFile(CloudAction):
	def init(self, configuration : dict, resourceConfiguration : dict  ) -> bool:
		
		#self.client = boto3.client('s3')
		self.action = "Delete File"
		self.configuration = configuration
		self.resourceConfiguration = resourceConfiguration

		self.setFail()
		
		bOK, self.ref = self.getResourceConfiguration('ref',None)
		if (bOK == False or self.ref == None):
			raise ActionHandlerConfigurationException(f'ref {CONST_ERRMSG_MISSING_ATTR} {resourceConfiguration}') 

		bOK, self.bucket_name = self.getResourceConfiguration('bucket',None)
		if (bOK == False or self.bucket_name == None):
			raise ActionHandlerConfigurationException(f'bucket {CONST_ERRMSG_MISSING_ATTR} {resourceConfiguration}')

		bOK, self.key = self.getResourceConfiguration('key',None)
		if (bOK == False or self.key == None):
			raise ActionHandlerConfigurationException(f'key {CONST_ERRMSG_MISSING_ATTR} {resourceConfiguration}')  
		
		bOK, self.region = self.getResourceConfiguration('region',None)
		if (bOK == False or self.region == None):
			raise ActionHandlerConfigurationException(f'region {CONST_ERRMSG_MISSING_ATTR} {resourceConfiguration}') 

		bOK, self.awsSecretAccessKey = self.getResourceConfiguration('aws-secret-access-key',None)
		if (bOK == False or self.awsSecretAccessKey == None):
			raise ActionHandlerConfigurationException(f'aws-secret-access-key {CONST_ERRMSG_MISSING_ATTR} {resourceConfiguration}') 

		bOK, self.awsAccessKeyId = self.getResourceConfiguration('aws-access-key-id',None)
		if (bOK == False or self.awsAccessKeyId == None):
			raise ActionHandlerConfigurationException(f'aws-access-key-id {CONST_ERRMSG_MISSING_ATTR} {resourceConfiguration}') 

		self.client = boto3.client('s3',
									aws_access_key_id=self.awsAccessKeyId,
									aws_secret_access_key=self.awsSecretAccessKey,
									region_name=self.region)
	
		return

	def execute( self ):
		
		logStr = f'[{self.ref}]'
		logger.info(f'{logStr}.Started ({self.bucket_name}{self.key})')
		response = self.client.delete_object(Bucket=self.bucket_name, Key=self.key)
		self.setSuccess()
		logger.info(f'{logStr}.Done')
		return

	def final( self) :
		pass

class CreateFile( CloudAction):

	def init(self, configuration : dict, resourceConfiguration : dict  ) -> bool:

		
		#self.client = boto3.client('s3')
		self.action = 'Create File'
		self.configuration = configuration
		self.resourceConfiguration = resourceConfiguration
		self.setFail()
		
		bOK, self.ref = self.getResourceConfiguration('ref',None)
		if (bOK == False or self.ref == None):
			raise ActionHandlerConfigurationException(f'ref {CONST_ERRMSG_MISSING_ATTR} {resourceConfiguration}') 

		bOK, self.bucket_name = self.getResourceConfiguration('bucket',None)
		if (bOK == False or self.bucket_name == None):
			raise ActionHandlerConfigurationException(f'bucket {CONST_ERRMSG_MISSING_ATTR} {resourceConfiguration}') 
		
		bOK, self.key = self.getResourceConfiguration('key',None)
		if (bOK == False or self.key == None):
			raise ActionHandlerConfigurationException(f'key {CONST_ERRMSG_MISSING_ATTR} {resourceConfiguration}') 
		
		bOK, self.content = self.getResourceConfiguration('content',None)
		if (bOK == False or self.content == None):
			raise ActionHandlerConfigurationException(f'content {CONST_ERRMSG_MISSING_ATTR} {resourceConfiguration}') 
		
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

		self.client = boto3.client('s3',
									aws_access_key_id=self.awsAccessKeyId,
									aws_secret_access_key=self.awsSecretAccessKey,
									region_name=self.region)
	

		return

	def execute(self ) :
		
		bRet = False
		logStr = f'[{self.ref}]'
		logger.info(f'{logStr}.Started')

		arn = f'arn:aws:s3:::{self.bucket_name}/{self.key}'
		self.setResourceConfiguration('arn',arn)

		response = self.client.put_object(
			Body=self.content, 
			Bucket=self.bucket_name, 
			Key=self.key
		)
		
		if (self.getHTTPStatusCodeOK(response) == False):
			raise Exception(f'{logStr} - Failed:{response}')
		
		logger.info(f'{logStr}.Done {arn}')
		
		if ( self.tags != None):
			logStr = f'{logStr}.Tags.Started'
			logger.info(f'{logStr}')
			response = self.client.put_object_tagging(
				Bucket=self.bucket_name,
				Key=self.key,
				Tagging={
					'TagSet': [{'Key': str(k), 'Value': str(v)} for k, v in self.new_tags.items()]
				}
			)
			
			if (self.getHTTPStatusCodeOK(response) == False ):
				raise Exception(f'{logStr} - Failed:{response}')

			self.setSuccess()
			
			logger.info(f'{logStr}.Tags.Done')
			
		return True


	def final(self ) -> bool:
		pass
import json
import boto3
import logging
from typing import Final
from handlers import *
import time
CONST_ERRMSG_MISSING_ATTR                    : Final[str]    = 'attribute not found in resource configuration'
							

logging.basicConfig(level=logging.INFO,format='%(asctime)s:%(levelname)s:[%(module)s.%(funcName)s]:%(message)s')
logger = logging.getLogger()

class FetchLambda( CloudAction):
	def init(self, configuration : dict, resourceConfiguration : dict  ) -> bool:
		self.action = "Fetch Lambda"
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

		self.stsClient = boto3.client('sts',
									aws_access_key_id=self.awsAccessKeyId,
									aws_secret_access_key=self.awsSecretAccessKey,
									region_name=self.region)

		self.accountId = self.stsClient.get_caller_identity()['Account']


	def execute( self ):
		#			 arn:aws:lambda:eu-north-1.  :905418456790.   :function:vw-vindolanda-uat-data-processor-generic
		self.arn = f'arn:aws:lambda:{self.region}:{self.accountId}:function:{self.id}'
		self.setResourceConfiguration('arn',self.arn)
		self.setSuccess()

	def final( self) :
		pass


class DeleteLambda( CloudAction):
	def init(self, configuration : dict, resourceConfiguration : dict  ) -> bool:
		
		
		self.action = "Delete Lambda"
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

		self.client = boto3.client('lambda',
									aws_access_key_id=self.awsAccessKeyId,
									aws_secret_access_key=self.awsSecretAccessKey,
									region_name=self.region)
		
	def execute( self ):
		
		logStr = f'[{self.ref}]'
		logger.info(f'{logStr}.Started')
		response = self.client.delete_function(FunctionName=self.id)
		if (self.getHTTPStatusCodeOK(response) == False):
			raise Exception(f'{logStr} Failed:{response}')

		self.setSuccess()
		logger.info(f'{logStr}.Done')

	def final( self) :
		pass

		
class CreateLambda( CloudAction):
	

	def init(self, configuration : dict, resourceConfiguration : dict  ) -> bool:
		
		#self.client = boto3.client('lambda')
		#self.stsClient = boto3.client('sts')

		self.action = "Create Lambda"
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
		
		bOK, self.sourceCodeBucket = self.getResourceConfiguration('sourceCodeBucket',None)
		if (bOK == False or self.sourceCodeBucket == None):
			raise ActionHandlerConfigurationException(f'sourceCodeBucket {CONST_ERRMSG_MISSING_ATTR} {resourceConfiguration}') 

		bOK, self.sourceCode = self.getResourceConfiguration('sourceCode',None)
		if (bOK == False or self.sourceCode == None):
			raise ActionHandlerConfigurationException(f'sourceCode {CONST_ERRMSG_MISSING_ATTR} {resourceConfiguration}') 

		bOK, self.runtime = self.getResourceConfiguration('runtime',None)
		if (bOK == False or self.runtime == None):
			raise ActionHandlerConfigurationException(f'runtime {CONST_ERRMSG_MISSING_ATTR} {resourceConfiguration}') 

		bOK, self.description = self.getResourceConfiguration('description','None')
		
		bOK, self.timeout = self.getResourceConfiguration('timeout',"30")
		if (bOK == False or self.timeout == None):
			raise ActionHandlerConfigurationException(f'timeout {CONST_ERRMSG_MISSING_ATTR} {resourceConfiguration}') 
		self.timeout = int(self.timeout)

		bOK, self.memorySize = self.getResourceConfiguration('memorySize',"128")
		if (bOK == False or self.memorySize == None):
			raise ActionHandlerConfigurationException(f'memorySize {CONST_ERRMSG_MISSING_ATTR} {resourceConfiguration}') 
		self.memorySize = int(self.memorySize)
				
		bOK, self.publish = self.getResourceConfiguration('publish',"False")
		if (bOK == False or self.publish == None):
			raise ActionHandlerConfigurationException(f'publish {CONST_ERRMSG_MISSING_ATTR} {resourceConfiguration}') 
			
		self.publish =  self.publish in ('y', 'yes', 't', 'true', 'True')

		bOK, self.handler = self.getResourceConfiguration('handler',None)
		if (bOK == False or self.handler == None):
			raise ActionHandlerConfigurationException(f'handler {CONST_ERRMSG_MISSING_ATTR} {resourceConfiguration}') 
		
		bOK, self.role = self.getResourceConfiguration('role',None)
		if (bOK == False or self.role == None):
			raise ActionHandlerConfigurationException(f'role {CONST_ERRMSG_MISSING_ATTR} {resourceConfiguration}') 
		logger.info(f'{self.role }')

		bOK, self.ephemeralStorage = self.getResourceConfiguration('ephemeralStorage',"512")
		if (bOK == False or self.ephemeralStorage == None):
			raise ActionHandlerConfigurationException(f'ephemeralStorage {CONST_ERRMSG_MISSING_ATTR} {resourceConfiguration}') 
		self.ephemeralStorage = int(self.ephemeralStorage)

		bOK, self.snapStart = self.getResourceConfiguration('snapStart',"None")
		if (bOK == False or self.snapStart == None):
			raise ActionHandlerConfigurationException(f'snapStart {CONST_ERRMSG_MISSING_ATTR} {resourceConfiguration}') 
		
		bOK, self.architectures = self.getResourceConfiguration('architectures',"arm64")
		if (bOK == False or self.architectures == None):
			raise ActionHandlerConfigurationException(f'architectures {CONST_ERRMSG_MISSING_ATTR} {resourceConfiguration}') 
		
		bOK, self.logFormat = self.getResourceConfiguration('logFormat',"Text")
		if (bOK == False or self.logFormat == None):
			raise ActionHandlerConfigurationException(f'logFormat {CONST_ERRMSG_MISSING_ATTR} {resourceConfiguration}') 
		
		bOK, self.applicationLogLevel = self.getResourceConfiguration('applicationLogLevel',"INFO")
		if (bOK == False or self.applicationLogLevel == None):
			raise ActionHandlerConfigurationException(f'applicationLogLevel {CONST_ERRMSG_MISSING_ATTR} {resourceConfiguration}') 

		bOK, self.systemLogLevel = self.getResourceConfiguration('systemLogLevel',"INFO")
		if (bOK == False or self.systemLogLevel == None):
			raise ActionHandlerConfigurationException(f'systemLogLevel {CONST_ERRMSG_MISSING_ATTR} {resourceConfiguration}') 
				
		bOK, self.logGroup = self.getResourceConfiguration('logGroup',None)
		if (bOK == False or self.logGroup == None):
			raise ActionHandlerConfigurationException(f'logGroup {CONST_ERRMSG_MISSING_ATTR} {resourceConfiguration}') 	
		
		bOK, self.layers = self.getResourceConfiguration('Layers',None)
		if (self.layers != None):
			self.new_layers = json.loads(self.layers) 
		
		bOK, self.environment = self.getResourceConfiguration('Environment',None)
		if (self.environment != None):
			self.new_environment = json.loads(self.environment) 
		
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

		self.client = boto3.client('lambda',
									aws_access_key_id=self.awsAccessKeyId,
									aws_secret_access_key=self.awsSecretAccessKey,
									region_name=self.region)

		self.stsClient = boto3.client('sts',
									aws_access_key_id=self.awsAccessKeyId,
									aws_secret_access_key=self.awsSecretAccessKey,
									region_name=self.region)

		self.accountId = self.stsClient.get_caller_identity()['Account']

		return

	def execute(self ) :
		
		logStr = f'[{self.ref}]'
		logger.info(f'{logStr},Started')

		response = self.client.create_function(
			FunctionName=self.id,
			Runtime=self.runtime,
			Role=self.role,
			Handler=self.handler,
			Code={
				'S3Bucket': self.sourceCodeBucket,
				'S3Key': self.sourceCode,
			},
			Description=self.description,
			Tags=self.new_tags,
			Timeout=self.timeout,
			Publish=self.publish,
			MemorySize=self.memorySize,
			PackageType='Zip',
			LoggingConfig={
				'LogFormat': self.logFormat,
				'LogGroup': self.logGroup
			},
			Architectures=[self.architectures],
			Layers=self.new_layers,
			EphemeralStorage={
				'Size': self.ephemeralStorage
			},
			SnapStart={
				'ApplyOn': self.snapStart
			}
		)

		#print(f'{json.dumps(response,indent=4)}')

		if (self.getHTTPStatusCodeOK(response) == False):
			raise Exception(f'{logStr} Failed:{response}')

		self.setResourceConfiguration('arn',response['FunctionArn'])
		self.setResourceConfiguration('codeSize',response['CodeSize'])
		self.setResourceConfiguration('codeSha256',response['CodeSha256'])
		self.setResourceConfiguration('state',response['State'])
		self.setResourceConfiguration('stateReason',response['StateReason'])
		self.setSuccess()
		logger.info(f'{logStr}.Done')
		return True

	def final(self ) -> bool:
		pass

	
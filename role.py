import json
import boto3
import logging
from handlers import *

CONST_ERRMSG_MISSING_ATTR                    : Final[str]    = 'attribute not found in resource configuration'

logging.basicConfig(level=logging.INFO,format='%(asctime)s:%(levelname)s:[%(module)s.%(funcName)s]:%(message)s')
logger = logging.getLogger()

class FetchRole( CloudAction):
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
		#			 arn:aws:iam::905418456790:role/vw-vindolanda-uat-dataprocessor-generic
		self.arn = f'arn:aws:iam::{self.accountId}:role/{self.id}'
		self.setResourceConfiguration('arn',self.arn)
		self.setSuccess()

	def final( self) :
		pass

class DeleteRole( CloudAction):

	def init(self, configuration : dict, resourceConfiguration : dict  ) -> bool:
				
		self.action = "Delete Role"

		#self.client = boto3.client('iam')
		#self.stsClient = boto3.client('sts')
		
		self.configuration = configuration
		self.resourceConfiguration = resourceConfiguration
		self.setFail()

		#self.accountId = self.stsClient.get_caller_identity()['Account']
		
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

		self.client = boto3.client('iam',
									aws_access_key_id=self.awsAccessKeyId,
									aws_secret_access_key=self.awsSecretAccessKey,
									region_name=self.region)

		self.stsClient = boto3.client('sts',
									aws_access_key_id=self.awsAccessKeyId,
									aws_secret_access_key=self.awsSecretAccessKey,
									region_name=self.region)

		self.accountId = self.stsClient.get_caller_identity()['Account']

		return

	def execute(self):
		
		logStr = f"[{self.ref}]"	
		logger.info(f'{logStr}.Started')
		response = self.client.delete_role(RoleName=self.id)

		if (self.getHTTPStatusCodeOK(response) == False):
			raise Exception(f'{logStr}  Failed:{response}')
		self.setSuccess()
		logger.info(f'{logStr}.Done')
		return		

	def final(self):
		pass



class CreateRole( CloudAction):

	def init(self, configuration : dict, resourceConfiguration : dict  ) -> bool:
		
			
		self.action = "Create Role"

		#self.client = boto3.client('iam')
		#self.stsClient = boto3.client('sts')
		#self.orgClient = boto3.client('organizations')
		self.configuration = configuration
		self.resourceConfiguration = resourceConfiguration

		self.setFail()

		#self.accountId = self.stsClient.get_caller_identity()['Account']
		
		bOK, self.ref = self.getResourceConfiguration('ref',None)
		if (bOK == False or self.ref == None):
			raise ActionHandlerConfigurationException(f'ref {CONST_ERRMSG_MISSING_ATTR} {resourceConfiguration}') 

		bOK, self.id = self.getResourceConfiguration('id',None)
		if (bOK == False or self.id == None):
			raise ActionHandlerConfigurationException(f'id {CONST_ERRMSG_MISSING_ATTR} {resourceConfiguration}') 
		
		bOK, self.delete = self.getResourceConfiguration('delete',"no")

		bOK, self.description = self.getResourceConfiguration('description',"None-Set")
		
		bOK, self.policy = self.getResourceConfiguration('Policy',None)
		if (self.policy != None):
			self.policies = json.loads(self.policy) 
		else:
			raise ActionHandlerConfigurationException(f'Policy {CONST_ERRMSG_MISSING_ATTR} {resourceConfiguration}') 

		bOK, self.tags = self.getResourceConfiguration('TagSet',None)
		if (self.tags != None):
			self.new_tags = json.loads(self.tags) 

		bOK, self.policyTemplate = self.getResourceConfiguration('PolicyRoleTemplate',None)
		if (bOK == False or self.policyTemplate == None):
			raise ActionHandlerConfigurationException(f'PolicyRoleTemplate {CONST_ERRMSG_MISSING_ATTR} {resourceConfiguration}') 
		else:
			self.policyTemplate = json.loads(self.policyTemplate)

		bOK, self.region = self.getResourceConfiguration('region',None)
		if (bOK == False or self.region == None):
			raise ActionHandlerConfigurationException(f'region {CONST_ERRMSG_MISSING_ATTR} {resourceConfiguration}') 

		bOK, self.awsSecretAccessKey = self.getResourceConfiguration('aws-secret-access-key',None)
		if (bOK == False or self.awsSecretAccessKey == None):
			raise ActionHandlerConfigurationException(f'aws-secret-access-key {CONST_ERRMSG_MISSING_ATTR} {resourceConfiguration}') 

		bOK, self.awsAccessKeyId = self.getResourceConfiguration('aws-access-key-id',None)
		if (bOK == False or self.awsAccessKeyId == None):
			raise ActionHandlerConfigurationException(f'aws-access-key-id {CONST_ERRMSG_MISSING_ATTR} {resourceConfiguration}') 

		self.client = boto3.client('iam',
									aws_access_key_id=self.awsAccessKeyId,
									aws_secret_access_key=self.awsSecretAccessKey,
									region_name=self.region)

		self.stsClient = boto3.client('sts',
									aws_access_key_id=self.awsAccessKeyId,
									aws_secret_access_key=self.awsSecretAccessKey,
									region_name=self.region)

		self.orgClient = boto3.client('organizations',
									aws_access_key_id=self.awsAccessKeyId,
									aws_secret_access_key=self.awsSecretAccessKey,
									region_name=self.region)

		self.accountId = self.stsClient.get_caller_identity()['Account']


		return

	def makeArn(self):
		#arn:aws:iam::905418456790:policy/vw-vindolanda-dev-dataprocessor-meteo-b
		#arn:aws:iam::<accountId>:policy/<id>
		return f'arn:aws:iam::{self.accountId}:policy/{self.id}'

	
			
	def createResource(self):

		logStr = f"[{self.ref}]"
		logger.info(f'{logStr}.Started')

		response = self.client.create_role(
				AssumeRolePolicyDocument=json.dumps(self.policyTemplate),
    			Path='/',
    			RoleName=self.id,
    			Description=self.description,
    			Tags=[{'Key': str(k), 'Value': str(v)} for k, v in self.new_tags.items()]
			)

		if (self.getHTTPStatusCodeOK(response) == False):
			raise Exception(f'{logStr} - Failed:{response}')

		arn = response['Role']['Arn']
		self.setResourceConfiguration('arn',arn)
		logger.info(f'{logStr}.Done :{arn}')

		return

	def updateResourceRolePolicy(self):
		logStr = f"[{self.ref}]"
		logger.info(f'{logStr}.Started')

		for k,v in self.policies.items():
			try:
				
				if v[:4] == "arn:":
					response = self.client.attach_role_policy(
					    RoleName=self.id,
					    PolicyArn=v
					)
					
					if (self.getHTTPStatusCodeOK(response) == False):
						raise Exception(f'{logStr} - Failed:{response}')

					logger.info(f'{logStr} -> {k}:{v} ')
				else:
					logger.warning(f'{logStr} -> No ARN see:{k}, ref:{v}')

			except ClientError as cErr:
				errCode, errMsg = self.getClientErrorDetails(cErr.response)	
				logger.warning(f'{logStr} - ClientError: {errCode}-{errMsg}')
		
			except Exception as eX:
				logger.error(f'{logStr} - Exception: {eX}')
		
		logger.info(f'{logStr}.Done')
		return

	def execute(self ) :
		self.createResource()
		self.updateResourceRolePolicy()
		self.setSuccess()
		return True


	def final(self ) -> bool:
		pass


class UpdateRole( CloudAction):

	def init(self, configuration : dict, resourceConfiguration : dict  ) -> bool:
				
		self.action = "Update Role"

		
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

		bOK, self.policy = self.getResourceConfiguration('Policy',None)
		if (self.policy != None):
			self.policies = json.loads(self.policy) 

		self.client = boto3.client('iam',
									aws_access_key_id=self.awsAccessKeyId,
									aws_secret_access_key=self.awsSecretAccessKey,
									region_name=self.region)

		self.stsClient = boto3.client('sts',
									aws_access_key_id=self.awsAccessKeyId,
									aws_secret_access_key=self.awsSecretAccessKey,
									region_name=self.region)

		self.accountId = self.stsClient.get_caller_identity()['Account']

		return

	def updateResourceRolePolicy(self):
		logStr = f"[{self.ref}]"
		logger.info(f'{logStr}.Started')

		for k,v in self.policies.items():
			try:
				
				if v[:4] == "arn:":
					response = self.client.attach_role_policy(
					    RoleName=self.id,
					    PolicyArn=v
					)
					
					if (self.getHTTPStatusCodeOK(response) == False):	
						raise Exception(f'{logStr} - Failed:{response}')

					logger.info(f'{logStr} -> {k}:{v} ')
				else:
					logger.warning(f'{logStr} -> No ARN see:{k}, ref:{v}')

			except ClientError as cErr:
				errCode, errMsg = self.getClientErrorDetails(cErr.response)	
				logger.warning(f'{logStr} - ClientError: {errCode}-{errMsg}')
		
			except Exception as eX:
				logger.error(f'{logStr} - Exception: {eX}')
		
		logger.info(f'{logStr}.Done')
		return

	def execute(self):
		
		logStr = f"[{self.ref}]"	
		logger.info(f'{logStr}.Started')
		self.updateResourceRolePolicy()
		self.setSuccess()
		logger.info(f'{logStr}.Done')
		return		

	def final(self):
		pass
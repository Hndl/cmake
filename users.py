from botocore.exceptions import ClientError
from typing import Final
import json
import boto3
import logging
from handlers import *
import string
import random

CONST_ERRMSG_MISSING_ATTR                    : Final[str]    = 'attribute not found in resource configuration'
	

logging.basicConfig(level=logging.INFO,format='%(asctime)s:%(levelname)s:[%(module)s.%(funcName)s]:%(message)s')
logger = logging.getLogger(__name__)

class DeleteUser( CloudAction):
	def init(self, configuration : dict, resourceConfiguration : dict  ) -> bool:
		
		
		#self.client = boto3.client('iam')
		self.action = "Delete User"
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

		self.client = boto3.client('iam',
									aws_access_key_id=self.awsAccessKeyId,
									aws_secret_access_key=self.awsSecretAccessKey,
									region_name=self.region)
			
	def deleteProfile(self):

		logStr = f'{self.ref}'
		logger.info(f'{logStr}.Started')
		
		response = self.client.delete_login_profile(
 	   		UserName=self.id
		)

		if (self.getHTTPStatusCodeOK(response) == False):
			raise Exception(f'{logStr} Failed:{response}')

		logger.info(f'{logStr}.Done')
		return

	def deleteAccessKeys( self, accessKeys) :
		logStr = f'{self.ref}'

		logger.info(f'{logStr}.Started')
		
		for accessKey in accessKeys:
			usr=accessKey['UserName']
			akey=accessKey['AccessKeyId']
			logger.info(f'{logStr} -> {usr}@{akey}')
			response = self.client.delete_access_key(
    			UserName=self.id,
    			AccessKeyId=akey
			)
			if (self.getHTTPStatusCodeOK(response) == False):
				raise Exception(f'{logStr} Failed:{response}')

		logger.info(f'{logStr}.Done')
		return

	def getAccessKeys(self):
		logStr = f'{self.ref}'
		logger.info(f'{logStr}.Started')

		response = self.client.list_access_keys(
    		UserName=self.id
		)

		if (self.getHTTPStatusCodeOK(response) == False):
			raise Exception(f'{logStr} Failed:{response}')

		logger.info(f'{logStr}.Done ')
		return response['AccessKeyMetadata']

	def execute( self ):
		
		logStr = f'{self.ref}'
		logger.info(f'{logStr}.Started')
			
		
		self.deleteAccessKeys(self.getAccessKeys())
		self.deleteProfile()

		response = self.client.delete_user(UserName=self.id)
		
		if (self.getHTTPStatusCodeOK(response) == False):
			raise Exception(f'{logStr} Failed:{response}')
		
		self.setSuccess()

		logger.info(f'{logStr}.Done')

	def final( self) :
		pass

			


class CreateUser( CloudAction):
	

	def init(self, configuration : dict, resourceConfiguration : dict  ) -> bool:
		
		
		#self.client = boto3.client('iam')
		self.action = "Create User"
		self.configuration = configuration
		self.resourceConfiguration = resourceConfiguration

		self.setFail()
		
		bOK, self.ref = self.getResourceConfiguration('ref',None)
		if (bOK == False or self.ref == None):
			raise ActionHandlerConfigurationException(f'ref {CONST_ERRMSG_MISSING_ATTR} {resourceConfiguration}') 

		bOK, self.id= self.getResourceConfiguration('id',None)
		if (bOK == False or self.id == None):
			raise ActionHandlerConfigurationException(f'id {CONST_ERRMSG_MISSING_ATTR} {resourceConfiguration}') 

		bOK, self.pwdcharset = self.getResourceConfiguration('pwdCharSet',None)
		if (bOK == False or self.pwdcharset == None):
			raise ActionHandlerConfigurationException(f'pwdcharset {CONST_ERRMSG_MISSING_ATTR} {resourceConfiguration}') 

		bOK, self.pwdLen = self.getResourceConfiguration('pwdLen',"8")
		if (bOK == False or self.pwdcharset == None):
			raise ActionHandlerConfigurationException(f'pwdLen {CONST_ERRMSG_MISSING_ATTR} {resourceConfiguration}') 
		self.pwdLen = int(self.pwdLen)
		
		bOK, self.tags = self.getResourceConfiguration('TagSet',None)
		if (self.tags != None):
			self.new_tags = json.loads(self.tags) 

		bOK, self.policies = self.getResourceConfiguration('Policies',None)
		if (self.tags != None):
			self.new_policies = json.loads(self.policies) 

		bOK, self.secret = self.getResourceConfiguration('secret',"No")

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
	

		return

	def charsequence_generator(self,len=6, charset=string.ascii_uppercase + string.digits):
		return 'I1.'.join(random.choice(charset) for _ in range(len-3))

	def attachProfile(self):
		
		logStr = f'{self.ref}'
		logger.info(f'{logStr}.Started')
		
		pwd = self.charsequence_generator(self.pwdLen,self.pwdcharset)
		
		response = self.client.create_login_profile(
			UserName=self.id,
    		Password=pwd,
    		PasswordResetRequired=True
		)

		if (self.getHTTPStatusCodeOK(response) == False):
			raise Exception(f'[{self.ref}][{self.action}@{self.region}] Failed:{response}')

		self.setResourceConfiguration('pwd',pwd)
		self.setResourceConfiguration('PasswordResetRequired',"yes")
		
		logger.info(f'{logStr}.Done')
		
		return
	
	def attachPolicies(self):
		logStr = f'{self.ref}'
		logger.info(f'{logStr}.Started')

		for policy in self.new_policies:
			logger.info(f'{logStr} - {policy}')
			response = self.client.attach_user_policy(
    			UserName=self.id,
    			PolicyArn=policy
			)
			if (self.getHTTPStatusCodeOK(response) == False):
				raise Exception(f'{logStr} Failed:{response}')

		logger.info(f'{logStr}.Done')
	def enableAccessKey(self):
		
		logStr = f'{self.ref}'
		logger.info(f'{logStr}.Started')
		
		response = self.client.create_access_key(
   			 UserName=self.id
		)

		if (self.getHTTPStatusCodeOK(response) == False):
			raise Exception(f'{logStr} Failed:{response}')

		self.setResourceConfiguration('AccessKeyId',response['AccessKey']['AccessKeyId'])
		self.setResourceConfiguration('status',response['AccessKey']['Status'])
		self.setResourceConfiguration('SecretAccessKey',response['AccessKey']['SecretAccessKey'])
		
		logger.info(f'{logStr}.Done')
		
		return

	def execute(self ) :
		
		logStr = f'{self.ref}'
		logger.info(f'{logStr}.Started')
	
		response = self.client.create_user(
		    UserName=self.id,
		    Tags=[{'Key': str(k), 'Value': str(v)} for k, v in self.new_tags.items()]
		)
		
		if (self.getHTTPStatusCodeOK(response) == False):
			raise Exception(f'{logStr} Failed:{response}')

		logger.info(f'{logStr}.Done')

		self.attachProfile()
		if ( self.secret in ("Yes","yes")) : 
			self.enableAccessKey()
		
		self.attachPolicies()
		self.setSuccess()
		return True

	def final(self ) -> bool:
		pass

	
from abc import ABC, abstractmethod
from types  import SimpleNamespace
from typing import Final
import json
import boto3
import re
import logging
from handlers import *

CONST_ERRMSG_MISSING_ATTR                    : Final[str]    = 'attribute not found in resource configuration'

logging.basicConfig(level=logging.INFO,format='%(asctime)s:%(levelname)s:[%(module)s.%(funcName)s.%(lineno)d]:%(message)s')
logger = logging.getLogger(__name__)

class FetchPolicy( CloudAction):
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

		
		self.client = boto3.client('iam',
									aws_access_key_id=self.awsAccessKeyId,
									aws_secret_access_key=self.awsSecretAccessKey,
									region_name=self.region)

		self.stsClient = boto3.client('sts',
									aws_access_key_id=self.awsAccessKeyId,
									aws_secret_access_key=self.awsSecretAccessKey,
									region_name=self.region)


		self.accountId = self.stsClient.get_caller_identity()['Account']

	def getPolicy(self) :

		logStr = f"[{self.ref}]"
		logger.info(f'{logStr}.Started')
		response = self.client.get_policy(PolicyArn = self.arn)

		#print(response)
		if (self.getHTTPStatusCodeOK(response) == False):
			raise Exception(f'{logStr} - Failed:{response}')

		self.defaultPolicyVersionId = response['Policy']['DefaultVersionId']
		self.setResourceConfiguration('defaultPolicyVersionId',self.defaultPolicyVersionId)
		logger.info(f'{logStr}.Done')

	def getDocument(self):
		logStr = f"[{self.ref}]"
		logger.info(f'{logStr}.Started')
		response = self.client.get_policy_version(
    				PolicyArn = self.arn, 
    				VersionId = self.defaultPolicyVersionId 
		)
		#print(response)
		self.defaultPolicyVersion = response['PolicyVersion']['Document']
		self.setResourceConfiguration('defaultPolicyVersion',self.defaultPolicyVersion)

		
		logger.info(f'{logStr}.Done')
	def execute( self ):
		#			
		self.arn = f'arn:aws:iam::{self.accountId}:policy/{self.id}'
		self.setResourceConfiguration('arn',self.arn)
		self.getPolicy()
		self.getDocument()
		self.setSuccess()

	def final( self) :
		pass

class DeletePolicy( CloudAction):
	def makeArn(self):
		#arn:aws:iam::905418456790:policy/vw-vindolanda-dev-dataprocessor-meteo-b
		#arn:aws:iam::<accountId>:policy/<id>
		return f'arn:aws:iam::{self.accountId}:policy/{self.id}'

	def init(self, configuration : dict, resourceConfiguration : dict  ) -> bool:
		
		self.action = "Delete Policy"
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

	def detach_user_policy(self, response):
		logStr = f"[{self.ref}]"
		logger.info(f'{logStr}.Started')
		if ( 'PolicyUsers' in response ):
			for user in response['PolicyUsers']:
				userName = user['UserName']
				logger.info(f'{logStr}.detach : {userName}')
				self.client.detach_user_policy(
			        PolicyArn=self.makeArn(),
			        UserName=userName
			    )
		logger.info(f'{logStr}.Done')
		return
		
	def detach_role_policy(self, response):
		logStr = f"[{self.ref}]"
		logger.info(f'{logStr}.Started')
		if ( 'PolicyRoles' in response ):
			for role in response['PolicyRoles']:
				roleName = role['RoleName']
				logger.info(f'{logStr}.detach : {roleName}')
				self.client.detach_role_policy(
			        PolicyArn=self.makeArn(),
			        RoleName=roleName
			    )
		logger.info(f'{logStr}.Done')
		return
		
	def detach_policy_dependenties(self):
		
		logStr = f"[{self.ref}]"
		logger.info(f'{logStr}.Started :{self.makeArn()}')
		
		response = self.client.list_entities_for_policy(
		    PolicyArn=self.makeArn()
		)

		if (self.getHTTPStatusCodeOK(response) == False):
			raise Exception(f'{logStr} - Failed:{response}')
		
		self.detach_role_policy(response)
		self.detach_user_policy(response)
		
		

		logger.info(f'{logStr}.Done' )
		return
	
	def deletePolicy(self):
		logStr = f"[{self.ref}]"
		logger.info(f'{logStr}.Started :{self.makeArn()}')

		response = self.client.delete_policy(
			PolicyArn=self.makeArn()
		)

		if (self.getHTTPStatusCodeOK(response) == False):
			raise Exception(f'{logStr} - Failed:{response}')

		logger.info(f'{logStr}.Done')
		return

	def execute(self ) :
		
		self.detach_policy_dependenties()
		self.deletePolicy()
		self.setSuccess()
		return True

	def final(self ) -> bool:
		pass




class CreatePolicy( CloudAction):

	def init(self, configuration : dict, resourceConfiguration : dict  ) -> bool:
		
		self.action = "Create Policy"
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
		
		bOK, self.template = self.getResourceConfiguration('Template',None)
		if (bOK == False or self.template == None):
			raise ActionHandlerConfigurationException(f'template {CONST_ERRMSG_MISSING_ATTR} {resourceConfiguration}') 
		else:
			self.template = json.loads(self.template)

		bOK, self.delete = self.getResourceConfiguration('delete',"no")

		bOK, self.description = self.getResourceConfiguration('description',"None-Set")

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

	def makeArn(self):
		#arn:aws:iam::905418456790:policy/vw-vindolanda-dev-dataprocessor-meteo-b
		#arn:aws:iam::<accountId>:policy/<id>
		return f'arn:aws:iam::{self.accountId}:policy/{self.id}'

	def createPolicy(self):
		logStr = f"[{self.ref}]"
		logger.info(f'{logStr}.Started')

		response = self.client.create_policy(
				PolicyName=self.id,
				PolicyDocument=json.dumps(self.template),
				Description=self.description,
				Tags=[{'Key': str(k), 'Value': str(v)} for k, v in self.new_tags.items()]
		)
		
		if (self.getHTTPStatusCodeOK(response) == False):
			raise Exception(f'{logStr} - Failed:{response}')

		arn = response['Policy']['Arn']
		self.setResourceConfiguration('arn',arn)
		logger.info(f'{logStr}.Done : {arn}')
		return

	def execute(self ) :
		
		self.createPolicy()
		self.setSuccess()
		return

	def final(self ) -> bool:
		pass


class UpdatePolicy( CloudAction):

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

		bOK, self.action = self.getResourceConfiguration('action',None)
		if (bOK == False or self.action == None):
			raise ActionHandlerConfigurationException(f'action {CONST_ERRMSG_MISSING_ATTR} {resourceConfiguration}') 

		

		if ( self.action.upper() == 'APPENDRESOURCE'):
			bOK, self.addresources = self.getResourceConfiguration('Resource',None)
			if (self.addresources != None):
				self.new_addresources = json.loads(self.addresources) 

		self.client = boto3.client('iam',
									aws_access_key_id=self.awsAccessKeyId,
									aws_secret_access_key=self.awsSecretAccessKey,
									region_name=self.region)

		self.stsClient = boto3.client('sts',
									aws_access_key_id=self.awsAccessKeyId,
									aws_secret_access_key=self.awsSecretAccessKey,
									region_name=self.region)

		self.accountId = self.stsClient.get_caller_identity()['Account']

		self.arn = f'arn:aws:iam::{self.accountId}:policy/{self.id}'
		self.setResourceConfiguration('arn',self.arn)

		return

	def getPolicy(self) :

		logStr = f"[{self.ref}]"
		logger.info(f'{logStr}.Started')
		response = self.client.get_policy(PolicyArn = self.arn)

		if (self.getHTTPStatusCodeOK(response) == False):
			raise Exception(f'{logStr} - Failed:{response}')

		self.defaultPolicyVersionId = response['Policy']['DefaultVersionId']
		self.policyId = response['Policy']['PolicyId']
		
		self.setResourceConfiguration('defaultPolicyVersionId',self.defaultPolicyVersionId)
		self.setResourceConfiguration('policyId',self.policyId)
		logger.info(f'{logStr}.Done')

	def getDocument(self):
		logStr = f"[{self.ref}]"
		logger.info(f'{logStr}.Started')
		response = self.client.get_policy_version(
    				PolicyArn = self.arn, 
    				VersionId = self.defaultPolicyVersionId 
		)
		if (self.getHTTPStatusCodeOK(response) == False):
			raise Exception(f'{logStr} - Failed:{response}')

		self.defaultPolicyVersion = response['PolicyVersion']['Document']
		self.setResourceConfiguration('defaultPolicyVersion',self.defaultPolicyVersion)

		
		logger.info(f'{logStr}.Done')

	def updateResourcePolicyDocumentResource(self):
		logStr = f"[{self.ref}]"
		logger.info(f'{logStr}.Started')
		i=len(self.defaultPolicyVersion['Statement'][0]['Resource'])
		for r in self.new_addresources:
			logger.info(f'{logStr}.[{i}]-{r}')
			self.defaultPolicyVersion['Statement'][0]['Resource'].append(r)
			i+=1
		
		
		logger.info(f'New Policy Version:\n{self.defaultPolicyVersion}')
		response = self.client.create_policy_version(
    		PolicyArn= self.arn,
    		PolicyDocument= json.dumps(self.defaultPolicyVersion),
    		SetAsDefault= True
		)

		if (self.getHTTPStatusCodeOK(response) == False):
			raise Exception(f'{logStr} - Failed:{response}')

		logger.info(f'{logStr}.Done')
		return

	def execute(self):
		
		logStr = f"[{self.ref}][{self.action}]"	
		logger.info(f'{logStr}.Started')

		if ( self.action.upper() == 'APPENDRESOURCE'):
			self.getPolicy()
			self.getDocument()
			self.updateResourcePolicyDocumentResource()
			self.setSuccess()

		
		
		logger.info(f'{logStr}.Done')
		return		

	def final(self):
		pass
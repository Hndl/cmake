#from abc import ABC, abstractmethod
#from types  import SimpleNamespace
#from typing import Final
#import re

from botocore.exceptions import ClientError
import json
import boto3
import logging
from handlers import *

logging.basicConfig(level=logging.INFO,format='%(asctime)s:%(levelname)s:[%(module)s.%(funcName)s.%(lineno)d]:%(message)s')
logger = logging.getLogger(__name__)


class DeleteRole( CloudAction):

	def init(self, configuration : dict, resourceConfiguration : dict  ) -> bool:
		logger.info(f'-In')
		try:
				
			self.action = "Delete Role"

			self.client = boto3.client('iam')
			self.stsClient = boto3.client('sts')
			
			self.configuration = configuration
			self.resourceConfiguration = resourceConfiguration

			self.accountId = self.stsClient.get_caller_identity()['Account']
			
			bOK, self.ref = self.getResourceConfiguration('ref',None)
			if (bOK == False or self.ref == None):
				raise ActionHandlerConfigurationException(f'ref attribute not found in resource configuration {resourceConfiguration}') 

			bOK, self.id = self.getResourceConfiguration('id',None)
			if (bOK == False or self.id == None):
				raise ActionHandlerConfigurationException(f'id attribute not found in resource configuration {resourceConfiguration}') 

		except ActionHandlerConfigurationException as ahceX:
			raise ahceX

		except ClientError as cErr:
			raise cErr

		except Exception as eX:
			raise eX
		logger.info(f'-Out')

	def execute(self):
		logger.info(f'-In')
		logStr = f"[{self.ref}][{self.accountId}][{self.action}] {self.id}"
			
		try:
			logger.info(f'{logStr}')
			response = self.client.delete_role(RoleName=self.id)

			if (self.getHTTPStatusCodeOK(response) == False):
				raise Exception(f'{logStr} - Failed:{response}')

			logger.info(f'{logStr} - Done')

		except ClientError as cErr:
			errCode, errMsg = self.getClientErrorDetails(cErr.response)	
			logger.warning(f'{logStr} - ClientError: {errCode}-{errMsg}')
			
		
		except Exception as eX:
			logger.error(f'{logStr} - Exception: {eX}')
			raise eX

		logger.info(f'-Out')
		
	def final(self):
		pass



class CreateRole( CloudAction):

	def init(self, configuration : dict, resourceConfiguration : dict  ) -> bool:
		logger.info(f'-In')
		try:
			
			self.action = "Create Role"

			self.client = boto3.client('iam')
			self.stsClient = boto3.client('sts')
			self.orgClient = boto3.client('organizations')
			self.configuration = configuration
			self.resourceConfiguration = resourceConfiguration

			self.accountId = self.stsClient.get_caller_identity()['Account']
			
			bOK, self.ref = self.getResourceConfiguration('ref',None)
			if (bOK == False or self.ref == None):
				raise ActionHandlerConfigurationException(f'ref attribute not found in resource configuration {resourceConfiguration}') 

			bOK, self.id = self.getResourceConfiguration('id',None)
			if (bOK == False or self.id == None):
				raise ActionHandlerConfigurationException(f'id attribute not found in resource configuration {resourceConfiguration}') 
			
			bOK, self.delete = self.getResourceConfiguration('delete',"no")

			bOK, self.description = self.getResourceConfiguration('description',"None-Set")
			
			bOK, self.policy = self.getResourceConfiguration('Policy',None)
			if (self.policy != None):
				self.policies = json.loads(self.policy) 
			else:
				raise ActionHandlerConfigurationException(f'Policy attribute not found in resource configuration {resourceConfiguration}') 

			bOK, self.tags = self.getResourceConfiguration('TagSet',None)
			if (self.tags != None):
				self.new_tags = json.loads(self.tags) 

			bOK, self.policyTemplate = self.getResourceConfiguration('PolicyRoleTemplate',None)
			if (bOK == False or self.policyTemplate == None):
				raise ActionHandlerConfigurationException(f'PolicyRoleTemplate attribute not found in resource configuration {resourceConfiguration}') 
			else:
				self.policyTemplate = json.loads(self.policyTemplate)

		except ActionHandlerConfigurationException as ahceX:
			raise ahceX

		except ClientError as cErr:
			raise cErr

		except Exception as eX:
			raise eX

		logger.info(f'-Out')

	def makeArn(self):
		#arn:aws:iam::905418456790:policy/vw-vindolanda-dev-dataprocessor-meteo-b
		#arn:aws:iam::<accountId>:policy/<id>
		return f'arn:aws:iam::{self.accountId}:policy/{self.id}'

	
			
	def createResource(self):

		logger.info(f'-In')

		logStr = f"[{self.ref}][{self.accountId}][{self.action}] {self.id}"
		logger.info(f'{logStr}')

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
		logger.info(f'{logStr} - Done {arn}')

		logger.info(f'-Out')

	def updateResource(self):
		logger.info(f'-In')
		logStr = f"[{self.ref}][{self.accountId}][{self.action}] {self.id}:Policy"
		logger.info(f'{logStr}')

		for k,v in self.policies.items():
			try:
				if v[:4] == "arn:":
					logger.info(f'{logStr}:{k}:{v}')
					
					response = self.client.attach_role_policy(
					    RoleName=self.id,
					    PolicyArn=v
					)
					
					if (self.getHTTPStatusCodeOK(response) == False):
						raise Exception(f'{logStr} - Failed:{response}')
				else:
					logger.warning(f'{logStr} - No ARN')

			except ClientError as cErr:
				errCode, errMsg = self.getClientErrorDetails(cErr.response)	
				logger.warning(f'{logStr} - ClientError: {errCode}-{errMsg}')
		
			except Exception as eX:
				logger.error(f'{logStr} - Exception: {eX}')
		
		logger.info(f'-Out')

	def execute(self ) :
		logger.info(f'-Imn')
		logStr = f"[{self.ref}][{self.accountId}][{self.action}] {self.id}"

		try:
			self.createResource()
			self.updateResource()

		except ClientError as cErr:
			errCode, errMsg = self.getClientErrorDetails(cErr.response)	
			logger.error(f'{logStr} - ClientError: {errCode}-{errMsg}')
			raise cErr
		except Exception as eX:
			logger.error(f'{logStr} - Exception: {eX}')
			raise eX
		
		logger.info(f'-Out')
		return True


	def final(self ) -> bool:
		logger.info(f'-In/Out')
		return True

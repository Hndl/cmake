from abc import ABC, abstractmethod
from types  import SimpleNamespace
from botocore.exceptions import ClientError
from typing import Final
import json
import boto3
import re
import logging
from handlers import *

logging.basicConfig(level=logging.INFO,format='%(asctime)s:%(levelname)s:[%(module)s.%(funcName)s.%(lineno)d]:%(message)s')
logger = logging.getLogger(__name__)

class DeletePolicy( CloudAction):
	def makeArn(self):
		#arn:aws:iam::905418456790:policy/vw-vindolanda-dev-dataprocessor-meteo-b
		#arn:aws:iam::<accountId>:policy/<id>
		return f'arn:aws:iam::{self.accountId}:policy/{self.id}'

	def init(self, configuration : dict, resourceConfiguration : dict  ) -> bool:
		logger.info(f'-In')
		try:
			self.action = "Delete Policy"
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

	def detach_policy_dependenties(self):
		logger.info(f'-In')
		logStr = f"[{self.ref}][{self.accountId}][{self.action}] {self.id}:{self.makeArn()} - detach where referenced"
		logger.info(f'{logStr}')
		try:
			response = self.client.list_entities_for_policy(
			    PolicyArn=self.makeArn()
			)
			if (self.getHTTPStatusCodeOK(response) == False):
				raise Exception(f'{logStr} - Failed:{response}')

			#print(f'{response}')
			if ( 'PolicyRoles' in response ):
				for role in response['PolicyRoles']:
					roleName = role['RoleName']
					logger.info(f'{logStr} : {roleName}')
					self.client.detach_role_policy(
				        PolicyArn=self.makeArn(),
				        RoleName=roleName
				    )
			else:
				logger.info(f'{logStr} - Not Referenced' )

		except ClientError as cErr:
			errCode, errMsg = self.getClientErrorDetails(cErr.response)	
			logger.warning(f'{logStr} - ClientError: {errCode}-{errMsg}')

		logger.info(f'{logStr} - Done' )
		logger.info(f'-Out')
	

	def execute(self ) :
		logger.info(f'-In')
		bRet = False
		logStr = f"[{self.ref}][{self.accountId}][{self.action}] {self.id}:{self.makeArn()}"
		try:
			self.detach_policy_dependenties()

			logger.info(f'{logStr}')

			response = self.client.delete_policy(
    			PolicyArn=self.makeArn()
			)

			if (self.getHTTPStatusCodeOK(response) == False):
				raise Exception(f'{logStr} - Failed:{response}')

			logger.info(f'{logStr} - Done')
			bRet = True

		except ClientError as cErr:
			errCode, errMsg = self.getClientErrorDetails(cErr.response)	
			if (errCode == 'NoSuchEntity'):
				logger.warning(f'{logStr} - ClientError: {errCode}-{errMsg}')
			else:
				logger.error(f'{logStr} - ClientError: {errCode}-{errMsg}')
				raise cErr
		
		except Exception as eX:
			logger.error(f'{logStr} - Exception: {eX}')
			raise eX

		logger.info(f'-Out')
		return bRet

	def final(self ) -> bool:
		logger.info(f'-In/Out')
		return True




class CreatePolicy( CloudAction):

	def init(self, configuration : dict, resourceConfiguration : dict  ) -> bool:
		logger.info(f'-In')
		try:
			self.action = "Create Policy"
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
			
			bOK, self.template = self.getResourceConfiguration('Template',None)
			if (bOK == False or self.template == None):
				raise ActionHandlerConfigurationException(f'template attribute not found in resource configuration {resourceConfiguration}') 
			else:
				self.template = json.loads(self.template)

			bOK, self.delete = self.getResourceConfiguration('delete',"no")

			bOK, self.description = self.getResourceConfiguration('description',"None-Set")
			

			bOK, self.tags = self.getResourceConfiguration('TagSet',None)
			if (self.tags != None):
				self.new_tags = json.loads(self.tags) 

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

	def execute(self ) :
		logger.info(f'-In')
		bRet = False
		logStr = f"[{self.ref}][{self.accountId}][{self.action}] {self.id}"
		try:
			
			
			logger.info(f'{logStr}')

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
			logger.info(f'{logStr} - Done {arn}')
			bRet = True
		except ClientError as cErr:
			errCode, errMsg = self.getClientErrorDetails(cErr.response)	
			logger.error(f'{logStr} - ClientError: {errCode}-{errMsg} \n Template:{json.dumps(self.template)}')
			raise cErr
		
		except Exception as eX:
			logger.error(f'{logStr} - Exception: {eX} \n  Template:{json.dumps(self.template)}')
			raise eX

		finally:
			if ( bRet == False):
				self.setResourceConfiguration('arn',self.makeArn())
				logger.warning(f'{logStr} - calculated arn value:{self.makeArn()}')
		
		logger.info(f'-Out')
		return bRet

	def final(self ) -> bool:
		logger.info(f'-In/Out')
		return True
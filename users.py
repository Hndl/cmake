#from abc import ABC, abstractmethod
#from types  import SimpleNamespace
from botocore.exceptions import ClientError
from typing import Final
import json
import boto3
#import re
import logging
from handlers import *
import string
import random

logging.basicConfig(level=logging.INFO,format='%(asctime)s:%(levelname)s:[%(module)s.%(funcName)s.%(lineno)d]:%(message)s')
logger = logging.getLogger(__name__)

class DeleteUser( CloudAction):
	def init(self, configuration : dict, resourceConfiguration : dict  ) -> bool:
		logger.info(f'-In')
		try:
			self.client = boto3.client('iam')
			self.action = "Delete User"
			self.configuration = configuration
			self.resourceConfiguration = resourceConfiguration
			
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

		except Exception as Ex:
			raise Ex

		logger.info(f'-Out')

	def deleteProfile(self):

		logStr = f'[{self.ref}][{self.action}@{self.id}] - Delete Profile'
		logger.info(f'{logStr}')
		
		response = self.client.delete_login_profile(
 	   		UserName=self.id
		)

		if (self.getHTTPStatusCodeOK(response) == False):
			raise Exception(f'{logStr} Failed:{response}')

		logger.info(f'{logStr} - Done')
		return

	def deleteAccessKeys( self, accessKeys) :
		logStr = f'[{self.ref}][{self.action}@{self.id}] - Delete Access Keys'
		logger.info(f'{logStr}')
		
		for accessKey in accessKeys:
			usr=accessKey['UserName']
			akey=accessKey['AccessKeyId']
			logger.info(f'{logStr} - {usr}@{akey}')
			response = self.client.delete_access_key(
    			UserName=self.id,
    			AccessKeyId=akey
			)
			if (self.getHTTPStatusCodeOK(response) == False):
				raise Exception(f'{logStr} Failed:{response}')
		logger.info(f'{logStr} - Done')
		return

	def getAccessKeys(self):
		logStr = f'[{self.ref}][{self.action}@{self.id}] - Get Access Keys'
		logger.info(f'{logStr}')
		response = self.client.list_access_keys(
    		UserName=self.id
		)

		if (self.getHTTPStatusCodeOK(response) == False):
			raise Exception(f'{logStr} Failed:{response}')

		logger.info(f'{logStr} - Done')
		return response['AccessKeyMetadata']

	def execute( self ):
		logger.info(f'-In')
		logStr = f'[{self.ref}][{self.action}@{self.id}]'
		try:
			
			logger.info(f'{logStr}')
			self.deleteAccessKeys(self.getAccessKeys())
			self.deleteProfile()

			response = self.client.delete_user(UserName=self.id)
			
			if (self.getHTTPStatusCodeOK(response) == False):
				raise Exception(f'{logStr} Failed:{response}')
			
			logger.info(f'{logStr} - Done')

		except ClientError as cErr:
			errCode, errMsg = self.getClientErrorDetails(cErr.response)
			if (errCode == 'NoSuchEntity'):
				logger.warning(f'{logStr} - ClientError:({errCode}-{errMsg})')
			else :
				logger.error(f'{logStr} - ClientError:({errCode}-{errMsg})')
				raise Exception ( f'AWS Exception:{errMsg}({errCode})')

		except Exception as eX:
			logger.error(f'{logStr} - Exception:{eX}')
			raise eX

		logger.info(f'-Out')

	def final( self) :
		pass

			


class CreateUser( CloudAction):
	

	def init(self, configuration : dict, resourceConfiguration : dict  ) -> bool:
		logger.info(f'-In')
		try:
			self.client = boto3.client('iam')
			self.action = "Create User"
			self.configuration = configuration
			self.resourceConfiguration = resourceConfiguration
			
			bOK, self.ref = self.getResourceConfiguration('ref',None)
			if (bOK == False or self.ref == None):
				raise ActionHandlerConfigurationException(f'ref attribute not found in resource configuration {resourceConfiguration}') 

			bOK, self.id= self.getResourceConfiguration('id',None)
			if (bOK == False or self.id == None):
				raise ActionHandlerConfigurationException(f'id attribute not found in resource configuration {resourceConfiguration}') 

			bOK, self.pwdcharset = self.getResourceConfiguration('pwdCharSet',None)
			if (bOK == False or self.pwdcharset == None):
				raise ActionHandlerConfigurationException(f'pwdcharset attribute not found in resource configuration {resourceConfiguration}') 

			bOK, self.pwdLen = self.getResourceConfiguration('pwdLen',"8")
			if (bOK == False or self.pwdcharset == None):
				raise ActionHandlerConfigurationException(f'pwdLen attribute not found in resource configuration {resourceConfiguration}') 
			self.pwdLen = int(self.pwdLen)
			
			bOK, self.tags = self.getResourceConfiguration('TagSet',None)
			if (self.tags != None):
				self.new_tags = json.loads(self.tags) 

		except ActionHandlerConfigurationException as ahceX:
			raise ahceX

		except ClientError as cErr:
			raise cErr

		except Exception as Ex:
			raise Ex

		logger.info(f'-Out')

	def charsequence_generator(self,len=6, charset=string.ascii_uppercase + string.digits):
		return ''.join(random.choice(charset) for _ in range(len))

	def attachProfile(self):
		logger.info(f'-In')
		logStr = f'[{self.ref}][{self.action}@{self.id}]:Attach Policy'
		logger.info(logStr)
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
		
		logger.info(f'{logStr} - Done')
		logger.info(f'-Out')
		return
		

	def enableAccessKey(self):
		logger.info(f'-In')
		logStr = f'[{self.ref}][{self.action}@{self.id}]:AccessKey'
		logger.info(logStr)
		response = self.client.create_access_key(
   			 UserName=self.id
		)

		if (self.getHTTPStatusCodeOK(response) == False):
			raise Exception(f'[{self.ref}][{self.action}@{self.region}] Failed:{response}')

		self.setResourceConfiguration('AccessKeyId',response['AccessKey']['AccessKeyId'])
		self.setResourceConfiguration('status',response['AccessKey']['Status'])
		self.setResourceConfiguration('SecretAccessKey',response['AccessKey']['SecretAccessKey'])
		
		logger.info(f'{logStr} - Done')
		logger.info(f'-Out')
		return

	def execute(self ) :
		
		logStr = f'[{self.ref}][{self.action}@{self.id}]'
		try:
			logger.info(logStr)
		
			response = self.client.create_user(
			    UserName=self.id,
			    Tags=[{'Key': str(k), 'Value': str(v)} for k, v in self.new_tags.items()]
			)
			
			if (self.getHTTPStatusCodeOK(response) == False):
				raise Exception(f'{logStr} Failed:{response}')

			logger.info(f'{logStr} - Done')

			self.attachProfile()

			self.enableAccessKey()

			logger.info(f'{logStr} - Done')

		except ClientError as cErr:
			errCode, errMsg = self.getClientErrorDetails(cErr.response)	
			logger.error(f'{logStr}- ClientError: {errCode}-{errMsg}')
			raise cErr
		
		except Exception as eX:
			logger.error(f'{logStr}- Exception: {eX}')
			raise eX
		
		
		return True

	def final(self ) -> bool:
		pass

	
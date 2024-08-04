#from abc import ABC, abstractmethod
#from types  import SimpleNamespace
#import re
#from typing import Final

from botocore.exceptions import ClientError
import json
import boto3
import logging
from handlers import *

logging.basicConfig(level=logging.INFO,format='%(asctime)s:%(levelname)s:[%(module)s.%(funcName)s.%(lineno)d]:%(message)s')
logger = logging.getLogger(__name__)

class DeleteFile(CloudAction):
	def init(self, configuration : dict, resourceConfiguration : dict  ) -> bool:
		logger.info(f'-In')
		try:
			self.client = boto3.client('s3')
			self.action = "Delete File"
			self.configuration = configuration
			self.resourceConfiguration = resourceConfiguration
			
			bOK, self.ref = self.getResourceConfiguration('ref',None)
			if (bOK == False or self.ref == None):
				raise ActionHandlerConfigurationException(f'ref attribute not found in resource configuration {resourceConfiguration}') 

			bOK, self.bucket_name = self.getResourceConfiguration('bucket',None)
			if (bOK == False or self.bucket_name == None):
				raise ActionHandlerConfigurationException(f'bucket attribute not found in resource configuration {resourceConfiguration}')

			bOK, self.key = self.getResourceConfiguration('key',None)
			if (bOK == False or self.key == None):
				raise ActionHandlerConfigurationException(f'key attribute not found in resource configuration {resourceConfiguration}')  
			
		except ActionHandlerConfigurationException as ahceX:
			raise ahceX

		except ClientError as cErr:
			raise cErr

		except Exception as eX:
			raise eX
		logger.info(f'-Out')

	def execute( self ):
		logger.info(f'-In')
		try:
			logStr = f'[{self.ref}][{self.action}@{self.bucket_name}/{self.key}]'
			logger.info(f'{logStr}')
			response = self.client.delete_object(Bucket=self.bucket_name, Key=self.key)
			logger.info(f'{logStr} - Done')

		except ClientError as cErr:
			errCode, errMsg = self.getClientErrorDetails(cErr.response)
			logger.error(f'{logStr} - ClientError:({errCode}-{errMsg})')
			raise Exception ( f'AWS Exception:{errorMessage}({errorCode})')

		except Exception as eX:
			logger.error(f'{logStr} - Exception:{eX}')
			raise eX

		logger.info(f'-Out')

	def final( self) :
		pass

class CreateFile( CloudAction):

	def init(self, configuration : dict, resourceConfiguration : dict  ) -> bool:

		try:
			logger.info(f'-In')
			self.client = boto3.client('s3')
			self.action = 'Create File'
			self.configuration = configuration
			self.resourceConfiguration = resourceConfiguration
			
			bOK, self.ref = self.getResourceConfiguration('ref',None)
			if (bOK == False or self.ref == None):
				raise ActionHandlerConfigurationException(f'ref attribute not found in resource configuration {resourceConfiguration}') 

			bOK, self.bucket_name = self.getResourceConfiguration('bucket',None)
			if (bOK == False or self.bucket_name == None):
				raise ActionHandlerConfigurationException(f'bucket attribute not found in resource configuration {resourceConfiguration}') 
			
			bOK, self.key = self.getResourceConfiguration('key',None)
			if (bOK == False or self.key == None):
				raise ActionHandlerConfigurationException(f'key attribute not found in resource configuration {resourceConfiguration}') 
			
			bOK, self.content = self.getResourceConfiguration('content',None)
			if (bOK == False or self.content == None):
				raise ActionHandlerConfigurationException(f'content attribute not found in resource configuration {resourceConfiguration}') 
			
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


	def execute(self ) :
		logger.info(f'-In')
		bRet = False
		logStr = f'[{self.ref}][{self.action}] @{self.bucket_name}/{self.key}'
		try:
			
			logger.info(f'{logStr}')

			response = self.client.put_object(
				Body=self.content, 
				Bucket=self.bucket_name, 
				Key=self.key
			)
			
			if (self.getHTTPStatusCodeOK(response) == False):
				raise Exception(f'{logStr} - Failed:{response}')
			
			arn = f'arn:aws:s3:::{self.bucket_name}/{self.key}'
			self.setResourceConfiguration('arn',arn)
			logger.info(f'{logStr} - Done {arn}')
			
			logStr = f'[{self.ref}][{self.action}] @{self.bucket_name}/{self.key} - Tags'
			logger.info(f'{logStr}')
			
			if ( self.tags != None):
				response = self.client.put_object_tagging(
					Bucket=self.bucket_name,
					Key=self.key,
					Tagging={
						'TagSet': [{'Key': str(k), 'Value': str(v)} for k, v in self.new_tags.items()]
					}
				)
				
				if (self.getHTTPStatusCodeOK(response) == False ):
					raise Exception(f'{logStr} - Failed:{response}')

				logger.info(f'{logStr} - Done')
				bRet = True

		except ClientError as cErr:
			errCode, errMsg = self.getClientErrorDetails(cErr.response)	
			logger.error(f'{logStr} - ClientError: {errCode}-{errMsg}')
			arn = f'arn:aws:s3:::{self.bucket_name}/{self.key}'
			self.setResourceConfiguration('arn',arn)
			logger.warning(f'{logStr} - calculated arn value:{arn}')
			raise cErr 

		except Exception as eX:
			logger.error(f'{logStr} - Exception: {eX}')
			raise eX

		finally:
			if ( bRet == False):
				arn = f'arn:aws:s3:::{self.bucket_name}/{self.key}'
				self.setResourceConfiguration('arn',arn)
				logger.warning(f'{logStr} - calculated arn value:{arn}')

		return bRet
		logger.info(f'-Out')

	def final(self ) -> bool:
		logger.info(f'-In/Out')
		return True

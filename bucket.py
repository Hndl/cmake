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

class DeleteBucket( CloudAction):
	def init(self, configuration : dict, resourceConfiguration : dict  ) -> bool:
		logger.info(f'-In')
		try:
			self.client = boto3.client('s3')
			self.action = "Delete Bucket"
			self.configuration = configuration
			self.resourceConfiguration = resourceConfiguration
			
			bOK, self.ref = self.getResourceConfiguration('ref',None)
			if (bOK == False or self.ref == None):
				raise ActionHandlerConfigurationException(f'ref attribute not found in resource configuration {resourceConfiguration}') 

			bOK, self.bucket_name = self.getResourceConfiguration('bucket',None)
			if (bOK == False or self.bucket_name == None):
				raise ActionHandlerConfigurationException(f'bucket attribute not found in resource configuration {resourceConfiguration}') 
			
		except ActionHandlerConfigurationException as ahceX:
			raise ahceX

		except ClientError as cErr:
			raise cErr

		except Exception as Ex:
			raise Ex
		logger.info(f'-Out')

	def execute( self ):
		logger.info(f'-In')
		try:
			logStr = f'[{self.ref}][{self.action}@{self.bucket_name}]'
			logger.info(f'{logStr}')
			response = self.client.delete_bucket(Bucket=self.bucket_name)
			logger.info(f'{logStr} - Done')

		except ClientError as cErr:
			errCode, errMsg = self.getClientErrorDetails(cErr.response)
			logger.error(f'{logStr} - ClientError:({errCode}-{errMsg})')
			raise Exception ( f'AWS Exception:{errMsg}({errCode})')

		except Exception as eX:
			logger.error(f'{logStr} - Exception:{eX}')
			raise eX

		logger.info(f'-Out')

	def final( self) :
		pass

			


class CreateBucket( CloudAction):
	

	def init(self, configuration : dict, resourceConfiguration : dict  ) -> bool:
		logger.info(f'-In')
		try:
			self.client = boto3.client('s3')
			self.action = "Create Bucket"
			self.configuration = configuration
			self.resourceConfiguration = resourceConfiguration
			
			bOK, self.ref = self.getResourceConfiguration('ref',None)
			if (bOK == False or self.ref == None):
				raise ActionHandlerConfigurationException(f'ref attribute not found in resource configuration {resourceConfiguration}') 

			bOK, self.bucket_name = self.getResourceConfiguration('id',None)
			if (bOK == False or self.bucket_name == None):
				raise ActionHandlerConfigurationException(f'id attribute not found in resource configuration {resourceConfiguration}') 
			
			bOK, self.region = self.getResourceConfiguration('region',None)
			if (bOK == False or self.region == None):
				raise ActionHandlerConfigurationException(f'region attribute not found in resource configuration {resourceConfiguration}') 
			
			bOK, self.acl = self.getResourceConfiguration('acl','private')
			bOK, self.dataRedundancy = self.getResourceConfiguration('dataRedundancy',"SingleAvailabilityZone")
			bOK, self.typeOfBucket = self.getResourceConfiguration('typeOfBucket',"Directory")
			bOK, self.objectOwnership = self.getResourceConfiguration('objectOwnership','BucketOwnerPreferred')
			bOK, self.delete = self.getResourceConfiguration('delete',"no")
			
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

	def updateResource(self):
		logger.info(f'-In')
		try:
			if ( self.tags != None):
				logger.info(f'[{self.ref}][{self.action}@{self.region}][Tags]')
				response = self.client.put_bucket_tagging(
					Bucket=self.bucket_name,
					Tagging={
						'TagSet': [{'Key': str(k), 'Value': str(v)} for k, v in self.new_tags.items()]
					}
				)
				
				if (self.getHTTPStatusCodeOK(response) == False ):
					raise Exception(f'[{self.ref}][{self.action}@{self.region}][Tags] - Failed:{response}')

				logger.info(f'[{self.ref}][{self.action}@{self.region}][Tags] - Done')

		except ClientError as cErr:
			errCode, errMsg = self.getClientErrorDetails(cErr.response)	
			logger.warning(f'[{self.ref}][{self.action}@{self.region}][Tags] - ClientError: {errCode} {errMsg}')
			
		except Exception as eX:
			logger.warning(f'[{self.ref}][{self.action}@{self.region}][Tags] - Exception: {eX}')
			
		logger.info(f'-Out')
		

	def execute(self ) :
		logger.info(f'-In')
		try:
			logger.info(f'[{self.ref}][{self.action}@{self.region}]')
		
			response = self.client.create_bucket(
			    ACL=self.acl,
			    Bucket=self.bucket_name,
			    CreateBucketConfiguration={
			        'LocationConstraint': self.region
			    }
			)
			
			if (self.getHTTPStatusCodeOK(response) == False):
				raise Exception(f'[{self.ref}][{self.action}@{self.region}] Failed:{response}')

			logger.info(f'[{self.ref}][{self.action}@{self.region}] - Done')

		except ClientError as cErr:
			errCode, errMsg = self.getClientErrorDetails(cErr.response)	
			logger.warning(f'[{self.ref}][{self.action}@{self.region}]- ClientError: {errCode}-{errMsg}')
		
		self.arn = f'arn:aws:s3:::{self.bucket_name}'

		self.setResourceConfiguration('arn',self.arn)
		
		logger.info(f'[{self.ref}][{self.action}@{self.region}] - Done {self.arn}')

		self.updateResource()
		
		logger.info(f'-Out')
		return True

	def final(self ) -> bool:
		logger.info(f'-In/Out')
		return True


	
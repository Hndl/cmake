from types  import SimpleNamespace
from typing import Final
from handlers import *

import json
import boto3
import logging

CONST_ERRMSG_MISSING_ATTR                    : Final[str]    = 'attribute not found in resource configuration'

logging.basicConfig(level=logging.INFO,format='%(asctime)s:%(levelname)s:[%(module)s.%(funcName)s.%(lineno)d]:%(message)s')
logger = logging.getLogger(__name__)

class DeleteBucket( CloudAction):
	def init(self, configuration : dict, resourceConfiguration : dict  ) -> bool:
		#self.client = boto3.client('s3')
		self.action = "Delete Bucket"
		self.configuration = configuration
		self.resourceConfiguration = resourceConfiguration

		self.setFail()
		
		bOK, self.ref = self.getResourceConfiguration('ref',None)
		if (bOK == False or self.ref == None):
			raise ActionHandlerConfigurationException(f'ref {CONST_ERRMSG_MISSING_ATTR} {resourceConfiguration}') 

		bOK, self.bucket_name = self.getResourceConfiguration('bucket',None)
		if (bOK == False or self.bucket_name == None):
			raise ActionHandlerConfigurationException(f'bucket {CONST_ERRMSG_MISSING_ATTR} {resourceConfiguration}') 

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

	def deleteBucket(self):
		logStr = f'[{self.ref}]'
		logger.info(f'{logStr}.Started')
		response = self.client.delete_bucket(Bucket=self.bucket_name)
		self.setSuccess()
		logger.info(f'{logStr}.Done')
		return

	def execute( self ):
		self.deleteBucket()
		

	def final( self) :
		pass

			


class CreateBucket( CloudAction):
	

	def init(self, configuration : dict, resourceConfiguration : dict  ) -> bool:
		
		#self.client = boto3.client('s3')
		self.action = "Create Bucket"
		self.configuration = configuration
		self.resourceConfiguration = resourceConfiguration

		self.setFail()
		
		bOK, self.ref = self.getResourceConfiguration('ref',None)
		if (bOK == False or self.ref == None):
			raise ActionHandlerConfigurationException(f'ref {CONST_ERRMSG_MISSING_ATTR} {resourceConfiguration}') 

		bOK, self.bucket_name = self.getResourceConfiguration('id',None)
		if (bOK == False or self.bucket_name == None):
			raise ActionHandlerConfigurationException(f'id {CONST_ERRMSG_MISSING_ATTR} {resourceConfiguration}') 
		
		bOK, self.acl = self.getResourceConfiguration('acl','private')
		bOK, self.dataRedundancy = self.getResourceConfiguration('dataRedundancy',"SingleAvailabilityZone")
		bOK, self.typeOfBucket = self.getResourceConfiguration('typeOfBucket',"Directory")
		bOK, self.objectOwnership = self.getResourceConfiguration('objectOwnership','BucketOwnerPreferred')
		bOK, self.delete = self.getResourceConfiguration('delete',"no")
		
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

	def updateResourceTags(self):
		logStr = f'[{self.ref}]'
		
		try:
			logger.info(f'{logStr}.Started')	
			if ( self.tags != None):
				
				response = self.client.put_bucket_tagging(
					Bucket=self.bucket_name,
					Tagging={
						'TagSet': [{'Key': str(k), 'Value': str(v)} for k, v in self.new_tags.items()]
					}
				)
				
				if (self.getHTTPStatusCodeOK(response) == False ):
					raise Exception(f'{logStr} - Failed:{response}')

			logger.info(f'{logStr}.Done')


		except Exception as eX:
			logger.warning(f'{logStr} - Exception {eX}')
			pass

		return

	def execute(self ) :
		
		logStr = f'[{self.ref}]'
		logger.info(f'{logStr}.Started')
	
		response = self.client.create_bucket(
		    ACL=self.acl,
		    Bucket=self.bucket_name,
		    CreateBucketConfiguration={
		        'LocationConstraint': self.region
		    }
		)
		
		if (self.getHTTPStatusCodeOK(response) == False):
			raise Exception(f'[{self.ref}][{self.action}@{self.region}] Failed:{response}')

		
		
		self.arn = f'arn:aws:s3:::{self.bucket_name}'
		self.setResourceConfiguration('arn',self.arn)
		
		logger.info(f'{logStr}.Done [{self.arn}]')
		self.updateResourceTags()

		self.setSuccess()
		
		return True

	def final(self ) -> bool:
		pass


	
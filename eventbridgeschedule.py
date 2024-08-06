import json
import boto3
import logging
from typing import Final
from handlers import *
import time
	
CONST_ERRMSG_MISSING_ATTR                    : Final[str]    = 'attribute not found in resource configuration'
							

logging.basicConfig(level=logging.INFO,format='%(asctime)s:%(levelname)s:[%(module)s.%(funcName)s]:%(message)s')
logger = logging.getLogger()

class DeleteEventBridgeSchedule( CloudAction):
	def init(self, configuration : dict, resourceConfiguration : dict  ) -> bool:
		
		self.client = boto3.client('events')
		self.action = "Delete EventBridge Schedule"
		self.configuration = configuration
		self.resourceConfiguration = resourceConfiguration
			
		bOK, self.ref = self.getResourceConfiguration('ref',None)
		if (bOK == False or self.ref == None):
			raise ActionHandlerConfigurationException(f'ref {CONST_ERRMSG_MISSING_ATTR} {resourceConfiguration}') 

		bOK, self.id = self.getResourceConfiguration('id',None)
		if (bOK == False or self.id == None):
			raise ActionHandlerConfigurationException(f'id {CONST_ERRMSG_MISSING_ATTR} {resourceConfiguration}') 

		bOK, self.targetId = self.getResourceConfiguration('targetId',None)
		if (bOK == False or self.targetId == None):
			raise ActionHandlerConfigurationException(f'targetId {CONST_ERRMSG_MISSING_ATTR} {resourceConfiguration}') 

			
	
	def deleteTarget(self):
		logStr = f'[{self.ref}]'
		logger.info(f'{logStr}.Started')
		response = self.client.remove_targets(
		    Rule=self.id,
		    Ids=[
		        self.targetId
		    ],
		    Force=True
		)
		if (self.getHTTPStatusCodeOK(response) == False):
			raise Exception(f'{logStr} Failed:{response}')
			
		logger.info(f'{logStr}.Done')
		return

	def deleteRule(self):
		logStr = f'[{self.ref}]'
		logger.info(f'{logStr}.Started')
		response = self.client.delete_rule(
		    Name=self.id,
		    Force=True
		)
		if (self.getHTTPStatusCodeOK(response) == False):
			raise Exception(f'{logStr} Failed:{response}')

		logger.info(f'{logStr}.Done')
		return

	def execute( self ):

		self.deleteTarget()
		self.deleteRule()
		

	def final( self) :
		pass

			


class CreateEventBridgeSchedule( CloudAction):
	

	def init(self, configuration : dict, resourceConfiguration : dict  ) -> bool:
		
		self.client = boto3.client('events')
		self.stsClient = boto3.client('sts')
		self.lmdClient = boto3.client('lambda')

		self.action = "Create EventBridge Schedule"
		self.configuration = configuration
		self.resourceConfiguration = resourceConfiguration

		self.accountId = self.stsClient.get_caller_identity()['Account']
		
		bOK, self.ref = self.getResourceConfiguration('ref',None)
		if (bOK == False or self.ref == None):
			raise ActionHandlerConfigurationException(f'ref {CONST_ERRMSG_MISSING_ATTR} {resourceConfiguration}') 

		bOK, self.id= self.getResourceConfiguration('id',None)
		if (bOK == False or self.id == None):
			raise ActionHandlerConfigurationException(f'id {CONST_ERRMSG_MISSING_ATTR} {resourceConfiguration}') 

		bOK, self.cron = self.getResourceConfiguration('cron',None)
		if (bOK == False or self.cron == None):
			raise ActionHandlerConfigurationException(f'cron {CONST_ERRMSG_MISSING_ATTR} {resourceConfiguration}') 

		bOK, self.region = self.getResourceConfiguration('region',None)
		
		bOK, self.description = self.getResourceConfiguration('description','None')

		bOK, self.status = self.getResourceConfiguration('status','DISABLED')

		bOK, self.eventBus = self.getResourceConfiguration('eventBus','default')	    
		
		bOK, self.target = self.getResourceConfiguration('Target',None)
		if (self.target != None):
			self.new_target = json.loads(self.target) 
		
		bOK, self.tags = self.getResourceConfiguration('TagSet',None)
		if (self.tags != None):
			self.new_tags = json.loads(self.tags) 

		return

	def putRule(self) : 
		logStr = f'[{self.ref}]'
		logger.info(f'{logStr}.Started')
		response = self.client.put_rule(
		    Name=self.id,
		    ScheduleExpression=self.cron,
		    State=self.status,
		    Description=self.description,
		    Tags=[{'Key': str(k), 'Value': str(v)} for k, v in self.new_tags.items()]
		)
		#print(f'PutRule\n{json.dumps(response,indent=4)}')
		if (self.getHTTPStatusCodeOK(response) == False):
			raise Exception(f'{logStr} Failed:{response}')

		self.ruleArn = response['RuleArn']
		self.setResourceConfiguration('arn',self.ruleArn)
		
		logger.info(f'{logStr}.Done')
		return


	def putTarget(self):
		logStr = f'[{self.ref}]'
		logger.info(f'{logStr}.Started')

		response = self.client.put_targets(
		    Rule=self.id,
		    Targets=[self.new_target]
		)
		#print(f'Rule Target\n{json.dumps(response,indent=4)}')
		if (self.getHTTPStatusCodeOK(response) == False):
			raise Exception(f'{logStr} Failed:{response}')

		logger.info(f'{logStr}.Done')
		return

	def attachRuleToLambda(self):
		logStr = f'[{self.ref}]'
		logger.info(f'{logStr}.Started')

		bOK, self.ruleArn = self.getResourceConfiguration('arn',None)
		bOK, self.function = self.getResourceConfiguration('function',None)

		response = self.lmdClient.create_event_source_mapping(
    		EventSourceArn=self.ruleArn,
    		FunctionName=self.function
    	)

		if (self.getHTTPStatusCodeOK(response) == False):
			raise Exception(f'{logStr} Failed:{response}')

		logger.info(f'{logStr}.Done')
		return
	
	def givePermission(self):

		logStr = f'[{self.ref}]'
		logger.info(f'{logStr}.Started')

		func_lambda_arn = self.new_target['Arn']
		response = self.lmdClient.add_permission(
            FunctionName=func_lambda_arn,
            StatementId=str(time.time())[-5:]+self.id,
            Action='lambda:InvokeFunction',
            Principal='events.amazonaws.com',
            SourceArn=self.ruleArn
        )

		if (self.getHTTPStatusCodeOK(response) == False):
			raise Exception(f'{logStr} Failed:{response}')

		logger.info(f'{logStr}.Done')

	def execute(self ) :
		self.putRule()
		self.putTarget()
		#self.attachRuleToLambda()
		self.givePermission()

		#print(f'{json.dumps(response,indent=4)}')

		return True

	def final(self ) -> bool:
		pass

	
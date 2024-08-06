from typing import Final
import json
import logging
from handlers import *
import time

CONST_ERRMSG_MISSING_ATTR                    : Final[str]    = 'attribute not found in resource configuration'
	

logging.basicConfig(level=logging.INFO,format='%(asctime)s:%(levelname)s:[%(module)s.%(funcName)s]:%(message)s')
logger = logging.getLogger()

class DeleteSleep( CloudAction ):
	def init(self, configuration : dict, resourceConfiguration : dict  ) -> bool:

		self.configuration = configuration
		self.resourceConfiguration = resourceConfiguration
		
		bOK, self.ref = self.getResourceConfiguration('ref',None)
		if (bOK == False or self.ref == None):
			raise ActionHandlerConfigurationException(f'ref {CONST_ERRMSG_MISSING_ATTR} {resourceConfiguration}') 

		bOK, self.description = self.getResourceConfiguration('description',None)
		if (bOK == False or self.description == None):
			raise ActionHandlerConfigurationException(f'description {CONST_ERRMSG_MISSING_ATTR} {resourceConfiguration}') 

		bOK, self.period = self.getResourceConfiguration('period',"30")
		if (bOK == False or self.period == None):
			raise ActionHandlerConfigurationException(f'period {CONST_ERRMSG_MISSING_ATTR} {resourceConfiguration}') 
		self.period = int(self.period)
			

	def execute( self ):
		
		logStr = f'{self.ref}'
		logger.info(f'{logStr}.Started : {self.description}')
		time.sleep(self.period) 
		logger.info(f'{logStr}.Done')

	def final( self) :
		pass


class CreateSleep( CloudAction):
	def init(self, configuration : dict, resourceConfiguration : dict  ) -> bool:
	
		self.configuration = configuration
		self.resourceConfiguration = resourceConfiguration
		
		bOK, self.ref = self.getResourceConfiguration('ref',None)
		if (bOK == False or self.ref == None):
			raise ActionHandlerConfigurationException(f'ref {CONST_ERRMSG_MISSING_ATTR} {resourceConfiguration}') 

		bOK, self.description = self.getResourceConfiguration('description',None)
		if (bOK == False or self.description == None):
			raise ActionHandlerConfigurationException(f'description {CONST_ERRMSG_MISSING_ATTR} {resourceConfiguration}') 

		bOK, self.period = self.getResourceConfiguration('period',"30")
		if (bOK == False or self.period == None):
			raise ActionHandlerConfigurationException(f'period {CONST_ERRMSG_MISSING_ATTR} {resourceConfiguration}') 
		self.period = int(self.period)
			

	def execute( self ):
		
		logStr = f'{self.ref}'
		logger.info(f'{logStr}.Started : {self.description}')
		time.sleep(self.period) 
		logger.info(f'{logStr}.Done')

	def final( self) :
		pass

			



	
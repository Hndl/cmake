from typing import Final
import json
import logging
from handlers import *
import time

CONST_ERRMSG_MISSING_ATTR                    : Final[str]    = 'attribute not found in resource configuration'
	

logging.basicConfig(level=logging.INFO,format='%(asctime)s:%(levelname)s:[%(module)s.%(funcName)s]:%(message)s')
logger = logging.getLogger()



class ReportNotes( CloudAction):
	def init(self, configuration : dict, resourceConfiguration : dict  ) -> bool:
	
		self.configuration = configuration
		self.resourceConfiguration = resourceConfiguration
		
		bOK, self.notes = self.getResourceConfiguration('Notes',None)
		if (self.notes != None):
			self.new_notes = json.loads(self.notes) 	

	def execute( self ):
		
		for note in self.new_notes:
			print(note)

	def final( self) :
		pass

			



	
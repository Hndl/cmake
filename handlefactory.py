#from abc import ABC, abstractmethod
#from types  import SimpleNamespace
#from botocore.exceptions import ClientError
#from typing import Final
#import json
#import boto3
#import re
import logging
from awsfile import *
from bucket import *
from role import *
from policy import *
from users import *
from loggroup import *
from awslambda import *
from eventbridgeschedule import *
from awssleep import *
from notes import *

logging.basicConfig(level=logging.INFO,format='%(asctime)s:%(levelname)s:[%(module)s.%(funcName)s.%(lineno)d]:%(message)s')
logger = logging.getLogger(__name__)

# DONE
# buckets : create done, delete done
# create files with specific content in target bucket/folder. done/ delete filed done
# policy creation/delete done
# role : create done
# role : delete done

# TODO:
# 

# log group
# lambda creation
# eventbridge schedule.


def cloudActionFactory ( action : str, command : str, configuration : dict, resourceConfiguration : dict ) -> CloudAction:

	availableHandlers= {
		'default:default': DefaultAction(),
		'Create:Bucket' : CreateBucket(), # Done
		'Delete:Bucket' : DeleteBucket(), # Done
		'Create:File' : CreateFile(), # Done
		'Delete:File' : DeleteFile(), # Done
		'Create:Policy': CreatePolicy(), # Done
		'Delete:Policy': DeletePolicy(), # Done
		'Create:Role' : CreateRole(), # Done
		'Delete:Role' : DeleteRole(), # Done
		'Create:User' : CreateUser(), # Done
		'Delete:User'  : DeleteUser(), # Done
		'Create:Loggroup' : CreateLoggroup(),
		'Delete:Loggroup' : DeleteLoggroup(),
		'Create:Lambda' : CreateLambda(),
		'Delete:Lambda' : DeleteLambda(),
		'Create:EventBridgeSchedule' : CreateEventBridgeSchedule(),
		'Delete:EventBridgeSchedule' : DeleteEventBridgeSchedule(),
		'Create:Sleep' : CreateSleep(),
		'Delete:Sleep' : DeleteSleep(),
		'Report:Notes' : ReportNotes()
	}
	
	if f'{action}:{command}' in availableHandlers:
		#print(f'cloudActionFactory:{action}:{command} - {action}:{command}')
		return availableHandlers[f'{action}:{command}']

	#print(f'cloudActionFactory:{action}:{command} - default')
	logging.warning(f'default handler selected for {action}:{command}')
	return availableHandlers['default']


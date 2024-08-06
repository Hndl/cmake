import boto3
import json
from typing import Final
from types  import SimpleNamespace
from abc import ABC, abstractmethod
from handlefactory import * 

logging.basicConfig(level=logging.INFO,format='%(asctime)s:%(levelname)s:[%(module)s.%(funcName)s.%(lineno)d]:%(message)s')
logger = logging.getLogger(__name__)

def loadConfiguration ( fname : str ) -> dict :
    with open(fname) as json_data:
        cfgJson = json.load(json_data)
        json_data.close()
    return cfgJson

def getClientErrorDetails(response):
    return response['Error']['Code'],response['Error']['Message']
    

def build_environment(  configuration : dict ) -> int :

    #config = SimpleNamespace(**configuration)

    #todo add error control
    #reuse function to do both delete and create.
    destroyResources(configuration)
   

    try:
        createResources(configuration)
    except Exception as eX:
        logger.error(eX)

   # TODO support accesskeys,region and secrety
   # TODO user to attach policy
   # Test Policies are being detached 
   # policys attached to user are not being deleted correctly.
def destroyResources( configuration : dict) -> int:
    errCount = 0
    for resourceItem in configuration['Delete'] :
        try:
            print(f"destroying {resourceItem['type']}:{resourceItem['ref']} - Started")
            handleResource('Delete',resourceItem['type'],configuration,resourceItem)
            print(f"destroying {resourceItem['type']}:{resourceItem['ref']} - Completed")
        except Exception as eX:
            logger.warning(eX)
            errCount+=1

    return errCount

def createResources( configuration : dict) -> int:
    for resourceItem in configuration['Create'] :
        print(f"build {resourceItem['type']}:{resourceItem['ref']} - Started")
        handleResource('Create',resourceItem['type'],configuration,resourceItem)
        print(f"build {resourceItem['type']}:{resourceItem['ref']} - Completed")
    
    return 0



def handleResource( action : str, command : str,  configuration : dict, resourceConfiguration : dict ) :
    cmdHandler = cloudActionFactory ( action , command, configuration, resourceConfiguration ) 
    cmdHandler.init( configuration, resourceConfiguration ) 
    cmdHandler.execute( )
    cmdHandler.final( )
    return 

def main () : 
    cfg=loadConfiguration('./vw-vin-qa.json')
    iResult = build_environment(  cfg)
    #print(json.dumps(cfg, indent=4))


# -- MAIN --
if __name__ == '__main__':
    main()

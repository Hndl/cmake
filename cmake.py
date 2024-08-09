import boto3
import json
from typing import Final
from types import SimpleNamespace
from abc import ABC, abstractmethod
from handlefactory import *
import argparse
import sys, traceback

CONST_CMDLINE_ARGREQUIRED   : Final[bool] = True

CONST_CMDLINE_LISTKEY_KEY        : Final[int]  = 0
CONST_CMDLINE_LISTKEY_NAME       : Final[int]  = 1
CONST_CMDLINE_LISTKEY_REQUIRED   : Final[int]  = 2
CONST_CMDLINE_LISTKEY_HELP       : Final[int]  = 3
CONST_CMDLINE_LISTKEY_DEFAULT    : Final[int]  = 4

CONST_ARG_PREFIX            : Final[str] = '-'
CONST_ARG_BLANK             : Final[str] = ''
CONST_ARG_Y_STR             : Final[list] = ['Y','YES']

CONST_BUILD_CREATE          : Final[str]  = 'Create'
CONST_BUILD_FETCH          : Final[str]  = 'Fetch'
CONST_BUILD_REPORT          : Final[str]  = 'Report'
CONST_BUILD_DELETE          : Final[str]  = 'Delete'
CONST_BUILD_UPDATE          : Final[str]  = 'Update'


CONST_CMDLINE_AWSACCESSKEY  : Final[list] = [ "-k", "--aws_access_key_id"       , CONST_CMDLINE_ARGREQUIRED, "aws access key id",CONST_ARG_BLANK]
CONST_CMDLINE_AWSSECRETKEY  : Final[list] = [ "-s", "--aws_secret_access_key"   , CONST_CMDLINE_ARGREQUIRED, "aws secret key",CONST_ARG_BLANK]
CONST_CMDLINE_AWSREGION     : Final[list] = [ "-r", "--region"                  , not(CONST_CMDLINE_ARGREQUIRED),"aws region",CONST_ARG_BLANK]
CONST_CMDLINE_VERBOSE       : Final[list] = [ "-v", "--verbose"                 , not(CONST_CMDLINE_ARGREQUIRED), "debug mode",False]
CONST_CMDLINE_FILE          : Final[list] = [ "-f", "--file"                    , CONST_CMDLINE_ARGREQUIRED, "build configuration file",CONST_ARG_BLANK]
CONST_CMDLINE_CLEAN          : Final[list] = [ "-C", "--clean_only"             , not(CONST_CMDLINE_ARGREQUIRED),"will execute the 'Delete' only portion of build file",CONST_ARG_BLANK]

CONST_CMD_ARGS              : Final[list] = [ CONST_CMDLINE_AWSACCESSKEY,
                                              CONST_CMDLINE_AWSSECRETKEY,
                                              CONST_CMDLINE_AWSREGION,
                                              CONST_CMDLINE_FILE,
                                              CONST_CMDLINE_VERBOSE,
                                              CONST_CMDLINE_CLEAN]


logging.basicConfig(level=logging.INFO,format="%(asctime)s:%(levelname)s:[%(module)s.%(funcName)s.%(lineno)d]:%(message)s")
logger = logging.getLogger(__name__)

def loadConfiguration(fname: str) -> dict:
    with open(fname) as json_data:
        cfgJson = json.load(json_data)
        json_data.close()
    return cfgJson


def getClientErrorDetails(response):
    return response["Error"]["Code"], response["Error"]["Message"]


def build_environment(configuration: dict,args) -> int:

    logger.info(f'Using Environment Configuration {args.file}')

    fetchResources(configuration, args)

    destroyResources(configuration,args)

    if ( args.clean_only.upper() in (CONST_ARG_Y_STR)):
        logger.info(f'No Build instructions to be executed')
        return

    try:
        createResources(configuration,args)
        updateResources(configuration,args)
    
    except Exception as eX:
        logger.error(eX)

    
    try:
        renderReport(configuration,args)
    except Exception as eX:
        logger.error(eX)



def setInternalVariables( configuration, args) : 
    configuration['Variables']['default-aws-secret-access-key']   = args.aws_secret_access_key
    configuration['Variables']['default-aws-access-key-id']       = args.aws_access_key_id
    configuration['Variables']['default-aws-region']              = args.region
    return

def enrichResourceConfiguration ( resourceConfiguration, args):
    resourceConfiguration['aws-access-key-id'] = args.aws_access_key_id
    resourceConfiguration['aws-secret-access-key'] = args.aws_secret_access_key
    return

def fetchResources(configuration: dict,args) -> int:
    
    errCount = 0

    if (CONST_BUILD_FETCH not in configuration):
        logger.warning(f'No Fetch Instructions')
        return errCount
    
    for resourceItem in configuration[CONST_BUILD_FETCH]:
        try:
            # add keys/secret to resourceItem
            logger.info(f'FETCHING\n{json.dumps(resourceItem,indent=4)}')
            enrichResourceConfiguration(resourceItem,args)
            handleResource(CONST_BUILD_FETCH, resourceItem["type"], configuration, resourceItem)
            logger.info(f'FETCHING\n{json.dumps(resourceItem,indent=4)}')

        except Exception as eX:
            logger.warning(eX)
            errCount += 1

    return errCount

def destroyResources(configuration: dict,args) -> int:
    errCount = 0
    if (CONST_BUILD_DELETE not in configuration):
        logger.warning(f'No Delete Instructions')
        return errCount

    for resourceItem in configuration[CONST_BUILD_DELETE]:
        try:
            # add keys/secret to resourceItem
            logger.info(f'DESTROYING\n{json.dumps(resourceItem,indent=4)}')
            enrichResourceConfiguration(resourceItem,args)
            handleResource("Delete", resourceItem["type"], configuration, resourceItem)
            
        except Exception as eX:
            logger.warning(eX)
            errCount += 1

    return errCount


def renderReport(configuration: dict,args) -> int:

    if (CONST_BUILD_REPORT not in configuration):
        logger.warning(f'No Report Instructions')
        return 0

    for resourceItem in configuration[CONST_BUILD_REPORT]:
        handleResource("Report", "Notes", configuration, resourceItem)
    return 0

def updateResources(configuration: dict, args) -> int:

    if (CONST_BUILD_UPDATE not in configuration):
        logger.warning(f'No Update Instructions')
        return 0

    for resourceItem in configuration[CONST_BUILD_UPDATE]:
        logger.info(f'BUILDING\n{json.dumps(resourceItem,indent=4)}')
        enrichResourceConfiguration(resourceItem,args)
        handleResource(CONST_BUILD_UPDATE, resourceItem["type"], configuration, resourceItem)
        logger.info(f'BUILDING\n{json.dumps(resourceItem,indent=4)}')
    return 0


def createResources(configuration: dict, args) -> int:
    if (CONST_BUILD_CREATE not in configuration):
        logger.warning(f'No Create Instructions')
        return 0

    for resourceItem in configuration[CONST_BUILD_CREATE]:
        logger.info(f'BUILDING\n{json.dumps(resourceItem,indent=4)}')
        enrichResourceConfiguration(resourceItem,args)
        handleResource("Create", resourceItem["type"], configuration, resourceItem)
        
    return 0


def handleResource( action: str, 
                    command: str, 
                    configuration: dict, 
                    resourceConfiguration: dict):

    cmdHandler = cloudActionFactory(
        action, command, configuration, resourceConfiguration
    )
    cmdHandler.init(configuration, resourceConfiguration)
    cmdHandler.execute()
    cmdHandler.final()
    return

def handle_cmdline_arguments( cmdLineArgs, argcfg ):
   
    for arg in argcfg:
        cmdLineArgs.add_argument(arg[CONST_CMDLINE_LISTKEY_KEY],
                                 arg[CONST_CMDLINE_LISTKEY_NAME],
                                 required=arg[CONST_CMDLINE_LISTKEY_REQUIRED],
                                 help=arg[CONST_CMDLINE_LISTKEY_HELP],
                                 default=arg[CONST_CMDLINE_LISTKEY_DEFAULT])
    
    return cmdLineArgs.parse_args()

def main(args):
    try:
        args = handle_cmdline_arguments(args,CONST_CMD_ARGS)
        if (args.verbose):
            logging.getLogger().setLevel(logging.DEBUG)

        cfg = loadConfiguration(args.file)
        
        setInternalVariables(cfg,args)

        iResult = build_environment(cfg, args)

        #print(f'{json.dumps(cfg,indent=4)}')

    except Exception as eX :
        logger.error(eX)

# -- MAIN --
if __name__ == "__main__":
    main(argparse.ArgumentParser())
    

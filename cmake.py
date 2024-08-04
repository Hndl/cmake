import boto3
import json
from typing import Final
from types  import SimpleNamespace
from abc import ABC, abstractmethod
from handlefactory import * 


def loadConfiguration ( fname : str ) -> dict :
    with open(fname) as json_data:
        cfgJson = json.load(json_data)
        json_data.close()
    return cfgJson



def build_environment(  configuration : dict ) -> int :

    config = SimpleNamespace(**configuration)

    for resourceItem in config.Create :
        resource = SimpleNamespace(**resourceItem)
        print(f'building {resource.type}:{resource.ref} - started')
        bRet, arnRef = handleResource('Create',resource.type,configuration,resourceItem)
        print(f'building {resource.type}:{resource.ref} - done')


def handleResource( action : str, command : str,  configuration : dict, resourceConfiguration : dict ) :
    cmdHandler = handlers.cloudActionFactory ( action , command, configuration, resourceConfiguration ) 
    cmdHandler.init(  configuration, resourceConfiguration ) 
    bResult, arnRef = cmdHandler.execute( configuration, resourceConfiguration )
    cmdHandler.final( )
    return bResult,arnRef

def main () : 
    cfg=loadConfiguration('./qa.json')
    iResult = build_environment(  cfg)
    print(json.dumps(cfg, indent=4))


# -- MAIN --
if __name__ == '__main__':
    main()

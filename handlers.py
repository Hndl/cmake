#from botocore.exceptions import ClientError
#import boto3

from abc import ABC, abstractmethod
from types  import SimpleNamespace
from typing import Final
import json
import re
import logging

CONST_BLANK                     : Final[str]    = ''
CONST_RX_REFERENCE              : Final[str]    = 'ref\\((.*?)\\)'
CONST_VX_REFERENCE              : Final[str]    = '%\\((.*?)\\)'
CONST_REF_ATTR_SPLIT_CHAR       : Final[str]    = ':'

logging.basicConfig(level=logging.INFO,format='%(asctime)s:%(levelname)s:[%(module)s.%(funcName)s.%(lineno)d]:%(message)s')
logger = logging.getLogger(__name__)

class ActionHandlerConfigurationException (Exception):
    pass

class CloudAction (ABC):

	def get_ref_nodes(self,d, keyAttr : str = 'ref',level : int = 0):
		if (isinstance(d,str)) : 
			return

		for key, value in d.items():
			if (isinstance(value,dict)) : 
				if (keyAttr in value):
					#print(f'^[{type(value)}]::{key} -> {value}')
					yield key, value
					level+=1
					yield from self.get_ref_nodes(value,level)

			if (isinstance(value,list)) :
				for i in value:
					if ( isinstance(i,dict)):
						if (keyAttr in i):
							#print(f'*[{type(i)}]::{key} -> {i}')
							yield key, i
					level+=1
					yield from self.get_ref_nodes(i,level)

	def getVariable( self,var : str, default : str) -> bool :

	    if (var in self.configuration['Variables']) :
	        return self.configuration['Variables'][var]
	    return default 

	def getReference( self, refs : dict,  default : str) -> bool :

		references = {} 
		for k,v in self.get_ref_nodes(self.configuration):
			for ref in refs:
				if ( v['ref'] == ref ):
					if ( refs[ref] in v):
						#print(f'FOUND {k}: {ref}.{refs[ref]} = {v[refs[ref]]}')
						references[ref] = {'field':refs[ref], 'value':v[refs[ref]] }
		#print(f'references are: {references}')	
		return references 

	def setResourceConfiguration( self, attr : str, val : str) -> bool : 
		self.resourceConfiguration[attr]=val
		logger.info(f'{attr} = {val}')
		return True

	def getResourceConfiguration( self, attr : str, default : str)  : 
		
		if attr not in self.resourceConfiguration:
			print(f'default value of "{default}" applied for attribute "{attr}"')
			return True,default

		val = self.resourceConfiguration[attr]
		if ( isinstance(val,dict) or isinstance(val,list)):
			val = json.dumps(val, indent=1)

		bRet, val2 = self.variableReplace(attr,val)
		bRet, val3 = self.referenceReplace(attr,val2)
		bRet, val4 = self.variableReplace(attr,val3)
		
		logger.info(f'{attr} = {val4}  default:{default}')
		return bRet, val4
	
	def variableReplace(self, attr,val):
		refs = self.hasReference(val,CONST_VX_REFERENCE,None)
		
		if ( len(refs) == 0):
			return True,val

		vars={}
		bFormedOK=True
		for ref in refs :
			#print(f'{ref}')	
			vars[ref]=self.getVariable(ref,"?")
			if vars[ref] == '?' : 
				bFormedOK = False
			else:
				val =val.replace(f'%({ref})',vars[ref])
			#print(f'resource configuration : {attr} --> {ref}->{vars[ref]} : {bFormedOK}  :: {val}')	

		return bFormedOK, val


	def referenceReplace(self, attr,val):
		refs = self.hasReference(val)
		
		if ( len(refs) == 0):
			return True,val
		refs = self.getReference(refs,"?")
		bFormedOK = True
		for ref in refs :
			sn = SimpleNamespace(**refs[ref])
			if sn.value == '?' :
				bFormedOK = False
			else:
				val =val.replace(f'ref({ref}:{sn.field})',sn.value)
			
			#print(f'resource configuration : {val} --> {ref}.{sn.field}={sn.value} : {bFormedOK}  :: {val}')	

		return bFormedOK, val
			
	def hasReference( self, val : str, regEx : str = CONST_RX_REFERENCE, ref_attr_split = CONST_REF_ATTR_SPLIT_CHAR) -> dict:

		refs = re.findall(regEx, val)
		if ( CONST_BLANK in refs):
			refs.remove( CONST_BLANK )

		if ref_attr_split != None :
			expandedRefs = {}
			for ref in refs:
				ref_list = ref.split(ref_attr_split)
				if ( len(ref_list) == 2):
					expandedRefs[ref_list[0]] = ref_list[1]
				else:
					print(f'warning - configuration issue with {ref}, no attr specified. ref ignored')
			return expandedRefs
		return refs

	def getHTTPStatusCode(self, response, meta : str = 'ResponseMetadata', status : str = 'HTTPStatusCode'):
		return response[meta][status]

	def getHTTPStatusCodeOK ( self,response ):
		httpStatusCode = self.getHTTPStatusCode(response)
		return httpStatusCode == 200 or httpStatusCode == 204

	def getClientErrorDetails(self,response):
		return response['Error']['Code'],response['Error']['Message']
			

	@abstractmethod
	def init(self, configuration : dict, resourceConfiguration : dict  ) -> bool:
		pass
	@abstractmethod
	def execute(self  ):
		pass
	@abstractmethod
	def final( self ) -> bool :
		pass

class DefaultAction (CloudAction):

	def init(self, configuration : dict, resourceConfiguration : dict  ) -> bool:
		return (False)
	def execute(self ) :
		return (False,'arn:false')
	def final( self ) -> bool :
		return (False)





def main():
	cfgJson=None
	with open('./qa.json') as json_data:
		cfgJson = json.load(json_data)
		json_data.close()

	

	#print(json.dumps(cfgJson, indent=4))

if __name__ == '__main__':
    main()


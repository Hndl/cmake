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
logger = logging.getLogger()

class ActionHandlerConfigurationException (Exception):
    pass

class CloudAction (ABC):

	def setFail(self):
		self.setResourceConfiguration('result',"Fail")

	def setSuccess(self):
		self.setResourceConfiguration('result',"Success")
			
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


	def xxgetReference( self, refs : dict,  default : str) -> bool :

		logger.debug(f'fetch refs {refs}')
		references = {} 
		for k,v in self.get_ref_nodes(self.configuration):
			for ref in refs:
				val=v['ref']

				logger.debug(f'compare : v:{val} == {ref} ')
				if ( v['ref'] == ref ):
					logger.debug(f'exists : {refs[ref] }? ')
					if ( refs[ref] in v):
						#print(f'FOUND {k}: {ref}.{refs[ref]} = {v[refs[ref]]}')
						logger.debug(f'match : {refs[ref] is {v[refs[ref]]} }? ')
						references[ref] = {'field':refs[ref], 'value':v[refs[ref]] }
		print(f'references are: {references}')	
		return references 


	def getReference( self, refs : dict,  default : str) -> bool :

		logger.debug(f'fetch refs {refs}')
		references = {} 
		for k,v in self.get_ref_nodes(self.configuration):
			for ref in refs:
				val=v['ref']
				compareRef=ref.split(':')[1]
				logger.debug(f'compare : v:{val} == {compareRef} ')
				if ( v['ref'] == compareRef ):
					logger.debug(f'exists : {refs[ref] }? ')
					if ( refs[ref] in v):
						#print(f'FOUND {k}: {ref}.{refs[ref]} = {v[refs[ref]]}')
						logger.debug(f'match : {refs[ref] is {v[refs[ref]]} }? ')
						references[ref] = {'field':refs[ref], 'value':v[refs[ref]] }
		logger.debug(f'references are: {json.dumps(references,indent=2)}')	
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
		logger.debug(f'var-replacement stage1:{json.dumps(val2,indent=4)}')
		bRet, val3 = self.referenceReplace(attr,val2)
		logger.debug(f'ref-replacement stage2:{json.dumps(val3,indent=4)}')
		bRet, val4 = self.variableReplace(attr,val3)
		logger.debug(f'var-replacement stage3:{json.dumps(val4,indent=4)}')
		
		return bRet, val4
	
	def variableReplace(self, attr,val):
		# Defect 20240802-1332-"None" should of been None.
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
		logger.debug(f'ref:{refs}')
		if ( len(refs) == 0):
			return True,val
		refs = self.getReference(refs,"?")
		bFormedOK = True
		for ref in refs :

			sn = SimpleNamespace(**refs[ref])
			logger.debug(f'replace ref:{ref} ->{sn.field} with {sn.value} ')
			if sn.value == '?' :
				bFormedOK = False
			else:
				strRef = ref.split(':')[1]
				#val =val.replace(f'ref({ref}:{sn.field})',sn.value)
				val =val.replace(f'ref({strRef}:{sn.field})',sn.value)
			
			#print(f'resource configuration : {val} --> {ref}.{sn.field}={sn.value} : {bFormedOK}  :: {val}')	

		return bFormedOK, val
			
	def hasReference( self, val : str, regEx : str = CONST_RX_REFERENCE, ref_attr_split = CONST_REF_ATTR_SPLIT_CHAR) -> dict:

		logger.debug(f'regex {regEx} split:{ref_attr_split} on {val}')
		refs = re.findall(regEx, val)
		logger.debug(f'refs:{refs}')
		if ( CONST_BLANK in refs):
			refs.remove( CONST_BLANK )

		if ref_attr_split != None :
			expandedRefs = {}
			i = 0
			for ref in refs:
				ref_list = ref.split(ref_attr_split)
				logger.debug(f'ref {ref} split into {ref_list} using delim {ref_attr_split}')
				if ( len(ref_list) == 2):

					logger.debug(f'[{i}]store {ref} split into {ref_list} using delim {ref_attr_split}')
					logger.debug(f'storge before {json.dumps(expandedRefs,indent=3)}')
					expandedRefs[f'{i}:{ref_list[0]}'] = ref_list[1]
					#expandedRefs[ref_list[0]] = ref_list[1]
					logger.debug(f'storge after {json.dumps(expandedRefs,indent=3)}')
					i+=1
				else:
					print(f'warning - configuration issue with {ref}, no attr specified. ref ignored')

			logger.debug(f'storge final {json.dumps(expandedRefs,indent=3)}')
			return expandedRefs

		return refs

	def getHTTPStatusCode(self, response, meta : str = 'ResponseMetadata', status : str = 'HTTPStatusCode'):
		return response[meta][status]

	def getHTTPStatusCodeOK ( self,response ):
		httpStatusCode = self.getHTTPStatusCode(response)
		return httpStatusCode == 200 or httpStatusCode == 204 or httpStatusCode == 201

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
		self.configuration = configuration
		self.resourceConfiguration = resourceConfiguration

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


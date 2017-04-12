#Developed by Puneet Tyagi 4/12/2017
#v1
# Reads host ip's or hostnames from a file and ping them to give a basix status.
import subprocess as sp #import check_output
import sys,time
import logging
from datetime import datetime
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool 
import re
codeDic={2:"UP",0:"CHECK HOST. DOWN OR SOME NETWORK ISSUE",1:"INTERMITTENT NETWORK CONNECTIVITY ISSUE:"}

logger_name='pingTest'
logger = logging.getLogger(logger_name)
logger.setLevel(logging.WARNING)
help="""
pingTest <IP File name> <Flag>
	<IP File name>: IP File must have each ip in a sepearte line . Any additional information about the host must be in same line seperated by commas.
	e.g. 127.0.0.1,myhost,used for xyz
	<Flag>	: 0 for DOWN Host
			: 1 for Host's with intermittent Network connectivity
			: 2 for UP hosts 
			: 3 All hosts""" 
# create the logging file handler
fh = logging.FileHandler("pingTest.log")
fs=logging.StreamHandler() 
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
fh.setFormatter(formatter)
fs.setFormatter(formatter) 
# add handler to logger object
logger.addHandler(fh)
logger.addHandler(fs)
	
def readFile(filename):
	try:
		file=open(filename)
		detailList=file.readlines()
		threadCount=len(detailList)
		detailDict={}
		for line in detailList:
			if line.strip()=="":
				continue
			else:
				item=line.split(",")
				detailDict[item[0].strip()]=item[1:]
			#detailDictList.append(dicitem)
		return (detailDict,threadCount)
	except :
		#logger.error("No Such File")
		logger.error(sys.exc_info()[1])
		sys.exit()

def pingHost(host):
	detailsList=[]
	if not re.search("\d+\.\d+\.\d+\.\d+",host):
		logger.warning("Ignoring invalid Ip Format: " +host)
		detailsList.append(10)
		detailsList.append("Invalid IP format")
		return {host:detailsList}
	else:	
		process=sp.Popen(["ping ",host.strip()],stdout=sp.PIPE,stderr=sp.STDOUT)
		rerurncode=process.wait()
		response=process.stdout.read().decode()
		#print("response is" ,response)
		sent=re.search("Sent = (\d+)",response).group(1)# if re.search("Sent = (/d+)",response)
		#print("sent is :", sent)
		received=re.search("Received = (\d+)",response).group(1)# if re.search("Received = (/d+)",response)
		lost=re.search("Lost = (\d+)",response).group(1)# if re.search("Lost = (/d+)",response)
		process.kill()
		
		if sent==received :
			detailsList.append(2)
			detailsList.append(codeDic[2])
			detailsList.append(response)
			return {host:detailsList}
		if received=='0' :
			detailsList.append(0)
			detailsList.append(codeDic[0])
			detailsList.append(response)
			return {host:detailsList}
		else :
			detailsList.append(1)
			detailsList.append(codeDic[1])
			detailsList.append(response+int(lost)/int(sent)+"% PACKET Loss")		
			return {host:detailsList}
	
def filterRes(pingResult,detailDict,flag):
	flag=int(flag)
	for result in pingResult:
		for k,v in result.items():
			if v[0]==flag or flag==3:
				print(k, " : ",detailDict[k]," : ", v[1])
			else:
				logger.debug("Set Flag: %d | Arg Flag: %s | Host : %s"%(v[0],flag,k))

def pingTest(filename,flag):
	
	detailDict,threadCount=readFile(filename)
	pool = ThreadPool(threadCount)
	hosts=detailDict.keys()
	pingResult=pool.map(pingHost,hosts)
	pool.close()
	pool.join()
	filterRes(pingResult,detailDict,flag)
	#print(pingResult)

def main():
	if len(sys.argv)==3:
		#print(help)
		filename=sys.argv[1]
		flag=sys.argv[2]
		pingTest(filename,flag)
	else:
		sys.exit(help)
	
if __name__=="__main__" :
	main()

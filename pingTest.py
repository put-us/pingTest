import subprocess as sp #import check_output
import sys,time
from datetime import datetime
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool 
import re
codeDic={2:"UP",0:"CHECK HOST. POSSIBLY DOWN OR SOME NETWORK ISSUE",1:"INTERMITTENT NETWORK CONNECTIVITY ISSUE:"}
def readFile(filename):
	file=open(filename)
	detailList=file.readlines()
	threadCount=len(detailList)
	detailDict={}
	for line in detailList:
		item=line.split(",")
		detailDict[item[0].strip()]=item[1:]
		#detailDictList.append(dicitem)
	return (detailDict,threadCount)

def pingHost(host):
	process=sp.Popen(["ping ",host.strip()],stdout=sp.PIPE,stderr=sp.STDOUT)
	rerurncode=process.wait()
	response=process.stdout.read().decode()
	#print("response is" ,response)
	sent=re.search("Sent = (\d+)",response).group(1)# if re.search("Sent = (/d+)",response)
	#print("sent is :", sent)
	received=re.search("Received = (\d+)",response).group(1)# if re.search("Received = (/d+)",response)
	lost=re.search("Lost = (\d+)",response).group(1)# if re.search("Lost = (/d+)",response)
	process.kill()
	detailsList=[]
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
	
def filterRes(pingResult,detailDict,flag=3):
	for result in pingResult:
		for k,v in result.items():
			if v[0]==flag or flag==3:
				print(k, " : ",detailDict[k]," : ", v[1])
	

def pingTest():
	
	detailDict,threadCount=readFile("IP.txt")
	pool = ThreadPool(threadCount)
	hosts=detailDict.keys()
	pingResult=pool.map(pingHost,hosts)
	#reduced=[port for port in open_ports if port>1]
	pool.close()
	pool.join()
	filterRes(pingResult,detailDict)
	#print(pingResult)
	
pingTest()
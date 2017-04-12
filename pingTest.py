#Developed by Puneet Tyagi 4/12/2017
#v1
# Reads host ip's or hostnames from a file and ping them to give a basix status.
import subprocess as sp #import check_output
import sys,time
from datetime import datetime
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool 
import re
codeDic={2:"UP",0:"CHECK HOST. DOWN OR SOME NETWORK ISSUE",1:"INTERMITTENT NETWORK CONNECTIVITY ISSUE:"}
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
	
def filterRes(pingResult,detailDict,flag):
	for result in pingResult:
		for k,v in result.items():
			if v[0]==flag or flag==3:
				print(k, " : ",detailDict[k]," : ", v[1])
	

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
	filename=sys.argv[1]
	flag=sys.argv[2]
	pingTest(filename,flag=0)
	
if __name__=="__main__" :
	main()

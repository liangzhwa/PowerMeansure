import threading
import time
import datetime
import PT_client as client

def RunMeansureWithDuration(duration,newFileName):  
    status = client.MeansurePowerWithDuration(duration,newFileName)
    
def RunMeansureStart():  
    status = client.StartMeansurePower()
    
def RunMeansureEnd(index,newFileName):  
    status = client.EndMeansurePower(newFileName)

def MeansureWithDuration(duration,newFileName):
    thread = threading.Thread(target=RunMeansureWithDuration, args=(duration,newFileName))
    thread.start()
    
def MeansureStart():
    thread = threading.Thread(target=RunMeansureStart, args=())
    thread.start()
    
def MeansureEnd(index,newFileName):
    thread = threading.Thread(target=RunMeansureEnd, args=(index,newFileName))
    thread.start()
    
if __name__ == "__main__":
    print 'start:', datetime.datetime.now()
    tempReportPath="c:/temp/testcase/test6.csv"
    #start measure
    MeansureStart()
    time.sleep(4)
    
    #end measure:  first arg is for multi thread, second arg is the report path
    MeansureEnd(0,tempReportPath)
    print 'end:', datetime.datetime.now()
    
    #messure with duration
    ##RunMeansureWithDuration(4,tempReportPath)
    print "OK?"
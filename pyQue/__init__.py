def isfile(cfgpath):
    import os
    return os.path.isfile(cfgpath)


def checkrights(cfgpath, campaign_type):
    import os
    #verify that these are correct.
    requiredFiles = {"lift":["cfg.json","hhcounts_model.csv","orig.csv","origHead.csv"],"ondemand" : ["cfg.json","hhcounts_model.csv","orig.csv","origHead.csv"],"samsclub" : ["cfg.json","hhcounts_model.csv","orig.csv","origHead.csv"],"out": ["cfg.json","hhcounts_model.csv","orig.csv","origHead.csv"]}
    cfgDir = os.path.dirname(cfgpath)
    if len(set(os.listdir(cfgDir)) & set(requiredFiles[campaign_type])) == len(requiredFiles[campaign_type]):
        return True
    else:
        print("Ensure you have all required files in this directory")
        return False


def writeAccessTest(cfgpath):
    import os
    cfgDir = os.path.dirname(cfgpath)
    try:
        f = open(cfgDir+"/accessTest.txt", "w")
        f.close()
        os.remove(cfgDir+"/accessTest.txt")
        return True
    except:
        print("Need permission to write scored files in directory "+cfgDir)
        return False



def quetask(cfgpath):
    import json, os, logging
    #create log
    logger = logging.getLogger('onDemand')
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler(os.path.dirname(cfgpath)+"/onDemand.log")
    fh.setLevel(logging.INFO)
    logger.addHandler(fh)
    ###CHECKS BEFORE QUEING###
    #check that cfgpath exists
    if not isfile(cfgpath):
        logger.warning(cfgpath+" DOES NOT EXIST.  Check location of file.")
        return(cfgpath+" DOES NOT EXIST.  Check location of file.")
        
    #check that cfgDir contains all necessary files
    json1_file = open(cfgpath)
    json1_str = json1_file.read()
    json1_data = json.loads(json1_str)
    campaign_type = json1_data["campaign_type"].lower()
    if not checkrights(cfgpath,campaign_type):
        logger.warning("Ensure you have all required files in this cfg directory.")
        return("Ensure you have all required files in this cfg directory.")
    
    #check that we have rwx to cfgDir    
    if not writeAccessTest(cfgpath):
        logger.warning("Need permission to write scored files in "+os.path.dirname(cfgpath))
        return("Need permission to write scored files in "+os.path.dirname(cfgpath))
    
    logger.info("Passed initial que tests, ready to add to que.")
    ###READY TO QUE###
    directoryDict = {"lift": "LIFT", "ondemand": "light", "samsclub": "SamsClub", "out": "out"}
    prefixDict = {"lift": "10", "ondemand":"20", "samsclub":"30", "out":"40"}
    subDir = directoryDict[campaign_type]    
    ####for now, assume we are in julia prod. will need to figure out dev/UAT late
    quePath = "/mapr/mapre04p/analytics0001/analytic_users/prod/julia/que/"+subDir+"/"
    
    listDir = os.listdir(quePath)
    for i in range(len(listDir)):
        listDir[i] = int(listDir[i].split(".")[0])
    
    tid = max(listDir) +1
    f = open(quePath+str(tid)+".ready", "w")
    f.write("/".join(cfgpath.split("/")[0:-1]))
    os.chmod(quePath+str(tid)+".ready", 0o777)
    f.close()
    
    returnTid = int(prefixDict[campaign_type] + str(tid))
    logger.info("Task successfully queued.  TaskID: "+str(returnTid))
    return returnTid


def statusPoll(tid):
    import os
    subDirDict = {"10":"LIFT", "20":"light", "30":"SamsClub", "40":"out"}
    #parse first 2 digits off to know which que to check
    subDir = subDirDict[str(tid)[0:2]]
    quePath = "/mapr/mapre04p/analytics0001/analytic_users/prod/julia/que/"+subDir+"/"
    listDir = os.listdir(quePath)
    for i in range(len(listDir)):
        if listDir[i].split(".")[0] == str(tid)[2:]:
            print(listDir[i].split(".")[1])

#!/usr/bin/python
import json
import sys
import getopt
import copy
import time
from pprint import pprint
import re

#Read an automation config and extend it with a second shard on same hosts as
#Original - NOT SOMETHIGN YOU SHOULD DO - in any normal case.

autoconfigfile = ""

def logmsg(x):
    #pprint(x)
    pass

def print_usage_message():
       print ("usage: " + sys.argv[0] + "  [-h,--help] [-c,--config CurrentConfig] ")

def parse_args(argv):
 
   global autoconfigfile
   try:
      opts, args = getopt.getopt(argv,"c:h",["config=","help"])
   except getopt.GetoptError:
      print_usage_message()
      sys.exit(2)


   for opt, arg in opts:
      if opt == '-h':
        print_usage_message()
        sys.exit()
      elif opt in ("-c", "--config"):
         autoconfigfile = arg
    
   if autoconfigfile == "":
      print("You must specify an input config")
      sys.exit(1)

def read_existing(name):
   with open(autoconfigfile) as autofile:
      data = json.load(autofile)
   return data



def add_shards(config,nnewshards):
    sharding = config['sharding']
    shards = sharding[0]['shards']
    firstshard = shards[0]
    nshards = len(shards)
    logmsg( "Cluster currently has " + str(nshards) + " shards")
    shardname = firstshard['_id'].split('_')[0]
    logmsg( "Prefix = " + shardname)

    #Find highest port for each host
    processes = config['processes']
   

    hosts = {}
    mongodhosts = {}
    newprocesses = []
    for p in processes:
        hostname = p['hostname']
        port = p["args2_6"]["net"]["port"]
        if hostname in hosts:
            if port > hosts[hostname]:
                hosts[hostname]=port
        else:
            hosts[hostname]=port

        #Which have a mongod on - no install with mongos!
        if p['processType'] == "mongod":
            #verify its not a config server
            isconfig = False
            try:
                if  p['args2_6']['sharding']['clusterRole'] == 'configsvr':
                   isconfig = True
            except:
                pass
            #in case we have dedicated config server hosts
            if isconfig == False:
                mongodhosts[hostname] = True
                example_mongod = p

   #Add Processes for our new shards
    host = 0
    oneup =  0
    newrepsets=[]
    stime = int(time.time())
    newshards = []
    for s in range(0,nnewshards):

        shardno = nshards + s 
        logmsg("Adding shard " + str(shardno))
        repsetmembers = []
        for r in range(0,3):
            newprocess = copy.deepcopy(example_mongod)
            newname = shardname+"_"+str(shardno)+"_"+str(stime)+"_"+str(oneup)
          
            hostname = list(mongodhosts)[host]
           

            port = hosts[hostname]+1
            hosts[hostname]=port
           
            oneup=oneup+1
            host=(host+1) % len(mongodhosts)
            dbpath = example_mongod['args2_6']['storage']['dbPath']
            matchObj = re.match(r'^(.*/)',dbpath)
            if matchObj == None:
                logmsg("Could not extract dbpath")
                exit(1)
            dbpath = matchObj.group(1)+newname
        
            replsetname = shardname+"_"+str(shardno)

            newprocess['args2_6']['net']['port'] = port
            newprocess['args2_6']['replication']['replSetName']=replsetname
            newprocess['args2_6']['storage']['dbPath'] = dbpath
            #DIFFERENT FOR EBPI (TODO)
            newprocess['args2_6']['systemLog']['path'] = dbpath + "/mongodb.log"
            newprocess['hostname'] = hostname
            newprocess['name'] = newname
            newprocesses.append(newprocess)
            logmsg(newprocess)

            if r == 2:
                isArbiter =True
            else:
                isArbiter = False

            repsetconfig = { "_id" : r,
                             "arbiterOnly" : isArbiter,
                             "hidden" : False,
                             "priority" : 1.0,
                             "slaveDelay": 0,
                             "votes" : 1,
                             "host" : newname }
             
            repsetmembers.append(repsetconfig)
          

        newrepsets.append({"_id":shardname+"_"+str(shardno),
                          "members" : repsetmembers})
        newshards.append({"_id":shardname+"_"+str(shardno),
                          "rs" : shardname+"_"+str(shardno),
                          "tags" : []
                          })  
    logmsg(newrepsets)

    #Now add all this
    for p in newprocesses:
        config['processes'].append(p)

    for r in newrepsets:
        config['replicaSets'].append(r)

    for s in newshards:
        config["sharding"][0]["shards"].append(s)


    logmsg(config['sharding'])
    print(json.dumps(config ,indent=4, separators=(',', ': ')))

if __name__ == "__main__": 
   logmsg("Reads an automation config and modifies it as needed")
   parse_args(sys.argv[1:])
   existing = read_existing(autoconfigfile)
   add_shards(existing,3)


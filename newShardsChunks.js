db=db.getSiblingDB("objStore")
sh.setBalancerState(false);

print("WARNING: This must either be run when no writes are")
print("happening OR set to a suitably large time after the ")
print("last write date!")

nshards = 3
lowestnewshard = 3

totalprefixes=100
pfxpershard = totalprefixes/nshards

startwhen = 120 // In 2 minutes - so we see 'most move over
                //Generator puts a 5 minute gap between runs anyway
nshardkeys = 100


print("Checking for newest record in the Database")
//Verify we do not have any chunks with higher ID's
maxid = ObjectId()
for(x=0;x<nshardkeys;x++){
	print("Shardkey "+x+" of "+nshardkeys)
	query = {_id:{$lt:{s:x+1}}}
	sort = {_id:-1}
	
	c = db.blobs.find(query,{_id:1}).sort(sort).limit(1).next()
	
	id = c['_id']['i']
	if(id > maxid)
	{
		printjson(id.getTimestamp())
		maxid = id
	}
	c = db.references.find(query,{_id:1}).sort(sort).limit(1).next()
	
	id = c['_id']['i']
	if(id > maxid)
	{
		printjson(id.getTimestamp())
		maxid = id
	}
}

printjson(maxid)
print(maxid.getTimestamp())


var idAsString = maxid.valueOf()
var timepartAsString = idAsString.substring(0,8)
var timepartAsInt = parseInt(timepartAsString,16)
timepartAsInt=timepartAsInt+startwhen
newid  = timepartAsInt.toString(16)+idAsString.substring(8,24)
newObjectId = ObjectId(newid)
print("Splitting from : ")
printjson(newObjectId)
print(newObjectId.getTimestamp())


print("Moving Chunks")
for(x=0;x<totalprefixes;x++){
	split = {_id:{s:x,i:newObjectId}};
	shard = "shard_"+(Math.floor(x/pfxpershard)+lowestnewshard);
	print ("Moving " + tojson(split) + " to " + shard);

	print("Checking it's empty")
	query = {_id:{$gt:{s:x,i:newObjectId},$lt:{s:x+1}}}
	blobcount = db.getSiblingDB('objStore').blobs.count(query)
	refcount = db.getSiblingDB('objStore').references.count(query)
	if(blobcount > 0 || refcount>0)
	{
		print("Error - moving a non empty chunk ")
		printjson(query)

	}
	r = sh.splitAt("objStore.blobs",split);
	if(r['ok'] != 1) {printjson(r)}
	r=sh.moveChunk("objStore.blobs",split,shard)
	if(r['ok'] != 1){ printjson(r)}
	r=sh.splitAt("objStore.references",split);
	if(r['ok'] != 1){ printjson(r)}
	r=sh.moveChunk("objStore.references",split,shard)
	if(r['ok'] != 1) {printjson(r)}
	
}


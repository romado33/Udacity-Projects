
# coding: utf-8

# **In this script I have include all the queries that I ran against the data in the MongoDB database.**

# In[21]:

# Here I import all libraries needed for the project

import pymongo
from pymongo import MongoClient
from collections import defaultdict
from pprint import pprint
from __future__ import division


# declaration of main OSM xml file
client = MongoClient('localhost:27017')
db = client['OSM']
coll = db.Kanata
pprint (db)


# In[22]:

print "Collection count: %d" % coll.find().count()
print "Node count: %d" % coll.find( {"type":"node"} ).count()
print "Way count: %d" % coll.find( {"type":"way"} ).count()
print "Distinct Users: %d" % len(coll.distinct( "created.user" ) )


# In[23]:

# lists all postal codes found, by number of occurences, descending
match = {"$match":{"address.postcode":{"$exists":1}}}
group = {"$group":{"_id":"$address.postcode", "count":{"$sum":1}}} 
sort = {"$sort":{"count":-1}}
pipeline = [match,group,sort]
postalcodes = coll.aggregate(pipeline)
pprint(list(postalcodes))  


# In[24]:

# Lists top 10 users who have edited this OSM file
group = {"$group":{ "_id":"$created.user", "count":{"$sum":1}}}
sort = {"$sort" : {"count" : -1}}
limit = {"$limit" : 10}
pipeline = [group,sort,limit]
top_users = coll.aggregate(pipeline)
pprint(list(top_users))  


# In[25]:

# lists top 10 occurring amenities in OSM file
match = {"$match": {"amenity":{"$exists":1}}}
group = {"$group": { "_id" :"$amenity", "count":{"$sum":1}}}
sort = {"$sort" : {"count" : -1}}
limit = {"$limit" : 10}
pipeline = [match,group,sort,limit]
amenities = coll.aggregate(pipeline)
pprint(list(amenities))  


# In[26]:

# lists top 10 places of worship, grouped by religion
match = {"$match":{"amenity":{"$exists":1}, "amenity":"place_of_worship"}}
group = {"$group":{"_id":"$religion", "count":{"$sum":1}}}
sort = {"$sort":{"count":-1}}
limit = {"$limit" : 10}
pipeline = [match,group,sort,limit]
religions = coll.aggregate(pipeline)
pprint(list(religions))  


# In[27]:

# lists top 10 restaurants, grouped by cuisine type
match = {"$match":{"amenity":{"$exists":1}, "amenity":"restaurant"}}
group = {"$group":{"_id":"$cuisine", "count":{"$sum":1}}}
sort = {"$sort":{"count":-1}}
limit = {"$limit" : 10}
pipeline = [match,group,sort,limit]
cuisines = coll.aggregate(pipeline)
pprint(list(cuisines))  


# In[28]:

# lists schools grouped by Language
match = {"$match":{"amenity":{"$exists":1}, "amenity":"school"}}
group = {"$group":{"_id":"$school:language", "count":{"$sum":1}}}
sort = {"$sort":{"count":-1}}
limit = {"$limit" : 10}
pipeline = [match,group,sort,limit]
cuisines = coll.aggregate(pipeline)
pprint(list(cuisines))  


# In[ ]:




# In[ ]:




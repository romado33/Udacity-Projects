
# coding: utf-8

# **This script contains the code that audits and cleans the OSM file, it is based on the OSM Case Study solution, but I have modified the functionality to fit me needs for this project.**

# In[9]:

# Here I import all libraries needed for the project

import xml.etree.cElementTree as ET
from collections import defaultdict
from pprint import pprint
from __future__ import division
import re
import codecs


# declaration of main OSM xml file
osmfile = 'C:/MongoDB/data/Kanata.osm'


# In[10]:

# This function audits the OSM xml file to count the tags it contains

def count_tags(filename):
    tags = {} # initialize diciontary to hold tags
    for event, element in ET.iterparse(filename): # iterate over tags
        if event == 'end': # if closing tab
            if element.tag in tags: # check to see if there is already an entry in the dictionary for that tag
                tags[element.tag] += 1 # increase tag counter by 1
        # if 'element.tag' is not a key of tags, add it:
            else:
                tags[element.tag] = 1
    return tags
        


# In[11]:

count_tags(osmfile)


# **The below code finds problematic characters, these are fixed when the file is converted from XML to Json, please see the *'Convert XML to Json' script.***

# In[12]:

# regular expressions to find problem characters in the tags
lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')


def key_type(element, keys):
    if element.tag == "tag":
        # search returns matchObject which is always true or None when 'false'
        if lower.search(element.attrib['k']):
            keys["lower"] += 1
        elif lower_colon.search(element.attrib['k']):
            keys["lower_colon"] += 1
        elif problemchars.search(element.attrib['k']):
            keys["problemchars"] += 1
        else:
            keys["other"] += 1

    return keys


def process_map(filename):
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    for _, element in ET.iterparse(filename):
        keys = key_type(element, keys)

    return keys


# In[13]:

process_map(osmfile)


# In[14]:

# these are the regular expressions that need to be matched to categorize an entry as correct or incorrect

# match proper Canadian postal code in format 'LNL NLN' where L is capital letter and N is a number (there are some letters that are not used)
valid_postal_code = re.compile(r'^[ABCEGHJKLMNPRSTVXY][0-9][ABCEGHJKLMNPRSTVWXYZ][\s][0-9][ABCEGHJKLMNPRSTVWXYZ][0-9]')

# matches postal codes with no space between 3rd and 4th characters
nospace_postal_code = re.compile(r'^[ABCEGHJKLMNPRSTVXY][0-9][ABCEGHJKLMNPRSTVWXYZ][0-9][ABCEGHJKLMNPRSTVWXYZ][0-9]')

# matches postal codes containing a lower case letter
lowercase_postal_code = re.compile(r'^[abceghjklmnprstvxy][0-9][abceghjklmnprstvxy][\s][0-9][abceghjklmnprstvxy][0-9]')

# matches correct city name of 'Ottawa' (not 'City of Ottawa')
valid_city = re.compile(r'^(?=.*Ottawa)(?!.*City).*')

# matches correct province name of 'ON'
valid_province = re.compile(r'ON')

# I wrote the below code to search for and correct any inconsistencies in the namin convention for postal code, city, and province
# The main function (test()) takes a type which lets the other functions know which of the 3 types they are working with 

# This function opens the osm file, initializes two lists, then iterates over the node and way tags to test if they are one of the
# 3 types we are looking for.  If they are, it calls the audit_match function and then returns the number of correct items
# and the number of incorrect ones

def audit(osmfile,type):
    osm_file = open(osmfile, "r") # open file
    good = [] #initialize list
    bad = [] #initialize list
    for event, elem in ET.iterparse(osm_file, events=("start",)): #iterate through tags
        if elem.tag == "node" or elem.tag == "way": #if tag is node or way then
            for tag in elem.iter("tag"): # iterate through node and way tags
                    if is_address_item(tag,type): # call function to see if the key is the appropriate one
                        audit_match(good,bad, tag.attrib['v'],type) # call function to test value against regular expression
    total = len(good) + len(bad) # get total number of items in set
    print "Correct Item," + " Total number: " + str(len(good)) + ", Percentage: " +  str(round(len(good) / total,2))
    #pprint(good) #  print number and percentage of items in correct set
    print "Incorrect Items," + " Total number: " + str(len(bad)) + ", Percentage: " + str(round(len(bad) / total,2))
    #pprint(bad)  #  print number and percentage of items in incorrect set
    return bad # return incorrect set so items can be corrected

# this functon just checks if the element in question is the key of a key-value pair for the address element that we want

def is_address_item(elem,type):
    if type == "PC":
        return elem.attrib['k'] == 'addr:postcode'
    elif type == "City":
        return elem.attrib['k'] == 'addr:city'
    elif type == "Prov":
        return elem.attrib['k'] == 'addr:province'
    
# This function checks each element against the regular expressions for a correct naming convention, if there is a match
# it is added to the 'good' list, otherwise, it is added to the 'bad' list

def audit_match(good,bad,item,type):
    if type == "PC":
        valid = valid_postal_code
    elif type == "City":
        valid = valid_city
    elif type == "Prov":
        valid = valid_province
    if valid.match(item):
        good.append(item)
    else:
        bad.append(item)
    return good, bad

#this function corrects the naming problem for the element in question

def correct_item(bi,type):
    if type == "PC":
        prob_nospace = nospace_postal_code.search(bi) # try to match with r.e. for no spaces
        prob_lowercase = lowercase_postal_code.search(bi) # try to match with r.e. for lower case letters
        if prob_nospace:
            bi = bi[:3] + " " + bi[3:] # insert space between 3rd and 4th character
        if prob_lowercase:
            bi = bi.upper() # convert to upper case
    if type == "City":
        bi = "Ottawa"
    if type == "Prov":
        bi = "ON"
    return bi

# main function, takes address element we are looking for as 'type', then creates list of incorrect items, and calls 
# the function that corrects them

def test(type):
    if type == "PC":
        bad_postal_codes = audit(osmfile,type)
        print "Corrections:"
        for bpc in bad_postal_codes: # for each item in the bad item list
            corrected_pc = correct_item(bpc,type) #call the correct_item function to correct it
            print bpc, "=>", corrected_pc # print out before/after
    elif type == "City":
        bad_cities = audit(osmfile,type)
        print "Corrections:"
        for bc in bad_cities: # for each item in the bad item list
            corrected_ct = correct_item(bc,type) #call the correct_item function to correct it
            print bc, "=>", corrected_ct # print out before/after
    elif type == "Prov":
        bad_provinces = audit(osmfile,type)
        print "Corrections:"
        for bp in bad_provinces: # for each item in the bad item list
            corrected_prov = correct_item(bp,type) #call the correct_item function to correct it
            print bp, "=>", corrected_prov # print out before/after


# In[15]:

test("PC")


# In[16]:

test("City")


# In[17]:

test("Prov")


# In[ ]:




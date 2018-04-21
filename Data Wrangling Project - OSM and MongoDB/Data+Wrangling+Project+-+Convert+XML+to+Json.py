
# coding: utf-8

# **This code, which takes an xml file and outputs a Json file which can be loaded into MongoDB, was taken from the lesson on 'Preparing for Database' and edited to include my cleaning code.**

# In[15]:

import xml.etree.cElementTree as ET
from collections import defaultdict
from pprint import pprint
from __future__ import division
import codecs
import json
import re

# declaration of main OSM xml file
osmfile = 'C:/MongoDB/data/Kanata.osm'


# regular expressions to find problem characters in the tags
# these are the regular expressions that need to be matched to categorize an entry as correct or incorrect

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

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


CREATED = ["version", "changeset", "timestamp", "user", "uid"]


def shape_element(element):
    node = {} #creates dictionary
    if element.tag == "node" or element.tag == "way": #if tag is node or way
        node['type'] = element.tag # create dictionary entry with type as key and tag as value
        
        # Parse attributes
        for a in element.attrib:
            if a in CREATED: # if the element attribute is in the CREATED list above do nothing
                if 'created' not in node: 
                    node['created'] = {} # create 'created' key with empty value in node dictionary
                node['created'][a] = element.attrib[a] # assign 'attrib[a] value to 'created' key

            elif a in ['lat', 'lon']: 
                if 'pos' not in node: 
                    node['pos'] = [None, None] #initialize multi dimensional diciontary entry with 'pos' key.
                if a == 'lat': 
                    node['pos'][0] = float(element.attrib[a]) # 'lat' is assigned to first position in 'node' diciontary entry
                else:
                    node['pos'][1] = float(element.attrib[a]) # 'long' is assigned to second position in 'node' diciontary entry

            else:
                node[a] = element.attrib[a] # just asssign the value to the key in question

        # I have now included my cleaning code in Shape_Element as directed in the Initial Project Review
        for tag in element.iter("tag"):
            if tag.attrib['k'] == 'addr:postcode':
                prob_nospace = nospace_postal_code.search(tag.attrib['k']) # try to match with r.e. for no spaces
                prob_lowercase = lowercase_postal_code.search(tag.attrib['k']) # try to match with r.e. for lower case letters
                if prob_nospace:
                    tag.attrib['k'] = tag.attrib['k'][:3] + " " + tag.attrib['k'][3:] # insert space between 3rd and 4th character
                if prob_lowercase:
                    tag.attrib['k'] = tag.attrib['k'].upper() # convert to upper case   
            elif  tag.attrib['k'] == 'addr:city':
                tag.attrib['k'] = "Ottawa"         
            elif tag.attrib['k'] == 'addr:province':
                tag.attrib['k'] = "ON"
                
                
            if not problemchars.search(tag.attrib['k']): 
                # Tags with single colon
                if lower_colon.search(tag.attrib['k']): 
                    # Single colon beginning with addr,
                    if tag.attrib['k'].find('addr') == 0:
                        if 'address' not in node:
                            node['address'] = {}
                        sub_attr = tag.attrib['k'].split(':', 1)
                        node['address'][sub_attr[1]] = tag.attrib['v']

                    # All other single colons processed normally
                    else:
                        node[tag.attrib['k']] = tag.attrib['v']

                # Tags with no colon
                elif tag.attrib['k'].find(':') == -1:
                    node[tag.attrib['k']] = tag.attrib['v']

            # Iterate nd children
            for nd in element.iter("nd"):
                if 'node_refs' not in node:
                    node['node_refs'] = []
                node['node_refs'].append(nd.attrib['ref'])

        return node
    else:
        return None

#output file to json format
def output_json(file_in, pretty=False):
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2) + "\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data


# In[16]:

output_json(osmfile)


# In[ ]:




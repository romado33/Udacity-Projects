#!/usr/bin/python

import sys
import pickle
import matplotlib.pyplot as plt
sys.path.append("../tools/")
from feature_format import featureFormat, targetFeatureSplit
from tester import dump_classifier_and_data, test_classifier
#from prettytable import PrettyTable
import pandas as pd
import numpy as np


### Task 1: Select what features you'll use.
### features_list is a list of strings, each of which is a feature name.
### The first feature must be "poi".
features_list = ['poi','salary', 'total_payments',
                 'bonus', 'total_stock_value', 'expenses', 
                 'exercised_stock_options',  
                 'to_messages', 'from_poi_to_this_person', 'from_messages', 
                 'from_this_person_to_poi', 'shared_receipt_with_poi']

### Load the dictionary containing the dataset
with open("final_project_dataset.pkl", "r") as data_file:
    data_dict = pickle.load(data_file)
    
print "Dataset Length", len(data_dict)

my_df = pd.DataFrame(data_dict).transpose() # transpose to get features as columns

# replace NaN with numpy nan so that we can use the .isnull() method
my_df= my_df.replace('NaN', np.nan)

# count up null values
nacount = my_df.isnull().sum().sort_values()


### Task 2: Remove outliers
    
data = featureFormat(data_dict, features_list)

### Plot salary vs bonus and emails and from_messages vs  in order to spot
### outliers
    
for point in data:
    salary = point[1]
    bonus = point[3]
    from_messages = point[10]
    to_messages = point[8]
    
    plt.tight_layout()
    
    plt.subplot(2, 1, 1)
    plt.scatter(salary, bonus)
    plt.xlabel("salary")
    plt.ylabel("bonus")

    plt.subplot(2, 1, 2)
    plt.scatter(from_messages,to_messages)
    plt.xlabel("Messages Received")
    plt.ylabel("Messages Sent")
    
    
### find maxvalue for salary and from_messages to investigate outliers

maxsalary = 0
max_from_messages = 0
for key, value in data_dict.iteritems():
    for ind, val in value.iteritems():
        if (ind == "salary") and (val != "NaN"):
                if val > maxsalary:
                    maxsalary = val
                    maxsalarykey = key
        if (ind == "from_messages") and (val != "NaN"):
                if val > max_from_messages:
                    max_from_messages = val
                    max_from_message_key = key

#print '\r'                
#print "Max salary value is", maxsalary, "belonging to", maxsalarykey
#print '\r'
#print "Max from_message value is", max_from_messages, "belonging to", max_from_message_key
#print '\r'
                    
#remove outliers
                    
data_dict.pop( "THE TRAVEL AGENCY IN THE PARK", 0)
data_dict.pop( "TOTAL", 0)


### Task 3: Create new feature(s)
for person in data_dict:

    if (data_dict[person]['to_messages'] not in ['NaN', 0]) and (data_dict[person]['from_this_person_to_poi'] not in ['NaN', 0]):
        data_dict[person]['to_poi_perc'] = float(data_dict[person]['from_this_person_to_poi'])/float(data_dict[person]['to_messages'])
    else:
        data_dict[person]['to_poi_perc'] = 0
    if (data_dict[person]['total_payments'] not in ['NaN', 0]) and (data_dict[person]['salary'] not in ['NaN', 0]):
        data_dict[person]['salary_perc'] = float(data_dict[person]['salary'])/float(data_dict[person]['total_payments'])
    else:
        data_dict[person]['salary_perc'] = 0
    if (data_dict[person]['shared_receipt_with_poi'] not in ['NaN', 0]):
        data_dict[person]['shared_receipt_perc'] = float(data_dict[person]['to_messages'])/float(data_dict[person]['shared_receipt_with_poi'])
    else:
        data_dict[person]['shared_receipt_perc'] = 0
        
my_features_list = ['to_poi_perc', 'salary_perc','shared_receipt_perc']

features_list = features_list + my_features_list
    
### Store to my_dataset for easy export below.
my_dataset = data_dict


### Extract features and labels from dataset for local testing
data = featureFormat(my_dataset, features_list, sort_keys = True)
labels, features = targetFeatureSplit(data)


### Task 4: Try a varity of classifiers
### Please name your classifier clf for easy export below.
### Note that if you want to do PCA or other multi-stage operations,
### you'll need to use Pipelines. For more info:
### http://scikit-learn.org/stable/modules/pipeline.html

from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import classification_report
from sklearn.cross_validation import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.model_selection import GridSearchCV
from sklearn.feature_selection import SelectKBest
from sklearn.model_selection import StratifiedShuffleSplit

features_train, features_test, labels_train, labels_test = train_test_split(features, labels,test_size=0.3, random_state=42)

# Trying out 4 different classifiers

print '\r'
print "Classifer Scores:"
print '\r'
 
from sklearn.naive_bayes import GaussianNB
clf = GaussianNB()

clf = clf.fit(features_train,labels_train)
pred = clf.predict(features_test)
print "Gaussian Naive Bayes Report:"
print '\r',classification_report(labels_test, pred)

from sklearn import tree
clf = tree.DecisionTreeClassifier()

clf = clf.fit(features_train,labels_train)
pred = clf.predict(features_test)
print "Decision Tree Report:"
print '\r',classification_report(labels_test, pred)

from sklearn.neighbors import KNeighborsClassifier
clf = KNeighborsClassifier(n_neighbors=3)

clf = clf.fit(features_train,labels_train)
pred = clf.predict(features_test)
print "KNeighbours Report:"
print '\r',classification_report(labels_test, pred)


from sklearn.ensemble import AdaBoostClassifier
clf = AdaBoostClassifier()

clf = clf.fit(features_train,labels_train)
pred = clf.predict(features_test)
print "AdaBoost Report:"
print '\r',classification_report(labels_test, pred)


# pipeline

skb = SelectKBest()              
clf_GNB = GaussianNB()

clf = Pipeline(steps=[("SKB", skb),("NaiveBayes", clf_GNB)])

clf = clf.fit(features_train,labels_train)
pred = clf.predict(features_test)
print "Pipeline Report:"
print '\r',classification_report(labels_test, pred)



### Task 5: Tune your classifier to achieve better than .3 precision and recall 
### using our testing script. Check the tester.py script in the final project
### folder for details on the evaluation method, especially the test_classifier
### function. Because of the small size of the dataset, the script uses
### stratified shuffle split cross validation. For more info: 
### http://scikit-learn.org/stable/modules/generated/sklearn.cross_validation.StratifiedShuffleSplit.html



#scaler = MinMaxScaler(),('scaling',scaler),
#pca = PCA(), ("PCA", pca),  ,"PCA__n_components":[2,4],"PCA__whiten": [True]  
skb = SelectKBest()              
clf_GNB = GaussianNB()

pipe= Pipeline(steps=[("SKB", skb),("NaiveBayes", clf_GNB)])

pca_params = {"SKB__k":[1,5]}

sshuff = StratifiedShuffleSplit(n_splits = 100, random_state=42)

gs = GridSearchCV(
    pipe,
    param_grid = pca_params,
    verbose=0,
    scoring = 'f1',
    cv=sshuff
)

gs.fit(features,labels)

features_selected_bool = gs.best_estimator_.named_steps['SKB'].get_support()
features_selected_scores = gs.best_estimator_.named_steps['SKB'].scores_
features_selected_list = [x for x, y in zip(features_list[1:], features_selected_bool) if y]
print 'Feature Scores:'
print '\r'
print "features_selected_list", features_selected_list
print '\r'
print "features_selected_scores", features_selected_scores
print '\r'

pred = gs.predict(features_test)
clf = gs.best_estimator_


# Print Results 
print "Classification report:" 
print " "
test_classifier(clf, my_dataset, features_list)

### Task 6: Dump your classifier, dataset, and features_list so anyone can
### check your results. You do not need to change anything below, but make sure
### that the version of poi_id.py that you submit can be run on its own and
### generates the necessary .pkl files for validating your results.

dump_classifier_and_data(clf, my_dataset, features_list)
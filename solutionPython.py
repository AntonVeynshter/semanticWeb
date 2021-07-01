#!/usr/bin/env python
# coding: utf-8

# In[1]:


from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd
import urllib
import traceback


# In[2]:


data_test=pd.read_csv("SNLP_2020_test.nt",sep=" ",names=["1","2","3","."])


# In[3]:


data_test.head()


# In[4]:



def check(s,o,sparql):
    punc = '''!()-[]{};:'"\,<>.?@#$%^&*_~'''

    sparql.setQuery(
        "SELECT ?a WHERE {{\
        "+s+" <http://dbpedia.org/ontology/abstract> ?a FILTER (  langMatches(lang(?a),'en') ) .}UNION{\
        "+s+" <http://dbpedia.org/ontology/wikiPageWikiLink> ?a .\
        }}")
    sparql.setReturnFormat(JSON)
    try:
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        if len(results["results"]["bindings"])==1:
            s="<"+results["results"]["bindings"][0]["a"]["value"]+">"
            sparql.setQuery(
                "SELECT ?a WHERE {{\
                "+s+" <http://dbpedia.org/ontology/abstract> ?a FILTER (  langMatches(lang(?a),'en') ) .}UNION{\
                "+s+" <http://dbpedia.org/ontology/wikiPageWikiLink> ?a .\
                }}")
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()
        
        string_to_search=""
        string_to_find=urllib.parse.unquote(o)
        string_to_find=string_to_find.split("/")[-1][:-1].replace("_"," ")
        for ele in punc: 
            string_to_find = string_to_find.replace(ele, " ") 
        for row in results["results"]["bindings"]:
            if row["a"]["type"]=="uri":
                value=row["a"]["value"].split("/")[-1][:].replace("_"," ").lower()
            if row["a"]["type"]=="literal":
                value=row["a"]["value"].replace("_"," ").lower()        
            for ele in punc: 
                value = value.replace(ele, "") 
            string_to_search+=" "+value
    except:
        print("error")
        print(s,o)
        return "0.0"
    string_to_search=string_to_search.lower().split(" ")
    string_to_find=string_to_find.lower().split(" ")
    
    if all(item in string_to_search for item in string_to_find):
        return "1.0"

    else:
        return "0.0"
    


# In[5]:



def check2(s,p,o,sparql):
    punc = '''!()-[]{};:'"\,<>.?@#$%^&*_~'''
    abstract=None
    sparql.setQuery(
        "SELECT ?a WHERE {{\
        "+s+" <http://dbpedia.org/ontology/abstract> ?a FILTER (  langMatches(lang(?a),'en') ) .}UNION{\
        "+s+" <http://dbpedia.org/ontology/wikiPageWikiLink> ?a .\
        }}")
    sparql.setReturnFormat(JSON)
    try:
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        if len(results["results"]["bindings"])==1:
            s="<"+results["results"]["bindings"][0]["a"]["value"]+">"
            sparql.setQuery(
                "SELECT ?a WHERE {{\
                "+s+" <http://dbpedia.org/ontology/abstract> ?a FILTER (  langMatches(lang(?a),'en') ) .}UNION{\
                "+s+" <http://dbpedia.org/ontology/wikiPageWikiLink> ?a .\
                }}")
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()
        
        string_to_search=""
        string_to_find=urllib.parse.unquote(o)
        string_to_find=string_to_find.split("/")[-1][:-1].replace("_"," ")
        prop=p.split("/")[-1][:-1]
        for ele in punc: 
            string_to_find = string_to_find.replace(ele, " ") 
        for row in results["results"]["bindings"]:
            if row["a"]["type"]=="uri":
                value=row["a"]["value"].split("/")[-1][:].replace("_"," ").lower()
            if row["a"]["type"]=="literal":
                value=row["a"]["value"].replace("_"," ").lower()
                abstract=value
            for ele in punc: 
                value = value.replace(ele, "") 
            string_to_search+=" "+value
    except:
        traceback.print_exc()
        print("error")
        print(s,o)
        return "0.0"
    string_to_search=string_to_search.lower().split(" ")
    string_to_find=string_to_find.lower().split(" ")
    #abstract=abstract.split(" ")
    if all(item in string_to_search for item in string_to_find):
        return "1.0"
        if prop in string_to_search:
            for i,token in enumerate(string_to_search):
                if token==prop:
                    if all(item in string_to_search[i-10:i+10] for item in string_to_find):
                        return "1.0"
                    else:
                        return "0.0"
        else:
            return "1.0"
    else:
        return "0.0"
    


# In[6]:


range_list=["<http://dbpedia.org/ontology/subsidiary>",
           "<http://dbpedia.org/ontology/award>",
           "<http://dbpedia.org/ontology/deathPlace>",
           "<http://dbpedia.org/ontology/spouse>",
           "<http://dbpedia.org/ontology/subsidiary>",
           "<http://dbpedia.org/ontology/starring>",
           "<http://dbpedia.org/ontology/foundationPlace>",
           "<http://dbpedia.org/ontology/author>"]
ignore_list=["<http://dbpedia.org/ontology/team>"]
def check_property(p,o,sparql):

    if p in range_list:
        sparql.setQuery(
                "SELECT ?a ?b WHERE {{\
                "+p+" <http://www.w3.org/2000/01/rdf-schema#range> ?a .}UNION{\
                "+o+" <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ?b.\
                }}")   
    else:
        return "1.0"    
    
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    a=results["results"]["bindings"][0]["a"]["value"]
    b=[]
    for row in results["results"]["bindings"]:
        try:
            b.append(row["b"]["value"])
        except:
            continue
    if a in b:
        return "1.0"
    elif p=="<http://dbpedia.org/ontology/starring>" and "http://dbpedia.org/ontology/Person" in b:
        return "1.0"
    elif p=="<http://dbpedia.org/ontology/team>" and "http://dbpedia.org/ontology/Organisation" in b:
        return "1.0"
    elif p=="<http://dbpedia.org/ontology/foundationPlace>" and "http://dbpedia.org/ontology/Location" in b:
        return "1.0"
    elif p=="<http://dbpedia.org/ontology/author>" and "http://dbpedia.org/ontology/Work" in b:
        return "1.0"
    else:
        return "0.0"


# In[7]:


s=None
o=None
p=None
answer=None
flag=False
dataset_id=None

sparql = SPARQLWrapper("http://dbpedia.org/sparql")

with open('submit.nt', 'w') as f:

    
    for i,row in data_test.iterrows():
        if i%200==0:
            print(i)
        if row["3"]=="<http://www.w3.org/1999/02/22-rdf-syntax-ns#Statement>":
            s=None
            o=None
            p=None
            answer=None
            flag=False
            dataset_id=None
            continue 

        
        if row["2"]=="<http://www.w3.org/1999/02/22-rdf-syntax-ns#subject>":
            s=row["3"]
            dataset_id=row["1"]
            continue
         
        if row["2"]=="<http://www.w3.org/1999/02/22-rdf-syntax-ns#object>":
            o=row["3"]
            flag=True
        if row["2"]=="<http://www.w3.org/1999/02/22-rdf-syntax-ns#predicate>":
            p=row["3"]
            
        if flag==True:
            direkt_answer=check2(s,p,o,sparql)
            backword_answer=check(o,s,sparql)
            if direkt_answer=="1.0" or backword_answer=="1.0":
                my_answer=check_property(p,o,sparql)
            else:
                my_answer="0.0"
            line=dataset_id+ " "+"<http://swc2017.aksw.org/hasTruthValue> "+'"'+my_answer+'"'+"^^<http://www.w3.org/2001/XMLSchema#double> .\n"
            f.write(line)
    f.close()


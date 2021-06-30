#!/usr/bin/env python
# coding: utf-8

# In[1]:


from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd
import urllib


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


s=None
o=None
p=None
answer=None
flag=False
dataset_id=None

sparql = SPARQLWrapper("http://dbpedia.org/sparql")

with open('submit.nt', 'w') as f:

    
    for i,row in data_test.iterrows():
        if i%50==0:
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
     
        if flag==True:
            direkt_answer=check(s,o,sparql)
            backword_answer=check(o,s,sparql)
            if direkt_answer=="1.0" or backword_answer=="1.0":
                my_answer="1.0"
            else:
                my_answer="0.0"
            line=dataset_id+ " "+"<http://swc2017.aksw.org/hasTruthValue> "+'"'+my_answer+'"'+"^^<http://www.w3.org/2001/XMLSchema#double> .\n"
            f.write(line)
    f.close()


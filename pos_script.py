#Normal Pretrained
import spacy
from spacy import displacy
from spacy.util import minibatch, compounding
import random
import os
import string
import pathlib
import re

import argparse

parser = argparse.ArgumentParser(description='POS Tagging using Spacy')
parser.add_argument("filepath", help="input the file path of your dataset", type=str)
args = parser.parse_args()

# Load a pretrained spaCy model
nlp = spacy.load('en_core_web_sm')

str_list = []
string1 = ""
f3 = open(args.filepath,'r')
next(f3)
for line in f3:
    word = line.strip("\n")
    # add only first word if line not equal \n
    if line != "\n": string1 += line.split(None, 1)[0]  + " " 
    else:
        if string1 != "\n":
          str_list.append(string1)
          string1 = ""
#append last string to list
str_list.append(string1)

f1 = open(args.filepath,'r')
f2 = open(args.filepath+"-POS",'w')

count=0
temp_text = "x"
token_counter = 0
for x in str_list:
  # Run the text through the pretrained model
  doc = nlp(x)
  #The NER pipeline component tags entities in the doc with various attributes
  for token in doc:
    # check if token is not in previous text
    if token.text not in temp_text and count==0:
      temp_text="x"
     # check if token is in previous text
    elif count == 1 and token.text in temp_text:
      # check if previous text ends with current token
      if temp_text.endswith(token.text):
        # check if the count of token in previous text is more than 1
        if temp_text.count(token.text) > 1:
          token_counter +=1
           # check if the previous text starts with token and if the token counter has hit the total count
          if temp_text.startswith(token.text) and temp_text.count(token.text)-1 == token_counter:
            token_counter=0
            count=0
            temp_text = "x"
          # check if the previous text does not starts with token and if the token counter has hit the total count
          elif not temp_text.startswith(token.text) and temp_text.count(token.text) == token_counter:
            token_counter=0
            count=0
            temp_text = "x"
        else:
          count=0
          temp_text = "x"
      continue
    # check if token is not in previous text 
    if (token.text not in temp_text):
      line = f1.readline()
      token_counter=0
      count=0
      temp_text = "x"
      # check if line is new line
      if line == '\n' or not line:
        f2.write("\n")
        line = f1.readline()
    else: continue
    # check if token is in current line 
    if (token.text in line.strip("\n") and count==1): continue 
    else:
      # retrieve the first word of the line from conll format
      mod_line = line.strip("\n").split(" ",2)
      # check if token is same as the first word of the current line
      if (token.text == mod_line[0]):
        z = line.replace("-X-", token.tag_)
        f2.write(z)
        # print("writing ... "+z)
      # check if token is a subset of the first word of the current line
      elif (token.text in mod_line[0] and count==0):
        temp_text = mod_line[0]
        z = line.replace("-X-", token.tag_)
        f2.write(z)
        count=1
      else: 
        doc = nlp(mod_line[0])
        for token in doc:
          f2.write(line.replace("-X-", token.tag_))
       
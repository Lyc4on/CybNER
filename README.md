
# Cybersecurity Named Entity Recognition
## Introduction
A AllenNLP Model trained for Named Entity Recognition in the Cybersecurity Domain with added features of automated annotation and visualization graph.
## Requirements
- Python3
## Installation and Setup 
 ```bash
git clone https://github.com/Lyc4on/Cybersecurity-NER.git
pip install -r requirements.txt
```
## System Architecture
The diagram below depicts the overall architecture of the system, beginning from the collection of cybersecurity related raw text to the training and usage of the AllenNLP model. Take note that in this diagram, The Cyber Threat intelligence Hunter (CTIH), a application from Singapore Institute of Technology (SIT), which utlises the model for prediction would not be featured in the repository.

![](images/Project_Architecture.png)

## Usage
```bash
# perform checks for encoding errors on a user specified dataset in CoNLL-2003 format, example.conll.
python analyse.py -dc -f "example.conll"

#perform training on the AllenNLP model with the user specified configuration file named raw_text.json.
# mode = 1 - perform train and overwrite output directory
python analyse.py -t 1 -c "raw_text.json"

#perform conversion of user specified raw text file, named raw_text.csv to JSON format for prediction purpose.
python analyse.py -co -f "raw_text.csv"

#perform prediction with the AllenNLP model by suppying a raw text file named raw_text.json.
python analyse.py -p -f "raw_text.json"

#generate a interactive web based knowledge graph with the user specified dataset file named example.conll.
python analyse.py -vg -f "example.conll"

```

```
Options:
    -f          inpu the path of the file/dataset required by visual graph, conversion, dataset_check or predict function.
    -t          train the model with a customised config or with the same dataset | - t [1, 2, 3], 1 - train with force overwrite 2 - train with recovery 3 - help page on train cmd.
    -c          input model configuration file to perform training of model.
    -p          perform prediction with the model with the supplied raw text provided by the user | -p [1, 2], 1 - predict from CSV file, 2 - predict from TXT file.
    -vg         generate a interactive web-based knowledge graph based on a dataset in CoNLL-2003 format.
    -co         convert a CSV file to a JSON file format for predictions with the model.
    -dc         perform checks for encoding errors on user supplied dataset.
```

## Visualization Graph 
 A interactive knowledge graph can be generated with the use of dash cytoscape and python flask libraries, for a better visualization of cybersecurity terms identified from a raw txt file in CoNLL-2003 format. A example of the interactive knowledge graph based on a small dataset are as shown below:

![](images/Knowledge_Graph.png)

## Releases
The release section consists of the trained AllenNLP model at https://github.com/Lyc4on/Cybersecurity-NER/releases/download/v1.0.0/AllenNLP_model.tar.gz


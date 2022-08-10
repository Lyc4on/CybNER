
# Cybersecurity Named Entity Recognition
## Introduction
A AllenNLP Model trained for Named Entity Recognition in the Cybersecurity Domain with added features of automated annotation and visualization graph.

## Requirements
- Python3
- Anaconda 

## Installation and Setup 
1. Download Anaconda from **https://www.anaconda.com/products/distribution**

 ```bash
conda create -n conda_env python=3.9
conda activate conda_env
git clone https://github.com/Lyc4on/Cybersecurity-NER.git
pip install -r requirements.txt
conda install -c anaconda cudatoolkit
```

## System Architecture
The diagram below depicts the overall architecture of the system, beginning from the collection of cybersecurity related raw text to the training and usage of the AllenNLP model. Take note that in this diagram, The Cyber Threat intelligence Hunter (CTIH), a application from Singapore Institute of Technology (SIT), which utlises the model for prediction would not be featured in the repository.

![](images/Project_Architecture.png)


## Usage
Trained AllenNLP model can be found in the release section at https://github.com/Lyc4on/Cybersecurity-NER/releases/download/v1.0.0/AllenNLP_model.tar.gz
 ```bash
python main.py -p <csv file>
```

## Visualization Graph 
 A interactive knowledge graph can be generated with the use of dash cytoscape and python flask libraries, for a better visualization of cybersecurity terms identified from a raw txt file in CoNLL-2003 format.
 ```bash
python main.py -p <csv file>
```

![](images/Knowledge_Graph.png)


import os
import re
import pandas as pd
import json


# ================ FUNCTION SECTION ================ #

def filecheck(path):
    """ To check and pinpoint for any encoding errors in the dataset """
    print("\n**************** Filecheck Started ****************")
    file1 = open(path, 'r+')
    count = 0
    while True:
        count += 1
        # Get next line from file
        line = file1.readline()
        # if line is empty
        # end of file is reached
        if not line:
            # Break when unable to open
            break
        print("Line{}: {}".format(count, line.strip()))
    file1.close()
    print("\n**************** Filecheck Complete ****************")


def train(mode, modelpath, config):
    """ Selection of different Modes of Operation for Prediction
    1 - Train with force overwrite
    2 - Train with Recover Model
    3 - Allennlp Train -h
    """
    print("\n**************** Training Started ****************")
    try:
        command = ""
        if mode == 1:
            command = "allennlp train -f -s " + modelpath + " " + config
        elif mode == 2:
            command = "allennlp train -s " + modelpath + " " + config + " --recover"
        elif mode == 3:
            command = "allennlp train -h"
        else:
            print("Select a mode")
            exit(1)
            print("\n**************** Training Complete ****************")
        print("\n**************** Training Commencing ****************")
        os.system(command)
        print("\n**************** Training Complete ****************")
    except:
        print("Something went wrong during training.")
        print("\n**************** Training Unsuccessful ****************")


def predict(mode, modelpath, outputpath):
    """ Selection of different Modes of Operation for Prediction
    1 - Predict from CSV and output evaluation.conll
    2 - Predict from Sample Sentence (sample.txt)
    """
    print("\n**************** Prediction Started ****************")
    try:
        command = ""
        if mode == 1:
            command = "allennlp predict --output-file " + outputpath + " " + modelpath + " data/texts/formatted_data" \
                                                                                         ".txt "
        elif mode == 2:
            command = "allennlp predict --output-file " + outputpath + " " + modelpath + " data/texts/sample" \
                                                                                         ".txt "
        else:
            print("Select a mode")
            print("\n**************** Prediction Complete ****************")
            exit(1)
        print("\n**************** Prediction Commencing ****************")
        os.system(command)
        print("\n**************** Prediction Complete ****************")
    except:
        print("Something went wrong during prediction.")
        print("\n**************** Prediction Unsuccessful ****************")


def csvToConll(csvpath, formattedpath):
    """To covert raw data in CSV format to sentences as input for prediction"""
    print("\n**************** Commencing Formatting ****************")
    # Converting CSV to formatted data
    sentence = ""
    dataList = pd.read_csv(csvpath, on_bad_lines='skip')
    # !!ensure that the heading in the csv for the data to be formatted is "Raw Data"!!
    for row in dataList["Raw Data"].values:
        if pd.isna(row):  # end of csv file
            break
        s = row
        # check if sentence is not empty
        if s:
            # strip() formats the whitespaces at the start and end of the string
            s = s.strip()
            # add the sanitised s into formatted sentence string
            sentence = sentence + s
    with open(formattedpath + '/formatted_data.txt', 'w', encoding='utf-8') as f:
        data_set = {"sentence": sentence}
        json.dump(data_set, f, ensure_ascii=False)
    print("\nFile saved in \'" + formattedpath + "/formatted_data.txt\'")
    print("\n**************** Formatting Complete****************")


def wordCleanup(evalpath):
    """To compile the words from the output"""
    f = open(evalpath, "r")
    text = f.read()
    regexp = re.compile("words(.*)$")
    newText = regexp.search(text).group(1)
    newClean = re.sub('[:",\]]', '', newText)
    string_without_brackets = re.sub(r"[\[]", '', newClean)
    removed_cursive_brackets = string_without_brackets.replace('}', '')
    outputText = removed_cursive_brackets.replace(' ', '\n')
    words = open(os.path.dirname(evalpath) + "/words.txt", "w")
    words.write(outputText[1:])
    words.close()


def tagCleanup(evalpath):
    """To compile the tags from the output"""
    f = open(evalpath, "r")
    text = f.read()
    regexp = re.compile("tags(.*)$")
    newText = regexp.search(text).group(1)
    clean = newText.split('words')[0]
    newClean = re.sub('[:",]', '', clean)
    string_without_front_brackets = re.sub(r"[\[\]]", '', newClean)
    outputText = string_without_front_brackets.replace(' ', '\n')
    tagsFile = open(os.path.dirname(evalpath) + "/tags.txt", "w")
    tagsFile.write(outputText[1:])
    tagsFile.close()
    newf = "-X- I-O "
    filepath = os.path.dirname(evalpath) + "/tags.txt"
    with open(filepath) as fp:
        lines = fp.read().splitlines()
    with open(filepath, "w") as fp:
        for line in lines:
            print(newf + line, file=fp)


def whitespaceTaggingRemoval(evalpath):
    """To remove inaccurate predictions of whitespaces"""
    with open(os.path.dirname(evalpath) + '/evaluation.conll', 'r') as file:
        filedata = file.read()

    # Remove all whitespace: Data clean up manually
    filedata = filedata.replace('\n -X- I-O O', '\n')
    filedata = filedata.replace('\n -X- I-O U-PER', '\n')
    filedata = filedata.replace('\n -X- I-O U-ORG', '\n')
    filedata = filedata.replace('\n -X- I-O U-LOC', '\n')
    filedata = filedata.replace('\n -X- I-O U-EXPLOITS', '\n')
    filedata = filedata.replace('\n -X- I-O U-MALWARE', '\n')
    filedata = filedata.replace('\n -X- I-O U-VENDOR', '\n')
    filedata = filedata.replace('\n -X- I-O U-DEVICES', '\n')
    filedata = filedata.replace('\n -X- I-O U-NETWORK', '\n')
    filedata = filedata.replace('\n -X- I-O U-PATH', '\n')
    filedata = filedata.replace('\n -X- I-O U-COMMANDS', '\n')
    filedata = filedata.replace('\n -X- I-O U-APT', '\n')
    filedata = filedata.replace('\n -X- I-O U-CYBERSEC', '\n')

    with open(os.path.dirname(evalpath) + '/evaluation.conll', 'w') as file:
        file.write(filedata)


def evaluationCleanup(predictionPath):
    """To Generate the result of the prediction in .conll format"""
    print("\n**************** Evaluation Generation Started ****************")
    wordCleanup(predictionPath)
    tagCleanup(predictionPath)
    # Opening up the created text Files
    tagList = pd.read_csv(os.path.dirname(predictionPath) + "/tags.txt", sep=" ", header=None)
    wordList = pd.read_csv(os.path.dirname(predictionPath) + "/words.txt", sep=" ", header=None, skip_blank_lines=False)

    # Extracting the words that are at first column, column 0
    words = wordList[0]

    # Insertion of words into the tagList at the first column , column 0
    tagList.insert(0, " ", words)

    # Insertion of the '-DOCSTART- -X- O' for .CONLL format
    # Adding it at the end
    tagList.loc[-1] = ['-DOCSTART-', '-X-', 'O', '']
    # Moving it to the top
    tagList.index = tagList.index + 1
    tagList = tagList.sort_index()

    # Saving the new file as .conll format
    tagList.to_csv(os.path.dirname(predictionPath) + '/evaluation.conll', header=None, index=None, sep=' ', mode='w')
    whitespaceTaggingRemoval(predictionPath)
    print("\nFile saved in  \'" + os.path.dirname(predictionPath) + '/evaluation.conll\'')
    print("\n**************** Evaluation Generated ****************")


# ================ END SECTION ================ #

# ================ RUNNING SECTION ================ #

# ********** File Paths **********
trainPath = "data/train/train.conll"
validPath = "data/valid/valid.conll"
csvPath = "data/texts/main_data.csv"
formatPath = "data/texts"
outputPath = "dataOutput/predictions/prediction"
modelPath = "modelOutput/model"
configPath = "config.json"
predictionPath = outputPath

# ********** Main Functions **********
filecheck(trainPath)
csvToConll(csvPath, formatPath)
train(1, modelPath, configPath)
predict(2, modelPath, outputPath)
evaluationCleanup(predictionPath)

# ================ END SECTION ================ #

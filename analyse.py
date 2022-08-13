import sys, os, re, json, spacy, dash, argparse, logging
import pandas as pd
import dash_cytoscape as cyto
from dash import html

log = logging.getLogger("CybNER")

# ********** File Paths **********
conversionOutputPath = "data/texts"
outputPath = "dataOutput/predictions/"
modelPath = "modelOutput/1"

parser = argparse.ArgumentParser(description='CybNER - perform cybersecurity named entity recognition')
parser.add_argument("-f", "--filepath", default=None, type=str, help="input the path of the file/dataset needed by visual graph, conversion, dataset_check or predict function")
parser.add_argument("-dc", "--dataset_check", action='store_true', help="check for encoding errors in datasets")
parser.add_argument("-co", "--conversion", action='store_true', help="convert CSV file to JSON format for prediction")
parser.add_argument("-pos", "--pos_format", action='store_true', help="append POS tag to CoNLL-2003 dataset file")
parser.add_argument("-t", "--train", default=None, type=int, help="[TRAIN] 1 - train with force overwrite 2 - train with recovery 3 - help page on train cmd | retrain the model with customised config or with the same dataset")
parser.add_argument("-c", "--config", default=None, type=str, help="input configuration file for training")
parser.add_argument("-p", "--predict", action='store_true', help="perform prediction on supplied raw text")
parser.add_argument("-vg", "--visual_graph", action='store_true', help="generate a interactive knowledge graph based on CoNLL-2003 format")
args = parser.parse_args()

# ================ FUNCTION SECTION ================ #
def dataset_check(path):
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
    1 - Train and force overwrite the model output directory
    2 - Train and recover past serialization directory (retrain)
    """
    print("\n**************** Training Started ****************")
    try:
        command = ""
        if mode == 1:
            command = "allennlp train -f -s " + modelpath + " " + config
        elif mode == 2:
            command = "allennlp train -s " + modelpath + " " + config + " --recover"
        else:
            print("Select a mode")
            exit(1)
        print("\n**************** Training Commencing ****************")
        os.system(command)
        print("\n**************** Training Complete ****************")
    except Exception as e:
        print("Something went wrong during training.")
        print("error message: "+e)
        print("\n**************** Training Unsuccessful ****************")


def predict(filepath, modelpath, outputpath):
    """ Selection of different Modes of Operation for Prediction
    Predict from JSON and output prediction.txt -> predictionCleanup function --> prediction.conll -> POSformat function --> prediction.conll
    """
    print("\n**************** Prediction Started ****************")
    try:
        command = "allennlp predict --output-file " + outputpath + "prediction.txt " + modelpath + " " +filepath

        print("\n**************** Prediction Commencing ****************")
        os.system(command)
        predictionCleanup(outputpath+'prediction.txt')
        POSformat(outputpath+'prediction.conll')
        print("\n**************** Prediction Complete ****************")
    except Exception as e:
        print("Something went wrong during prediction.")
        print("error message: "+e)
        print("\n**************** Prediction Unsuccessful ****************")


def csvToJSON(csvpath, conversionOutputPath):
    """To covert raw data in CSV format to JSON sentences as input for prediction"""
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
    with open(conversionOutputPath + '/formatted_data.json', 'w', encoding='utf-8') as f:
        data_set = {"sentence": sentence}
        json.dump(data_set, f, ensure_ascii=False)
    print("\nFile saved in \'" + conversionOutputPath + "/formatted_data.json\'")
    print("\n**************** Formatting Complete****************")


def wordCleanup(resultPath):
    """To compile the words from the output"""
    f = open(resultPath, "r")
    text = f.read()
    regexp = re.compile("words(.*)$")
    newText = regexp.search(text).group(1)
    newClean = re.sub('[:",\]]', '', newText)
    string_without_brackets = re.sub(r"[\[]", '', newClean)
    removed_cursive_brackets = string_without_brackets.replace('}', '')
    outputText = removed_cursive_brackets.replace(' ', '\n')
    words = open(os.path.dirname(resultPath) + "/words.txt", "w")
    words.write(outputText[1:])
    words.close()


def tagCleanup(resultPath):
    """To compile the tags from the output"""
    f = open(resultPath, "r")
    text = f.read()
    regexp = re.compile("tags(.*)$")
    newText = regexp.search(text).group(1)
    clean = newText.split('words')[0]
    newClean = re.sub('[:",]', '', clean)
    string_without_front_brackets = re.sub(r"[\[\]]", '', newClean)
    outputText = string_without_front_brackets.replace(' ', '\n')
    tagsFile = open(os.path.dirname(resultPath) + "/tags.txt", "w")
    tagsFile.write(outputText[1:])
    tagsFile.close()
    newf = "-X- I-O "
    filepath = os.path.dirname(resultPath) + "/tags.txt"
    with open(filepath) as fp:
        lines = fp.read().splitlines()
    with open(filepath, "w") as fp:
        for line in lines:
            print(newf + line, file=fp)


def whitespaceTaggingRemoval(resultPath):
    """To remove inaccurate predictions of whitespaces"""
    with open(os.path.dirname(resultPath) + '/prediction.conll', 'r') as file:
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

    with open(os.path.dirname(resultPath) + '/prediction.conll', 'w') as file:
        file.write(filedata)


def predictionCleanup(predictionPath):
    """To Generate the result of the prediction in .conll format"""
    print("\n**************** Prediction Result Generation Started ****************")
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
    tagList.to_csv(os.path.dirname(predictionPath) + '/prediction.conll', header=None, index=None, sep=' ', mode='w')
    whitespaceTaggingRemoval(predictionPath)
    print("\nFile saved in  \'" + os.path.dirname(predictionPath) + '/prediction.conll\'')
    print("\n**************** Prediction Result Generated ****************")


def POSformat(resultPath):
    """To add POS tags onto datasets."""
    print("\n**************** Adding POS Tags ****************")
    # Load a pretrained spaCy model
    nlp = spacy.load('en_core_web_sm')

    str_list = []
    string1 = ""
    f3 = open(resultPath, 'r')
    next(f3)
    for line in f3:
        word = line.strip("\n")
        # add only first word if line not equal \n
        if line != "\n":
            string1 += line.split(None, 1)[0] + " "
        else:
            if string1 != "\n":
                str_list.append(string1)
                string1 = ""
    # append last string to list
    str_list.append(string1)

    f1 = open(resultPath, 'r')
    f2 = open(resultPath + "-POS", 'w')

    count = 0
    temp_text = "x"
    token_counter = 0
    for x in str_list:
        # Run the text through the pretrained model
        doc = nlp(x)
        # The NER pipeline component tags entities in the doc with various attributes
        for token in doc:
            # check if token is not in previous text
            if token.text not in temp_text and count == 0:
                temp_text = "x"
            # check if token is in previous text
            elif count == 1 and token.text in temp_text:
                # check if previous text ends with current token
                if temp_text.endswith(token.text):
                    # check if the count of token in previous text is more than 1
                    if temp_text.count(token.text) > 1:
                        token_counter += 1
                        # check if the previous text starts with token and if the token counter has hit the total count
                        if temp_text.startswith(token.text) and temp_text.count(token.text) - 1 == token_counter:
                            token_counter = 0
                            count = 0
                            temp_text = "x"
                        # check if the previous text does not start with token and if the token counter has hit the
                        # total count
                        elif not temp_text.startswith(token.text) and temp_text.count(token.text) == token_counter:
                            token_counter = 0
                            count = 0
                            temp_text = "x"
                    else:
                        count = 0
                        temp_text = "x"
                continue
            # check if token is not in previous text
            if token.text not in temp_text:
                line = f1.readline()
                token_counter = 0
                count = 0
                temp_text = "x"
                # check if line is new line
                if line == '\n' or not line:
                    f2.write("\n")
                    line = f1.readline()
            else:
                continue
            # check if token is in current line
            if token.text in line.strip("\n") and count == 1:
                continue
            else:
                # retrieve the first word of the line from conll format
                mod_line = line.strip("\n").split(" ", 2)
                # check if token is same as the first word of the current line
                if token.text == mod_line[0]:
                    z = line.replace("-X-", token.tag_)
                    f2.write(z)
                    # print("writing ... "+z)
                # check if token is a subset of the first word of the current line
                elif token.text in mod_line[0] and count == 0:
                    temp_text = mod_line[0]
                    z = line.replace("-X-", token.tag_)
                    f2.write(z)
                    count = 1
                else:
                    doc = nlp(mod_line[0])
                    for token in doc:
                        f2.write(line.replace("-X-", token.tag_))
    print("\nNew dataset can be found in " + resultPath + "-POS")
    print("\n**************** Adding POS Tags Completed ****************")


def graphicalDisplay(resultPath):
    """ Function used to display the plot chart used for presentation
    """
    try:
        print("\n**************** Commencing Chart Generation ****************")
        f1 = open(resultPath, 'r')
        id_list = ['raw text']
        label_list = ['raw text']
        ner_tag_list = ['-']
        next(f1)
        str_list = []
        for line in f1:
            if line != "\n":
                if line.split()[3] != "O":
                    if line.split()[3].startswith("B-") or line.split()[3].startswith("U-"):
                        if str_list:
                            if str_list[-1] not in label_list:
                                label_list.append(str_list[-1])
                            else:
                                ner_tag_list.pop()
                                id_list.pop()
                        str_list.append(line.split()[0])
                        id_list.append(str(str_list.index(line.split()[0])))
                        ner_tag_list.append(line.split()[3][2:])
                    elif line.split()[3].startswith("I-") or line.split()[3].startswith("L-"):
                        str_list[-1] += " " + line.split()[0]

        label_list.append(str_list[-1])

        nodes = [
            {'data': {'id': id_no, 'label': label, "NER-tag": ner_tag}}
            for id_no, label, ner_tag in zip(id_list, label_list, ner_tag_list)
        ]

        edges = [
            {'data': {'source': 'raw text', 'target': target, "NER-tag": ner_tag}}
            for target, ner_tag in zip(id_list[1:], ner_tag_list[1:])
        ]

        app = dash.Dash(__name__)

        app.layout = html.Div([
            cyto.Cytoscape(
                id='cytoscape-two-nodes',
                layout={'name': 'concentric'},
                style={'width': '100%', 'height': '100vh'},
                elements=nodes + edges,
                stylesheet=[
                    # Class selectors
                    {
                        'selector': 'node',
                        'style': {'label': 'data(label)', 'background-color': 'white'}
                    },
                    {
                        'selector': '[ NER-tag = "PER" ]',
                        'style': {'background-color': 'blue', 'line-color': 'blue'}
                    },
                    {
                        'selector': '[ NER-tag = "ORG" ]',
                        'style': {'background-color': 'yellow', 'line-color': 'yellow'}
                    },
                    {
                        'selector': '[ NER-tag = "LOC" ]',
                        'style': {'background-color': 'green', 'line-color': 'green'}
                    },
                    {
                        'selector': '[ NER-tag = "EXPLOITS" ]',
                        'style': {'background-color': 'red', 'line-color': 'red'}
                    },
                    {
                        'selector': '[ NER-tag = "MALWARE" ]',
                        'style': {'background-color': 'purple', 'line-color': 'purple'}
                    },
                    {
                        'selector': '[ NER-tag = "VENDOR" ]',
                        'style': {'background-color': 'orange', 'line-color': 'orange'}
                    },
                    {
                        'selector': '[ NER-tag = "DEVICES" ]',
                        'style': {'background-color': 'black', 'line-color': 'black'}
                    },
                    {
                        'selector': '[ NER-tag = "NETWORK" ]',
                        'style': {'background-color': 'pink', 'line-color': 'pink'}
                    },
                    {
                        'selector': '[ NER-tag = "COMMANDS" ]',
                        'style': {'background-color': 'grey', 'line-color': 'grey'}
                    },
                    {
                        'selector': '[ NER-tag = "APT" ]',
                        'style': {'background-color': 'brown', 'line-color': 'brown'}
                    },
                    {
                        'selector': '[ NER-tag = "CYBERSEC" ]',
                        'style': {'background-color': 'aqua', 'line-color': 'aqua'}
                    },

                ]
            )
        ])

        app.run_server(debug=True)
        print("\n**************** Chart Generation Complete ****************")
    except Exception as e:
        print("Unable to display chart. Something went wrong")
        print("error message: "+e)
        print("\n**************** Chart Generation Stopped ****************")
        sys.exit(1)

# ********** Main Functions **********
def main() -> None:
    if args.dataset_check: 
        if args.filepath: dataset_check(args.filepath)
        else: 
            logging.error('specify the path of the file for dataset check with -f option')
            sys.exit(1)
    if args.conversion: 
        if args.filepath: csvToJSON(args.filepath, conversionOutputPath)
        else: 
            logging.error('specify the path of the CSV file for conversion with -f option')
            sys.exit(1)
    if args.pos_format: 
        if args.filepath: POSformat(args.filepath)
        else: 
            logging.error('specify the path of the dataset to append POS tag with -f option')
            sys.exit(1)
    if args.train: 
        if args.config: train(args.train, modelPath, args.config)
        else: 
            logging.error('specify configuration file for training with -c option')
            sys.exit(1)
    if args.predict: 
        if args.filepath: predict(args.filepath, modelPath, outputPath)
        else: 
            logging.error('specify the path of the file for prediction with -f option')
            sys.exit(1)
    if args.visual_graph: 
        if args.filepath: graphicalDisplay(args.visual_graph)
        else: 
            logging.error('specify the path of the dataset for generation of knowledge graph with -f option')
            sys.exit(1)

if __name__ == '__main__': main()

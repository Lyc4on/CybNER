import dash
import dash_cytoscape as cyto
from dash import html

f1 = open('data/test.txt','r')
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
                    if str_list[-1] not in label_list: label_list.append(str_list[-1])
                    else:
                        ner_tag_list.pop()
                        id_list.pop()
                str_list.append(line.split()[0])
                id_list.append(str(str_list.index(line.split()[0])))
                ner_tag_list.append(line.split()[3][2:])
            elif line.split()[3].startswith("I-") or line.split()[3].startswith("L-"):
                str_list[-1] += " "+line.split()[0]
             
label_list.append(str_list[-1])

nodes = [
    { 'data': {'id': id_no, 'label': label, "NER-tag": ner_tag}}
    for id_no, label, ner_tag in zip(id_list, label_list, ner_tag_list)
]

edges = [
    {'data': {'source': 'raw text', 'target': target, "NER-tag": ner_tag}}
    for target, ner_tag in zip(id_list[1:],ner_tag_list[1:])
]

app = dash.Dash(__name__)

app.layout = html.Div([
    cyto.Cytoscape(
        id='cytoscape-two-nodes',
        layout={'name': 'concentric'},
        style={'width': '100%', 'height': '100vh'},
        elements = nodes + edges,
        stylesheet=[
            # Class selectors
            {
                'selector': 'node',
                'style': {'label': 'data(label)', 'background-color': 'white'}
            },
            {
                'selector': '[ NER-tag = "PER" ]',
                'style': { 'background-color': 'blue', 'line-color': 'blue'}
            },
            {
                'selector': '[ NER-tag = "ORG" ]',
                'style': {'background-color': 'yellow', 'line-color': 'yellow' }
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
                'style': {'background-color': 'pink', 'line-color': 'orange'}
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

if __name__ == '__main__':
    app.run_server(debug=True)
    
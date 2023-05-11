import os
import json
import pandas as pd
from templates.data_to_text import Data2TextTemplates
import argparse
from tqdm import tqdm

def _generate(args, batch, ids):


    template_list ={
        'Fluency': [
            _task.jumble,
            _task.subject_verb_dis,
            _task.typos,
            _task.remove_punct,
            _task.drop_stopwords,
            _task.add_negation,  
            _task.hyponyms,
            _task.drop_adjectives
        ],
        'Invariance' : [
            _task.synonym_adjective,
            _task.antonym_adjective,
            _task.contractions,
            _task.expansions,
            _task.number2words
        ],
        'Correctness':[
            _task.change_names,
            _task.change_numeric,
            _task.add_negation,  
        ],
        'Relevance':[
            _task.change_names,
            _task.change_numeric
        ],
        'Coverage':[
            _task.drop_phrases,
            _task.repeat_phrases
        ]
    }
    
    templates = [j for i in template_list.values() for j in i]
    for operand in tqdm(templates):
        out = map(operand, batch)
        for i,j,k in zip(out, batch, ids):
            if i ==j:
                continue
            data.append({'type':operand.__name__,'id':k, 'reference': j, 'perturbed': i.encode('utf-8').decode('utf-8')})
      
    with open('outputs/' + args.output_file + '.jsonl' , 'w') as fp:
        for i in data:
            json.dump(i, fp)
            fp.write("\n")
    fp.close()

if __name__ =='__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--ref_file', type=str, help='input reference file(supports cvs/jsonl')
    parser.add_argument('--output_file', default='output.jsonl', type=str, help='output file')
    args = parser.parse_args()
    
    batch =[]
    ids =[]
    with open(args.ref_file, 'r', encoding='utf-8') as f:
        for line in f:
            data = json.loads(line)
            try:
                batch.append(data['references'])
                ids.append(data['id'])
            except KeyError as msg:
                print(msg,'please format the input file correctly')
                exit()
    f.close()

    _generate(args, batch, ids)
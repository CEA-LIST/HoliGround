from typing import Any


from engine.utils.indexer import IndexedJSONL
from engine.utils.utils import *

from tqdm import tqdm

if __name__ == "__main__":

    questions = IndexedJSONL('data/gqa/questions/balanced/val_balanced_questions.jsonl', primary_key='question_id')

    unique_query_args = set()

    for qid, data in tqdm(questions.items(), total=len(questions)):
        semantic = data['semantic']
        for step in semantic:
            op = step.get('operation')
            if 'filter' in op:
                unique_query_args.add(step.get('argument'))
                # print(data['semanticStr'])


    print(f"All unique query arguments ({len(unique_query_args)}):")
    for arg in sorted(unique_query_args):
        print(arg)


        # print(data['semantic'], data['question'], qid, image_id, "\n")
    
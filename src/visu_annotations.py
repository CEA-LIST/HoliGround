from utils.indexer import IndexedJSONL
from tqdm import tqdm


if __name__ == "__main__":

    annotations = IndexedJSONL('output/annotations.jsonl', primary_key='question_id', force_rebuild=True)

    for qid, data in tqdm(annotations.items(), total=len(annotations)):
        image_id = data['image_id']

        reasoning_steps = data['reasoning_steps']

        
        print(f"{data['question']}\n")
        
        rationales = ""
        for step in reasoning_steps:
            rationales += f"{step['operation']} {' '*(10-len(step['operation']))} |  {step['rationale']}\n" 

        print(rationales)
     
        print(f"{data['answer']}\n")
        print("-"*100)
        print("\n")
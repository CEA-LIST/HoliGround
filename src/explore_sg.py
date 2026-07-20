from engine.utils.indexer import IndexedJSONL
from engine.utils.utils import *

if __name__ == "__main__":

    scene_graphs = IndexedJSONL('data/gqa/scene_graphs/val_sceneGraphs.jsonl', primary_key='image_id')
    print(len(scene_graphs))

    # unique_attributes = set()

    data = scene_graphs.get('n23181')
    print(data)
    # a = data['objects']

    # for key, obj in a.items():
    #     print(f"{key}: {obj}")
    #     print("\n")

    # for qid, data in tqdm(scene_graphs.items(), total=len(scene_graphs)):
    #     objects = data['objects']
    #     for obj in objects.values():
    #         print(obj['x'])
    
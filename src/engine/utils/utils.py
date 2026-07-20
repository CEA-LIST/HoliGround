import json
import ijson
import re
from engine.reasoning.context import ReasoningStep, SceneObject
from engine.utils.exceptions import *
import engine.ontology.attributes as ontology_attributes


def get_answer_complexity(structural_type):
    if structural_type in {"choose", "logical", "compare", "verify"}:
        return "1"
    else:
        return "2"

def get_object_category(bbox):
    """
    Categorizes objects by pixel area based on bounding box dimensions.
    
    Args:
        bbox: A list of 4 values [x, y, w, h] where w and h are the width and height in pixels.
    
    Returns:
        str: Category label - "S" (Small), "M" (Medium), or "L" (Large)
    
    Categories:
        - S (Small): Area < 32x32 px (1024 px²) - Smaller than a generic app icon
        - M (Medium): 32² < Area < 96² px (1024 < Area < 9216 px²) - Between an icon and a post-it note
        - L (Large): Area > 96x96 px (9216 px²) - Anything larger than a post-it note
    """
    _, _, w, h = bbox
    area = w * h
    
    if area < 32 * 32:  # Area < 1024 px²
        return "S"
    elif area < 96 * 96:  # Area < 9216 px²
        return "M"
    else:  # Area >= 9216 px²
        return "L"


def convert_to_jsonl(input_json, output_jsonl, key_name):

    print(f"Converting {input_json} -> {output_jsonl}...")
    print(f"Dict keys will be stored as {key_name} in each entry.")

    count = 0
    
    with open(input_json, 'rb') as f_in, open(output_jsonl, 'w', encoding='utf-8') as f_out:
        
        for key, data in ijson.kvitems(f_in, ''):
            
            data[key_name] = key
            
            # Write single line
            f_out.write(json.dumps(data) + '\n')
            
            count += 1
            if count % 50000 == 0:
                print(f"  Converted {count} lines...")

    print(f"Conversion complete. Total lines: {count}")


def get_all_operations(semantic):
    return set([step['operation'] for step in semantic])


def normalize_bbox(bbox, img_w, img_h, round_to_decimal_places=2):
    """
    Normalizes the bounding box to the range [0, 1].
    Rounding to the specified decimal places.
    """
    x, y, w, h = bbox
    return [round(x / img_w, round_to_decimal_places), 
            round(y / img_h, round_to_decimal_places), 
            round(w / img_w, round_to_decimal_places), 
            round(h / img_h, round_to_decimal_places)]


def get_object_from_dependency_step(dependency_step: ReasoningStep) -> SceneObject:
    """Return the primary object referenced by a dependency step."""
    if dependency_step.operation == 'relate': 
        _, _, id_type, _ = relation_parser(dependency_step.argument)
        if id_type == 'o':
            return dependency_step.objects[0]
        else:
            return dependency_step.objects[1]
    return dependency_step.objects[-1]


def select_parser(arg):
    pattern = r"^\s*(.*?)\s*\(\s*(.*?)\s*\)\s*$"
    match = re.match(pattern, arg, re.DOTALL)
    if match:
        name = match.group(1)
        obj_id = match.group(2)
        return name, obj_id
    else:
        raise ObjectNotSupported(f"Invalid argument: {arg}")
    

def relation_parser(arg):
    pattern = r"^\s*(.*?)\s*\(\s*(.*?)\s*\)\s*$"
    match = re.match(pattern, arg, re.DOTALL)
    if match:
        obj_name, relation, id_type = match.group(1).split(',')
        obj_id = match.group(2)
        obj_name = obj_name if obj_name != "_" else None
        return obj_name, relation, id_type, obj_id
    else:
        raise ValueError(f"Invalid argument: {arg}")


def get_attributes(attributes, bbox, img_w, img_h):
    attr_to_keep = dict()
    attr_to_keep["other_attributes"] = list()
    
    for attr in attributes:
        if attr in ontology_attributes.COLORS:
            attr_to_keep['color'] = attr
        if attr in ontology_attributes.SHAPES:
            attr_to_keep['shape'] = attr
        if attr in ontology_attributes.MATERIALS:
            attr_to_keep['material'] = attr
        # DEV: for now, keep all other attributes
        attr_to_keep['other_attributes'].append(attr)

    attr_to_keep['hposition'] = get_bbox_horizontal_location_xywh(bbox, img_w, img_h)
    attr_to_keep['vposition'] = get_bbox_vertical_location_xywh(bbox, img_w, img_h)
    return attr_to_keep if len(attr_to_keep) > 0 else None


def get_dummy_object(name) -> SceneObject:
    return SceneObject(
        id="-1",
        name=name,
        name_in_question=name,
        bbox=None,
        category=None,
        complexity=None
    )


def build_object(obj, obj_id, name_in_question, img_w, img_h, round_to_decimal_places, do_normalize_bbox, complexity = "1"):
    bbox = [obj['x'], obj['y'], obj['w'], obj['h']]
    category = get_object_category(bbox)
    if do_normalize_bbox:
        bbox = normalize_bbox(bbox, img_w, img_h, round_to_decimal_places)
    return SceneObject(
        id=obj_id,
        name=obj.get('name'),
        name_in_question=name_in_question,
        bbox=bbox,
        category=category,
        complexity=complexity
    )

def get_relations(obj: SceneObject, obj_id):
    if not obj.relations:
        return []
    return [rel['name'] for rel in obj.relations if rel['object'] == obj_id]


def get_bbox_vertical_location_xywh(normalized_bbox_xywh, image_width, image_height):
    """
    Converts a normalized bounding box (x, y, w, h) to pixel coordinates
    and determines if it is located on the 'top', 'middle', or 'bottom' third
    of the image.

    Args:
        normalized_bbox_xywh (tuple/list): A sequence (x, y, w, h) where values are 0.0 to 1.0.
        image_width (int): The absolute width of the image in pixels.
        image_height (int): The absolute height of the image in pixels.

    Returns:
        str: "top", "middle", or "bottom".
    """
    if len(normalized_bbox_xywh) != 4:
        raise ValueError("Normalized bbox must contain 4 values: x, y, w, h")
    if image_height <= 0:
        raise ValueError("Image height must be greater than zero.")

    _, y_norm, _, h_norm = normalized_bbox_xywh

    # Convert to absolute coordinates
    top_pixel = y_norm * image_height
    bottom_pixel = (y_norm + h_norm) * image_height

    bbox_center_y = (top_pixel + bottom_pixel) / 2

    upper_third = image_height / 3
    lower_third = 2 * image_height / 3

    if bbox_center_y < upper_third:
        return "top"
    if bbox_center_y < lower_third:
        return "middle"
    return "bottom"


def get_bbox_horizontal_location_xywh(normalized_bbox_xywh, image_width, image_height):
    """
    Converts a normalized bounding box (x, y, w, h) to pixel coordinates
    and determines if it is located on the 'left', 'center', or 'right' third
    of the image.

    Args:
        normalized_bbox_xywh (tuple/list): A sequence (x, y, w, h) where values are 0.0 to 1.0.
        image_width (int): The absolute width of the image in pixels.
        image_height (int): The absolute height of the image in pixels.

    Returns:
        str: "left", "center", or "right".
    """
    if len(normalized_bbox_xywh) != 4:
        raise ValueError("Normalized bbox must contain 4 values: x, y, w, h")
    if image_width <= 0:
        raise ValueError("Image width must be greater than zero.")

    x_norm, _, w_norm, _ = normalized_bbox_xywh

    left_pixel = x_norm * image_width
    right_pixel = (x_norm + w_norm) * image_width
    bbox_center_x = (left_pixel + right_pixel) / 2

    left_third = image_width / 3
    right_third = 2 * image_width / 3

    if bbox_center_x < left_third:
        return "left"
    if bbox_center_x < right_third:
        return "center"
    return "right"
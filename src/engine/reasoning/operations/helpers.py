from __future__ import annotations

from typing import Dict

from engine.reasoning.context import SceneObject, StepContext
from engine.utils.exceptions import ObjectNotInSceneGraph
from engine.utils.utils import build_object, get_attributes, get_dummy_object


def load_scene_object(ctx: StepContext, obj_id: str, obj_name: str | None) -> SceneObject:
    
    sg_objects: Dict[str, Dict] = ctx.scene_graph['objects']
    img_w, img_h = ctx.scene_graph.get('width'), ctx.scene_graph.get('height')

    obj = sg_objects.get(obj_id)

    if obj is None:
        if obj_id == "-":
            return get_dummy_object(obj_name or "unknown")
        raise ObjectNotInSceneGraph(f"Object {obj_id} not found in scene graph {ctx.scene_graph.get('image_id')}")

    return build_object(
        obj,
        obj_id,
        obj_name or obj.get('name', 'unknown'),
        img_w,
        img_h,
        ctx.config.round_to_decimal_places,
        ctx.config.normalize_bbox,
    )



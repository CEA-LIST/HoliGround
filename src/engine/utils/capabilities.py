from enum import Enum

class Capabilities(Enum):
    # perception capabilities
    # - coarse perception
    SceneUnderstanding = "SceneUnderstanding"

    # - fine-grained perception (singe-instance)
    ObjectLocalization = "ObjectLocalization"
    AttributeRecognition = "AttributeRecognition"
    SpatialRecognition = "SpatialRecognition"
    ActionRecognition = "ActionRecognition"

    # - fine-grained perception (cross-instance)
    SpatialRelation = "SpatialRelation"
    PhysicalRelation = "PhysicalRelation"
    
    # ObjectRetrieval = "ObjectRetrieval" (filter)

    def to_dict(self):
        return {"type": self.value}

    def __repr__(self):
        return f"{self.value}"
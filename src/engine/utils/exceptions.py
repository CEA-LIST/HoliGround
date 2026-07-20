class OperationNotSupported(Exception):
    pass

class ObjectNotInSceneGraph(Exception):
    pass

class LogicalOperationNotSupported(Exception):
    pass

class RelationNotFound(Exception):
    pass

class ObjectNotSupported(Exception):
    pass

class SubTypeNotSupported(Exception):
    pass

class ArgumentNotFound(Exception):
    pass

class AttributeNotFound(Exception):
    pass

class StopQuestionProcessing(Exception):
    """Raised when a handler decides to halt further processing for the question."""
    pass
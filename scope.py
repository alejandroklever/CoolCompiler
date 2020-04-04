class VariableInfo:
    def __init__(self, name, typex):
        self.name = name
        self.type = typex


class FunctionInfo:
    def __init__(self, name, params, return_type, typex=None):
        self.name = name
        self.params = params
        self.return_type = return_type
        self.type = typex


class ClassInfo:
    def __init__(self):
        pass


class Scope:
    def __init__(self, parent=None):
        self.variables = {}
        self.functions = {}
        self.classes = {}
        self.parent = parent

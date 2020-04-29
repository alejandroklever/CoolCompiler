from scope import Context


def fix_self_type(context: Context, errors=[]):
    types = [a[1] for a in context.types.items()]
    ts = []
    visited = set()
    for v in types:
        if v not in visited:
            visit(v, ts, visited)
    # Checking circular dependencies in the topological sort
    visited = set()
    for v in ts:
        if v.parent is not None and v.parent not in visited:
            errors.append(f'Not valid parent for class "{v.name}".')
        visited.add(v)
    # Setting all self_type methods and attributes
    self_type = context.get_type('SELF_TYPE')
    self_typed_methods = {t: [] for t in types}
    self_typed_attributes = {t: [] for t in types}
    for t in ts:
        for att in t.attributes:
            if att.type == self_type:
                self_typed_attributes[t].append(att)
        for func in t.methods:
            if func.return_type == self_type:
                self_typed_methods[t].append(func)
            else:
                for item2 in func.param_types:
                    if item2 == self_type:
                        self_typed_attributes[t].append(func)
                        break
        if t.parent is not None:
            for item in self_typed_methods[t.parent]:
                t.define_method(item.name, item.param_names, item.param_types, item.return_type)
            for item in self_typed_attributes[t.parent]:
                t.define_attribute(item.name, item.type)
    # replacing self_type
    for t in ts:
        for method in t.methods:
            for i, item2 in enumerate(method.param_types):
                if item2 == self_type:
                    method.param_types[i] = t
            if method.return_type == self_type:
                method.return_type = t
        for att in t.attributes:
            if att.type == self_type:
                att.type = t


def visit(v, ts, visited):
    visited.add(v)
    if v.parent is not None and v.parent not in visited:
        visit(v.parent, ts, visited)
    ts.append(v)


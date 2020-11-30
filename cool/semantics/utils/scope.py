from collections import OrderedDict
from typing import List, Optional, Dict, Tuple, Union


class SemanticError(Exception):
    @property
    def text(self):
        return self.args[0]


class Attribute:
    def __init__(self, name, typex):
        self.name: str = name
        self.type: 'Type' = typex

    def __str__(self):
        return f'[attrib] {self.name} : {self.type.name};'

    def __repr__(self):
        return str(self)


class Method:
    def __init__(self, name, param_names, params_types, return_type):
        self.name: str = name
        self.param_names: List[str] = param_names
        self.param_types: List['Type'] = params_types
        self.return_type: 'Type' = return_type

    def __str__(self):
        params = ', '.join(f'{n}: {t.name}' for n, t in zip(self.param_names, self.param_types))
        return f'[method] {self.name}({params}): {self.return_type.name};'

    def __eq__(self, other):
        return (other.name == self.name and
                other.return_type == self.return_type and
                tuple(other.param_types) == tuple(self.param_types))


class Type:
    def __init__(self, name: str):
        self.name: str = name
        self.attributes_dict: OrderedDict[str, Attribute] = OrderedDict()
        self.methods_dict: OrderedDict[str, Method] = OrderedDict()
        self.parent: Optional['Type'] = None

    @property
    def attributes(self):
        return [x for _, x in self.attributes_dict.items()]

    @property
    def methods(self):
        return [x for _, x in self.methods_dict.items()]

    def set_parent(self, parent: 'Type') -> None:
        if self.parent is not None:
            raise SemanticError(f'Parent type is already set for {self.name}.')
        self.parent = parent

    def get_attribute(self, name: str, get_owner: bool = False) -> Union[Attribute, Tuple[Attribute, 'Type']]:
        """
        Search the innermost declaration of the attribute with the given name and return it, if "get_owner" has
        value "True" the returned object is a tuple (attribute, type) where type is the innermost `Type` in th Type
        Hierarchy where the attribute is defined. If the method does not exist in the hierarchy then a SemanticError is
        raised.

        :param name: str, name of the attribute

        :param get_owner: bool, if has value "True" then a tuple (attribute, type) is returned else only the method is
        returned

        :return: the desired attribute and it's optional type owner.
        """
        try:
            return self.attributes_dict[name] if not get_owner else (self.attributes_dict[name], self)
        except KeyError:
            if self.parent is None:
                raise SemanticError(f'Attribute "{name}" is not defined in {self.name}.')
            try:
                return self.parent.get_attribute(name, get_owner)
            except SemanticError:
                raise SemanticError(f'Attribute "{name}" is not defined in {self.name}.')

    def define_attribute(self, name: str, typex: 'Type') -> Attribute:
        try:
            self.get_attribute(name)
        except SemanticError:
            attribute = Attribute(name, typex)
            self.attributes_dict[name] = attribute
            return attribute
        else:
            raise SemanticError(f'Attribute "{name}" is already defined in {self.name}.')

    def contains_attribute(self, name: str) -> bool:
        return name in self.attributes_dict or self.parent is not None and self.parent.contains_attribute(name)

    def get_method(self, name: str, get_owner: bool = False) -> Union[Method, Tuple[Method, 'Type']]:
        """
        Search the innermost declaration of the method with the given name and return it, if "get_owner" has
        value "True" the returned object is a tuple (method, type) where type is the innermost `Type` in th Type
        Hierarchy where the methods is defined. If the method does not exist in the hierarchy then a SemanticError is
        raised

        :param name: str, name of the method

        :param get_owner: bool, if has value "True" then a tuple (method, type) is returned else only the method is
        returned

        :return: the desired method and it's optional type owner.
        """
        try:
            return self.methods_dict[name] if not get_owner else (self.methods_dict[name], self)
        except KeyError:
            if self.parent is None:
                raise SemanticError(f'Method "{name}" is not defined in {self.name}.')
            try:
                return self.parent.get_method(name, get_owner)
            except SemanticError:
                raise SemanticError(f'Method "{name}" is not defined in {self.name}.')

    def define_method(self, name: str,
                      param_names: List[str],
                      param_types: List['Type'],
                      return_type: 'Type') -> Method:
        if name in self.methods_dict:
            raise SemanticError(f'Method "{name}" already defined in {self.name}')

        method = Method(name, param_names, param_types, return_type)
        self.methods_dict[name] = method
        return method

    def contains_method(self, name) -> bool:
        return name in self.methods_dict or (self.parent is not None and self.parent.contains_method(name))

    def all_attributes(self) -> List[Tuple[Attribute, 'Type']]:
        attributes = [] if self.parent is None else self.parent.all_attributes()
        attributes += [(x, self) for x in self.attributes]
        return attributes

    def all_methods(self) -> List[Tuple[Method, 'Type']]:
        methods = [] if self.parent is None else self.parent.all_methods()
        methods += [(x, self) for x in self.methods]
        return methods

    def conforms_to(self, other: 'Type') -> bool:
        return other.bypass() or self == other or self.parent is not None and self.parent.conforms_to(other)

    def join(self, other: 'Type') -> 'Type':
        self_ancestors = set(self.get_ancestors())

        current_type = other
        while current_type is not None:
            if current_type in self_ancestors:
                break
            current_type = current_type.parent
        return current_type

    @staticmethod
    def multi_join(types: List['Type']) -> 'Type':
        static_type = types[0]
        for t in types[1:]:
            static_type = static_type.join(t)
        return static_type

    def bypass(self) -> bool:
        return False

    def get_ancestors(self):
        if self.parent is None:
            return [self]
        return [self] + self.parent.get_ancestors()

    def __str__(self):
        output = f'type {self.name}'
        parent = '' if self.parent is None else f' : {self.parent.name}'
        output += parent
        output += ' {'
        output += '\n\t' if self.attributes or self.methods else ''
        output += '\n\t'.join(str(x) for x in self.attributes)
        output += '\n\t' if self.attributes_dict else ''
        output += '\n\t'.join(str(x) for x in self.methods)
        output += '\n' if self.methods_dict else ''
        output += '}\n'
        return output

    def __repr__(self):
        return str(self)


class ErrorType(Type):
    def __init__(self):
        super().__init__('Error')

    def conforms_to(self, other):
        return True

    def bypass(self):
        return True

    def __eq__(self, other):
        return isinstance(other, Type)


class Context:
    def __init__(self):
        self.types: Dict[str, Type] = {}

    def create_type(self, name: str) -> Type:
        if name in self.types:
            raise SemanticError(f'Type with the same name ({name}) already in context.')
        typex = self.types[name] = Type(name)
        return typex

    def get_type(self, name: str) -> Type:
        try:
            return self.types[name]
        except KeyError:
            raise SemanticError(f'Type "{name}" is not defined.')

    def __str__(self):
        return '{\n\t' + '\n\t'.join(y for x in self.types.values() for y in str(x).split('\n')) + '\n}'

    def __repr__(self):
        return str(self)

    def __iter__(self):
        return iter(self.types.values())


class VariableInfo:
    def __init__(self, name, var_type):
        self.name: str = name
        self.type: Type = var_type

    def __str__(self):
        return self.name + ': ' + self.type.name


class Scope:
    def __init__(self, parent: Optional['Scope'] = None):
        self.locals: Dict[str, VariableInfo] = {}
        self.parent: Optional['Scope'] = parent
        self.children: List[Scope] = []

    def create_child(self) -> 'Scope':
        child = Scope(self)
        self.children.append(child)
        return child

    def define_variable(self, var_name: str, var_type: Type) -> VariableInfo:
        info = VariableInfo(var_name, var_type)
        self.locals[var_name] = info
        return info

    def find_variable(self, var_name: str) -> Optional[VariableInfo]:
        try:
            return self.locals[var_name]
        except KeyError:
            return self.parent.find_variable(var_name) if self.parent is not None else None

    def is_defined(self, var_name) -> bool:
        return self.find_variable(var_name) is not None

    def is_local(self, var_name: str) -> bool:
        return var_name in self.locals

    def clear(self):
        self.children = []

    def __len__(self):
        return len(self.locals)

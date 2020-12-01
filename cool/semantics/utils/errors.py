ATTRIBUTE_OVERRIDE_ERROR = 'OverrideError: Attribute "%s" already defined in "%s", attributes cannot be overridden'
METHOD_OVERRIDE_ERROR = 'OverrideError: Method "%s" already defined in "%s" with a different signature.'

INCOMPATIBLE_TYPES = 'TypeError: Cannot convert "%s" into "%s".'
INVALID_PARAM_TYPE = 'TypeError: "%s" cannot be a static type of a parameter.'
INVALID_CASE_TYPE = 'TypeError: "%s" cannot be a static type of a case branch.'
INVALID_PARENT_TYPE = 'TypeError: Class "%s" cannot inherits from "%s"'
INVALID_ANCESTOR = 'TypeError: Class "%s" has no an ancestor class "%s".'

INVALID_BINARY_OPERATION = 'OperationError: Operation "%s" is not defined between "%s" and "%s".'
INVALID_UNARY_OPERATION = 'OperationError: Operation "%s" is not defined for "%s".'

SELF_IS_READONLY = 'IdentifierError: Variable "self" is read-only.'
SELF_INVALID_ATTRIBUTE_ID = 'IdentifierError: Cannot set "self" as attribute of a class.'
SELF_INVALID_PARAM_ID = 'IdentifierError: Cannot set "self" as parameter of a method.'
LOCAL_ALREADY_DEFINED = 'IdentifierError: Variable "%s" is already defined in method "%s".'
VARIABLE_NOT_DEFINED = 'IdentifierError: Variable "%s" is not defined in "%s".'

INFERENCE_ERROR_ATTRIBUTE = 'InferenceError: Cannot infer type for attribute "%s".'
INFERENCE_ERROR_PARAMETER = 'InferenceError: Cannot infer type for parameter "%s".'
INFERENCE_ERROR_VARIABLE = 'InferenceError: Cannot infer type for variable "%s".'
INFERENCE_ERROR_METHOD = 'InferenceError: Cannot infer return type for method "%s".'


DIVIDE_BY_ZERO = 'ZeroDivisionError: Division by zero.'
INPUT_INT_ERROR = 'InputError: Expected a number.'
MAIN_CLASS_NOT_FOUND = 'MainClassNotFound: no Main class in program.'
MAIN_METHOD_NOT_FOUND = 'MainMethodNotFound: no main method in class Main.'
VOID_EXPRESSION = 'VoidReferenceError: Object reference not set to an instance of an object.'
CASE_OF_ERROR = 'CaseOfError: No branch matches wit de dynamic type of the case expression.'

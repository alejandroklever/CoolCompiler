"""This module contains definitions of classes for make different travels through the AST of a cool program. All
classes defined here follows the visitor pattern using the module visitor, with this we can get a more decoupled
inspection. """

from semantics.collector import TypeCollector
from semantics.builder import TypeBuilder
from semantics.overridden import OverriddenMethodChecker, topological_ordering
from semantics.selftype import SelfTypeReplacement
from semantics.type_checker import TypeChecker
from semantics.formatter import Formatter

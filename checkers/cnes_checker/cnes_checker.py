# Copyright (c) 2015 LOGILAB S.A. (Paris, FRANCE).
# http://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
"""CNES checker for Python code"""

from collections import defaultdict
import re
import os

import astroid
from astroid.exceptions import InferenceError
from pylint.extensions import docparams
from pylint.checkers import BaseChecker, BaseTokenChecker
from pylint.checkers import utils
from pylint.checkers.raw_metrics import get_type
from pylint.constants import WarningScope
import tokenize


class DesignChecker(BaseChecker):
    """Checks for multiple exit statements in loops"""

    name = 'design'
    msgs = {'R5101': ('More than one exit statement for this loop',
                      'multiple-exit-statements',
                      'Used when there is more than one possible exit '
                      'statement for a loop (either break or return '
                      'statements)'),
            'R5102': ('Too many decorators for this function (%s/%s)',
                      'too-many-decorators',
                      'Used when too many decorators are applied on a function'),
            'R5103': ('Exit condition based on equality or difference',
                      'bad-exit-condition',
                      'Used when the exit condition of a loop uses an '
                      'equality or a difference comparison.'),
            'R5104': ('%s is named after a built-in, consider renaming it',
                      'builtin-name-used',
                      'Used when an attribute or a method is named after a '
                      'built-in. This makes the code more difficult to read.'),
            'R5105': ('Consider not using recursion',
                      'recursive-call',
                      'Used when direct recursion is used in a function or a'
                      'method. It can lead to a dangerous behaviour if the'
                      'depth is not known.'),
            'R5106': ('Consider %s within a context manager',
                      'use-context-manager',
                      'Used when a file is opened or a lock is acquired without'
                      'context manager. This is error-prone because one can'
                      'forget closing or releasing it.'),
           }

    options = (('max-decorators',
                {'default': 5,
                 'type': 'int', 'metavar': '<num>',
                 'help': 'Maximum number of decorators allowed per function.'}
               ),
              )

    def __init__(self, linter=None):
        BaseChecker.__init__(self, linter)
        self.config = linter.config
        self._exit_statements = []

    def visit_for(self, node):
        self._exit_statements.append(0)

    @utils.only_required_for_messages('use-context-manager')
    def visit_attribute(self, node):
        try:
            for infer in node.infer():
                if (not isinstance(infer, astroid.BoundMethod)
                        or infer.name != 'acquire'):
                    continue
                orig_module = infer.root()
                if (isinstance(orig_module, astroid.Module) and
                        orig_module.name == 'threading'):
                    self.add_message('use-context-manager', node=node,
                                     args='acquiring the lock')
                    return
        except InferenceError:
            pass

    @utils.only_required_for_messages('use-context-manager')
    def visit_call(self, node):
        try:
            for funcdef in node.func.infer():
                if funcdef.name == 'open':
                    parent = funcdef.parent
                    if (isinstance(parent, astroid.Module)
                            and parent.name == '_io'):
                        if not isinstance(node.parent, astroid.With):
                            self.add_message('use-context-manager', node=node,
                                             args='opening the file')
        except InferenceError:
            pass

    @utils.only_required_for_messages('bad-exit-condition')
    def visit_while(self, node):
        self._exit_statements.append(0)
        comparisons = None
        if isinstance(node.test, astroid.Compare):
            comparisons = [node.test]
        elif isinstance(node.test, astroid.BoolOp):
            comparisons = [comp for comp in node.test.values
                           if isinstance(comp, astroid.Compare)]
        if not comparisons:
            return
        for comp in comparisons:
            for ops in comp.ops:
                if ops[0] in ('!=', '=='):
                    self.add_message('bad-exit-condition', node=node)

    @utils.only_required_for_messages('multiple-exit-statements')
    def leave_for(self, node):
        if self._exit_statements[-1] > 1:
            self.add_message('multiple-exit-statements', node=node)
        self._exit_statements.pop()

    def visit_return(self, node):
        if self._exit_statements:
            self._exit_statements[-1] += 1

    visit_break = visit_return
    leave_while = leave_for

    @utils.only_required_for_messages('too-many-decorators')
    def visit_functiondef(self, node):
        max_decorators = getattr(self.config, 'max_decorators', self.options[0][1]['default'])
        if node.decorators:
            if len(node.decorators.nodes) > max_decorators:
                self.add_message('too-many-decorators', node=node,
                                 args=(len(node.decorators.nodes),
                                       max_decorators))
        for child in node.nodes_of_class(astroid.Call):
            try:
                for funcdef in child.func.infer():
                    if funcdef == node:
                        self.add_message('recursive-call', node=child)
                        break
            except:
                continue

    @utils.only_required_for_messages('builtin-name-used')
    def visit_classdef(self, node):
        for name, item in node.instance_attrs.items():
            self._check_node_name(node, item[0], name)
        for name, item in node.items():
            self._check_node_name(node, item, name)

    def _check_node_name(self, class_node, item, name):
        """Checks if `name` of `item` `class_node` member is the one of a builtin

        If yes, and if the item is not inherited from `class_node` ancestors,
        trigger a "builtin-name-used" message.
        """
        if name not in __builtins__:
            return
        for ancestor in class_node.ancestors():
            try:
                ancestor.getattr(name)
                return
            except astroid.exceptions.NotFoundError:
                pass
        self.add_message('builtin-name-used', node=item, args=(name,))


class CommentMetricsChecker(BaseTokenChecker):
    """Checks the ratio comments+docstrings/code lines by module and by function
    """
    
    # Theses values are hardcoded in pylint (and have changed in pylint 2.12)
    # We can't get them directly from the pylint lib :(
    LINE_TYPE_DOCSTRING = 'docstring'
    LINE_TYPE_COMMENT = 'comment'
    LINE_TYPE_CODE = 'code'
    LINE_TYPE_EMPTY = 'empty'
    LINE_TYPES = [LINE_TYPE_DOCSTRING, LINE_TYPE_CODE, LINE_TYPE_COMMENT, LINE_TYPE_EMPTY]
    
    name = 'commentmetrics'
    msgs = {'R5201': ('Too few comments (%s/%s %%)',
                      'too-few-comments',
                      'Used the ratio (comments+docstrings)/code_lines is '
                      'unsufficient for a function or a module.',
                      {'scope': WarningScope.NODE}
                     ),
           }
    
    options = (('min-func-comments-ratio',
                {'default': 30, 'type': 'int', 'metavar': '<int>',
                 'help': 'Minimum ratio (comments+docstrings)/code_lines for a '
                         'function (percentage).'}),
               ('min-module-comments-ratio',
                {'default': 30, 'type': 'int', 'metavar': '<int>',
                 'help': 'Minimum ratio (comments+docstrings)/code_lines for a '
                         'module (percentage).'}),
               ('min-func-size-to-check-comments',
                {'default': 10, 'type': 'int', 'metavar': '<int>',
                 'help': 'Minimum number of lines for a function from which '
                         'the comments ratio will be checked.'}),
              )

    def __init__(self, linter):
        BaseTokenChecker.__init__(self, linter)
        self.config = linter.config
        self._reset()

    def _reset(self):
        self._stats = {}
        self._global_stats = dict.fromkeys(self.LINE_TYPES, 0)

    def process_tokens(self, tokens):
        """update stats"""
        i = 0
        tokens = list(tokens)
        if tokens[0].type == tokenize.ENCODING:
            i = 1
        tail = None
        while i < len(tokens):
            start_line = tokens[i][2][0]
            i, lines_number, line_type = get_type(tokens, i)
            self._global_stats[line_type] += lines_number
            if tail and self._stats[tail][0] == line_type:
                self._stats[tail][1] += lines_number
            else:
                self._stats[start_line] = [line_type, lines_number]
                tail = start_line

    @utils.only_required_for_messages('too-few-comments')
    def visit_functiondef(self, node):
        min_func_comments_ratio = getattr(self.config, 'min_func_comments_ratio', self.options[0][1]['default'])
        min_func_size_to_check_comments = getattr(self.config, 'min_func_size_to_check_comments', self.options[2][1]['default'])
        nb_lines = node.tolineno - node.fromlineno
        if nb_lines <= min_func_size_to_check_comments:
            return
        func_stats = dict.fromkeys(self.LINE_TYPES, 0)
        for line in sorted(self._stats):
            if line > node.tolineno:
                break
            lines_number = self._stats[line][1]
            if line + lines_number - 1 >= node.fromlineno:
                l_type = self._stats[line][0]
                func_stats[l_type] += (min(node.tolineno,
                                           line + lines_number - 1)
                                       - max(node.fromlineno, line) + 1)
        if func_stats[self.LINE_TYPE_CODE] <= 0:
            return
        ratio = ((func_stats[self.LINE_TYPE_COMMENT] + func_stats[self.LINE_TYPE_DOCSTRING])
                 / float(func_stats[self.LINE_TYPE_CODE]) * 100)
        if ratio < min_func_comments_ratio:
            self.add_message('too-few-comments', node=node,
                            args=(f'{ratio:.2f}', min_func_comments_ratio))

    @utils.only_required_for_messages('too-few-comments')
    def visit_module(self, node):
        min_module_comments_ratio = getattr(self.config, 'min_module_comments_ratio', self.options[1][1]['default'])
        if self._global_stats[self.LINE_TYPE_CODE] <= 0:
            return
        ratio = ((self._global_stats[self.LINE_TYPE_COMMENT] +
                  self._global_stats[self.LINE_TYPE_DOCSTRING]) /
                 float(self._global_stats[self.LINE_TYPE_CODE]) * 100)
        if ratio < min_module_comments_ratio:
            self.add_message('too-few-comments', node=node,
                             args=(f'{ratio:.2f}', min_module_comments_ratio))


    def leave_module(self, node):
        self._reset()


class PathGraph(object):
    """Comes from mccabe module (see https://pypi.python.org/pypi/mccabe)
    """
    def __init__(self, node):
        self.root = node
        self.nodes = defaultdict(list)

    def connect(self, n1, n2):
        self.nodes[n1].append(n2)
        # Ensure that the destination node is always counted.
        self.nodes[n2] = []

    def complexity(self):
        """ Return the McCabe complexity for the graph V-E+2
        """
        num_edges = sum([len(n) for n in self.nodes.values()])
        num_nodes = len(self.nodes)
        return num_edges - num_nodes + 2


class McCabeASTVisitor(object):
    """Make a depth-first visit of a code node and build a graph accordingly

    Comes from mccabe module (see https://pypi.python.org/pypi/mccabe)
    """

    def __init__(self):
        self.node = None
        self._cache = {}
        self.classname = ""
        self.graphs = {}
        self.reset()
        self._bottom_counter = 0

    def default(self, node, *args):
        pass

    def reset(self):
        self.graph = None
        self.tail = None

    def dispatch(self, node, *args):
        self.node = node
        klass = node.__class__
        meth = self._cache.get(klass)
        if meth is None:
            className = klass.__name__
            meth = getattr(self.visitor, 'visit' + className, self.default)
            self._cache[klass] = meth
        return meth(node, *args)

    def dispatch_list(self, node_list):
        for node in node_list:
            self.dispatch(node)

    def preorder(self, tree, visitor, *args):
        """Do preorder walk of tree using visitor"""
        self.visitor = visitor
        visitor.visit = self.dispatch
        self.dispatch(tree, *args)

    def visitFunctionDef(self, node):
        if self.graph is not None:
            # closure
            pathnode = self._append_node(node)
            self.tail = pathnode
            self.dispatch_list(node.body)
            bottom = f"{self._bottom_counter}"
            self._bottom_counter += 1
            self.graph.connect(self.tail, bottom)
            self.graph.connect(node, bottom)
            self.tail = bottom
        else:
            self.graph = PathGraph(node)
            self.tail = node
            self.dispatch_list(node.body)
            self.graphs[f"{self.classname}{node.name}"] = self.graph
            self.reset()

    def visitClassDef(self, node):
        old_classname = self.classname
        self.classname += node.name + "."
        self.dispatch_list(node.body)
        self.classname = old_classname

    def visitSimpleStatement(self, node):
        self._append_node(node)

    visitAssert = visitAssign = visitAugAssign = visitDelete = visitPrint = \
        visitRaise = visitYield = visitImport = visitCall = visitSubscript = \
        visitPass = visitContinue = visitBreak = visitGlobal = visitReturn = \
        visitExpr = visitSimpleStatement

    def visitIf(self, node):
        name = f"If {node.lineno}"
        self._subgraph(node, name)

    def visitLoop(self, node):
        name = f"Loop {node.lineno}"
        self._subgraph(node, name)

    visitFor = visitWhile = visitLoop

    def visitTryExcept(self, node):
        name = f"TryExcept {node.lineno}"
        self._subgraph(node, name, extra_blocks=node.handlers)

    visitTry = visitTryExcept

    def visitWith(self, node):
        self._append_node(node)
        self.dispatch_list(node.body)

    def _append_node(self, node):
        if not self.tail:
            return
        self.graph.connect(self.tail, node)
        self.tail = node
        return node

    def _subgraph(self, node, name, extra_blocks=()):
        """create the subgraphs representing any `if` and `for` statements"""
        if self.graph is None:
            # global loop
            self.graph = PathGraph(node)
            self._subgraph_parse(node, extra_blocks)
            self.graphs[f"{self.classname}{name}"] = self.graph
            self.reset()
        else:
            self._append_node(node)
            self._subgraph_parse(node, extra_blocks)

    def _subgraph_parse(self, node, extra_blocks):
        """parse the body and any `else` block of `if` and `for` statements"""
        loose_ends = []
        self.tail = node
        self.dispatch_list(node.body)
        loose_ends.append(self.tail)
        for extra in extra_blocks:
            self.tail = node
            self.dispatch_list(extra.body)
            loose_ends.append(self.tail)
        if node.orelse:
            self.tail = node
            self.dispatch_list(node.orelse)
            loose_ends.append(self.tail)
        else:
            loose_ends.append(node)
        if node:
            bottom = f"{self._bottom_counter}"
            self._bottom_counter += 1
            for le in loose_ends:
                self.graph.connect(le, bottom)
            self.tail = bottom


class McCabeChecker(BaseChecker):
    """Checks for functions or methods having a high McCabe number"""

    name = 'mccabe'
    msgs = {'R5301': ('Too high cyclomatic complexity (mccabe %d/%d)',
                      'too-high-complexity',
                      'Used when the McCabe cyclomatic number is too high '
                      'for a function or a method.'),
            'R5302': ('Too high cyclomatic complexity (simplified mccabe %d/%d)',
                      'too-high-complexity-simplified',
                      'Used when the simplified McCabe cyclomatic number is'
                      'too high for a function or a method.'),
           }
    options = (('max-mccabe-number',
                {'default': 25, 'type': 'int', 'metavar': '<int>',
                 'help': 'Maximum McCabe cyclomatic number for a function or '
                         'a method'}),
               ('max-simplified-mccabe-number',
                {'default': 20, 'type': 'int', 'metavar': '<int>',
                 'help': 'Maximum simplified McCabe cyclomatic number for a '
                         'function or a method'}),
              )

    def __init__(self, linter=None):
        BaseChecker.__init__(self, linter)
        self.config = linter.config
        self.simplified_mccabe_number = []

    @utils.only_required_for_messages('too-high-complexity')
    def visit_module(self, node):
        max_mccabe_number = getattr(self.config, 'max_mccabe_number', self.options[0][1]['default'])
        visitor = McCabeASTVisitor()
        for child in node.body:
            visitor.preorder(child, visitor)
        for graph in visitor.graphs.values():
            complexity = graph.complexity()
            if complexity > max_mccabe_number:
                self.add_message('too-high-complexity', node=graph.root,
                                 args=(complexity,
                                       max_mccabe_number))

    def visit_functiondef(self, node):
        self.simplified_mccabe_number.append(0)

    @utils.only_required_for_messages('max-simplified-mccabe-number')
    def leave_functiondef(self, node):
        max_simplified_mccabe_number = getattr(self.config, 'max_simplified_mccabe_number', self.options[1][1]['default'])
        complexity = self.simplified_mccabe_number.pop()
        if complexity > max_simplified_mccabe_number:
            self.add_message('too-high-complexity-simplified', node=node,
                             args=(complexity,
                                   max_simplified_mccabe_number))

    def visit_while(self, node):
        if self.simplified_mccabe_number:
            self.simplified_mccabe_number[-1] += 1

    visit_for = visit_tryexcept = visit_tryfinally = visit_if \
            = visit_excepthandler = visit_while


class SphinxDocChecker(docparams.DocstringParameterChecker):
    """Checks sphinx documentation in docstrings"""

    name = 'sphinxdoc'
    msgs = docparams.DocstringParameterChecker.msgs.copy()
    msgs['W9095'] = ('"%s" field missing from %s docstring',
                     'missing-docstring-field',
                     'Used when an expected field is not present in the'
                     'docstring of a module, class, function or method')
    msgs['W9096'] = ('malformed "%s" field in %s docstring',
                     'malformed-docstring-field',
                     'Used when an expected field is not present in the'
                     'docstring of a module, class, function or method')
    msgs['W9097'] = ('description missing in %s docstring',
                     'missing-docstring-description',
                     'Used when no description exists for a docstring')

    regexp = {}
    for field in ('author', 'version', 'date'):
        regexp[field] = (re.compile(fr':{field}:'),
                         re.compile(fr':{field}: \S+'))

    @utils.only_required_for_messages('malformed-docstring-field', 'missing-docstring-field')
    def visit_module(self, node):
        if not hasattr(node, 'doc') :
            return
        if not node.doc:
            return
        for field, expr in self.regexp.values():
            self._check_docstring_field(node, field, expr)

    @utils.only_required_for_messages('malformed-docstring-field', 'missing-docstring-field')
    def visit_classdef(self, node):
        if not hasattr(node, 'doc') :
            return
        if not node.doc:
            return
        self._check_description_exists(node)

    @utils.only_required_for_messages('malformed-docstring-field', 'missing-docstring-field')
    def visit_functiondef(self, node):
        super(SphinxDocChecker, self).visit_functiondef(node)
        if not hasattr(node, 'doc') :
            return
        if not node.doc:
            return
        self._check_description_exists(node)

    def _check_description_exists(self, node):
        """Check docstring of node `node` contains a description part

        To do so, check the first line contains something
        """
        if not hasattr(node, 'doc') :
            return
        doc_lines = [line.strip() for line in node.doc.splitlines() if line]
        if not doc_lines or doc_lines[0].startswith(':'):
            self.add_message('missing-docstring-description', node=node,
                             args=node.name.split('.')[-1])

    def _check_docstring_field(self, node, field, expr):
        """Check `field` re exists in `node` docstring and the format is `expr`
        """
        if not expr.search(node.doc):
            if field.search(node.doc):
                msg = 'malformed-docstring-field'
            else:
                msg = 'missing-docstring-field'
            self.add_message(msg, node=node,
                             args=(field.pattern.replace(':', ''),
                                   node.name.split('.')[-1]))


class ForbiddenUsageChecker(BaseChecker):
    """Checks for use of forbidden functions or variables"""

    name = 'forbiddenusage'
    msgs = {'R5401': ('Consider dropping use of sys.exit()',
                      'sys-exit-used',
                      'Used when a call to sys.exit() is made out of __main__'
                      'scope.'
                     ),
            'R5402': ('Consider dropping use of os.%s',
                      'os-environ-used',
                      'Used when environment variables are accessed. A program'
                      'should not rely on its execution environment.'
                      'The project properties such as login, database access URL,'
                      'system properties, etc. could be managed using a properties'
                      'file (XML, YAML or JSON format). Python modules like'
                      '"configparser" (python version > 3.10.7) could be useful'
                      'to manage properties along the project development.'
                     ),
            'R5403': ('Consider using argparse module instead of sys.argv',
                      'sys-argv-used',
                      'Used when command line arguments are read from sys.argv'
                      'instead of using argparse module.'
                     ),
           }

    def __init__(self, linter=None):
        BaseChecker.__init__(self, linter)
        self._main_module = False
        self._authorized_exits = []

    def visit_module(self, node):
        if node.name.split('.')[-1] == '__main__':
            # this is the main module, tolerate calls to sys.exit in the module
            # scope
            self._main_module = True
            return
        for child in node.body:
            # look for a "if __name__ == '__main__'" in the module
            if not isinstance(child, astroid.If):
                continue
            if not isinstance(child.test, astroid.Compare):
                continue
            ops = child.test.as_string().split()
            if ops[:2] != ['__name__', '=='] or ops[2][1:-1] != '__main__':
                continue
            # find calls in __main__ scope: sys.exit() is authorized there
            for stmt in child.body:
                if not isinstance(stmt, astroid.Expr):
                    continue
                if not isinstance(stmt.value, astroid.Call):
                    continue
                call = stmt.value
                if self._is_sys_exit_call(call):
                    self._authorized_exits.append(call)

    @utils.only_required_for_messages('sys-exit-used')
    def visit_call(self, node):
        self._check_os_environ_call(node)
        if not self._is_sys_exit_call(node):
            return
        expr = node.parent
        if isinstance(expr.scope(), astroid.Module):
            if self._main_module or node in self._authorized_exits:
                return
        self.add_message('sys-exit-used', node=node)

    @utils.only_required_for_messages('os-environ-used', 'sys-argv-used')
    def visit_attribute(self, node):
        if self._check_access(node, ('os', os.name), 'environ', astroid.Dict):
            self.add_message('os-environ-used', node=node, args='environ')
        if self._check_access(node, ('sys',), 'argv', astroid.List):
            self.add_message('sys-argv-used', node=node)

    @utils.only_required_for_messages('os-environ-used', 'sys-argv-used')
    def visit_name(self, node):
        if self._check_access(node, ('os', os.name), 'environ', astroid.Dict,
                              False):
            self.add_message('os-environ-used', node=node, args='environ')
        if self._check_access(node, ('sys',), 'argv', astroid.List, False):
            self.add_message('sys-argv-used', node=node)

    def _check_access(self, node, modules, var, vtype, attribute=True):
        """Check if `node` (attribute if `attribute` else name) is `modules`.`var`

        In case it is, display `msg`
        """
        try:
            for infer in node.infer():
                if (not isinstance(infer, vtype)
                        or infer.name != var):
                    continue
                if attribute:
                    try:
                        orig = node.expr.inferred()[0]
                    except Exception:
                        continue
                else:
                    orig = infer.parent
                if isinstance(orig, astroid.Module) and orig.name in modules:
                    return True
        except InferenceError:
            pass
        return False

    def _is_sys_exit_call(self, node):
        """Return True if call node `node` is a call to sys.exit(), else False
        """
        try:
            for funcdef in node.func.infer():
                if (funcdef.name == 'exit'
                        and isinstance(funcdef.parent, astroid.Module)
                        and funcdef.parent.name == 'sys'):
                    return True
        except InferenceError:
            pass
        return False

    def _check_os_environ_call(self, node):
        """Return True if node `node` accesses os.environ, else False
        """
        try:
            for funcdef in node.func.infer():
                if (funcdef.name in ('putenv', 'getenv', 'unsetenv')
                        and funcdef.root().name in('os', os.name)):
                    self.add_message('os-environ-used', node=node,
                                     args=f"{funcdef.name}()")
                    return
        except InferenceError:
            pass
        return False


def register(linter):
    """required method to auto register this checker"""
    linter.register_checker(DesignChecker(linter))
    linter.register_checker(CommentMetricsChecker(linter))
    linter.register_checker(McCabeChecker(linter))
    linter.register_checker(SphinxDocChecker(linter))
    linter.register_checker(ForbiddenUsageChecker(linter))

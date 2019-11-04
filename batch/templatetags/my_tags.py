"""
Django模板有诸多限制，例如不能调用方法，不能执行任意的Python表达式。
它的设计者表示这样做是故意的，我不去争论这样到底是好是坏，但在调试时
我们确实需要想执行任意的Python表达式。Django提供了自定义标签的机制，
再加上Python的eval函数，使得在Django模板中也能执行任意的Python表达式。
这里写了三个标签，分别是set, print和import。
set的语法为：
{% set len = len(list) %}
length of list: {{ len }} <br />
{% set a = num + len %}
Now num value: {{ a }} <br />

print语法为：
length of list: {% print len(list) %} <br />
Now num value: {% print num + len %} <br />

import语法为：
{% import sys %}
{% print sys.path %} <br />
"""
from django import template
import re

register = template.Library()

set_regex = re.compile(r'^\s*set\s+(\w+)\s*=\s*(.*)$')


def do_set(parser, token):
    m = re.match(set_regex, token.contents)
    if m:
        name, exp = m.group(1), m.group(2)
        return SetNode(name, exp)
    else:
        raise template.TemplateSyntaxError('{% set varname = python_expression %}')


class SetNode(template.Node):
    def __init__(self, varname, expression):
        self.varname = varname
        self.expression = expression

    def render(self, context):
        context[self.varname] = eval(self.expression, {}, context)
        return ''


register.tag('set', do_set)

print_regex = re.compile(r'^\s*print\s+(.*)$')


def do_print(parser, token):
    m = re.match(print_regex, token.contents)
    if m:
        exp = m.group(1)
        return PrintNode(exp)
    else:
        raise template.TemplateSyntaxError('{% print expression %}')


class PrintNode(template.Node):
    def __init__(self, expression):
        self.expression = expression

    def render(self, context):
        obj = eval(self.expression, {}, context)
        return str(obj)


register.tag('print', do_print)


import_regex = re.compile(r'^\s*import\s+(\S+)(?:\s+as\s+(\w+))?$')


def do_import(parser, token):
    m = re.match(import_regex, token.contents)
    if m:
        exp = m.group(1)
        try:
            alias = m.group(2)
        except Exception:
            alias = None
        return ImportNode(exp, alias)
    else:
        raise template.TemplateSyntaxError('{% import import_expression [ as alias_name ] %}')


class ImportNode(template.Node):
    def __init__(self, expression, alias=None):
        if not alias: alias = expression
        self.expression = expression
        self.alias = alias

    def render(self, context):
        module = __import__(self.expression, {}, context)
        context[self.alias] = module
        return ''


register.tag('import', do_import)

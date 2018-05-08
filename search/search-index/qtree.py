import re
import unittest

SPLIT_RGX = re.compile(r'\w+|[\(\)&\|!]', re.U)


class QtreeTypeInfo:
    def __init__(self, value, op=False, bracket=False, term=False):
        self.value = value
        self.is_operator = op
        self.is_bracket = bracket
        self.is_term = term

    def __repr__(self):
        return repr(self.value)

    def __eq__(self, other):
        if isinstance(other, QtreeTypeInfo):
            return self.value == other.value
        return self.value == other


class QTreeTerm(QtreeTypeInfo):
    def __init__(self, term):
        QtreeTypeInfo.__init__(self, term, term=True)


class QTreeOperator(QtreeTypeInfo):
    def __init__(self, op):
        QtreeTypeInfo.__init__(self, op, op=True)
        self.priority = get_operator_prio(op)
        self.left = None
        self.right = None


class QTreeBracket(QtreeTypeInfo):
    def __init__(self, bracket):
        QtreeTypeInfo.__init__(self, bracket, bracket=True)


def get_operator_prio(s):
    if s == '|':
        return 0
    if s == '&':
        return 1
    if s == '!':
        return 2

    return None


def is_operator(s):
    return get_operator_prio(s) is not None


def tokenize_query(q):
    tokens = []
    for t in map(lambda w: w.encode('utf-8'), re.findall(SPLIT_RGX, q)):
        if t == '(' or t == ')':
            tokens.append(QTreeBracket(t))
        elif is_operator(t):
            tokens.append(QTreeOperator(t))
        else:
            tokens.append(QTreeTerm(t))

    return tokens


def parse_query(q):
    tokens = tokenize_query(q)
    return build_query_tree(tokens)


""" Collect query tree to sting back. It needs for tests. """


def qtree2str(root, depth=0):
    if root.is_operator:
        need_brackets = depth > 0 and root.value != '!'

        res = ''
        if need_brackets:
            res += '('

        if root.left:
            res += qtree2str(root.left, depth + 1)

        if root.value == '!':
            res += root.value
        else:
            res += ' ' + root.value + ' '

        if root.right:
            res += qtree2str(root.right, depth + 1)

        if need_brackets:
            res += ')'

        return res
    else:
        return root.value


def find_lowest_prio(tokens):
    fold = 0
    cur_lowest_prio = 99
    cur_lowest_prio_n = -1
    cur_lowest_prio_f = 0

    for j, t in enumerate(tokens[::-1]):
        if t == ')':
            fold += 1

        elif t == '(':
            fold -= 1

        if fold < 0:
            raise Exception('brackets error')

        if is_operator(t):
            if (get_operator_prio(t) < cur_lowest_prio) and (fold <= cur_lowest_prio_f):
                cur_lowest_prio_f = fold
                cur_lowest_prio_n = j
                cur_lowest_prio = get_operator_prio(t)

    if fold != 0:
        raise Exception('brackets error')

    token_num = len(tokens) - cur_lowest_prio_n - 1
    return token_num
    # return tokens[::-1][cur_lowest_prio_n]


def build_query_tree(tokens):

    if len(tokens) == 1:
        return tokens[0]

    # delete useless brackets

    while True:
        fold = 0
        folds = []
        for t in tokens:
            if t == '(':
                fold += 1

            folds.append(fold)

            if t == ')':
                fold -= 1

        if min(folds) > 0:
            tokens = tokens[1:-1]
        else:
            break

    # find lowest priority token and create branches
    token_num = find_lowest_prio(tokens)

    root = QTreeOperator(tokens[token_num].value)

    left_branch = tokens[:token_num]
    right_branch = tokens[token_num + 1:]

    if len(left_branch) > 1:
        root.left = build_query_tree(tokens[:token_num])

    elif len(left_branch) == 1:
        root.left = left_branch[0]

    if len(right_branch) > 1:

        root.right = build_query_tree(tokens[token_num + 1:])
    elif len(right_branch) == 1:
        root.right = right_branch[0]

    return root
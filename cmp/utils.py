class Token:
    """
    A Token class.

    Parameters
    ----------
    lex: str
        Token's lexeme.
    token_type: Enum
        Token's type.
    """

    def __init__(self, lex, token_type, row=0, col=0):
        """
        :param lex: str
        :param token_type: Enum
        :param row: int
        :param col: int
        """
        self.lex = lex
        self.token_type = token_type
        self.row = row
        self.col = col

    def __str__(self):
        return f'{self.token_type}: {self.lex}'

    def __repr__(self):
        return str(self)

    @property
    def is_valid(self):
        return True


class UnknownToken(Token):
    def __init__(self, lex):
        Token.__init__(self, lex, None)

    def transform_to(self, token_type):
        return Token(self.lex, token_type)

    @property
    def is_valid(self):
        return False


class DisjointSet:
    def __init__(self, *items):
        self.nodes = {x: DisjointNode(x) for x in items}

    def merge(self, items):
        items = (self.nodes[x] for x in items)
        try:
            head, *others = items
            for other in others:
                head.merge(other)
        except ValueError:
            pass

    @property
    def representatives(self):
        return {n.representative for n in self.nodes.values()}

    @property
    def groups(self):
        return [[n for n in self.nodes.values() if n.representative == r] for r in self.representatives]

    def __len__(self):
        return len(self.representatives)

    def __getitem__(self, item):
        return self.nodes[item]

    def __str__(self):
        return str(self.groups)

    def __repr__(self):
        return str(self)


class DisjointNode:
    def __init__(self, value):
        self.value = value
        self.parent = self

    @property
    def representative(self):
        if self.parent != self:
            self.parent = self.parent.representative
        return self.parent

    def merge(self, other):
        other.representative.parent = self.representative

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self)

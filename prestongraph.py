# Classes for constructing a graph from a list of n-quads

import re
import nquads

class Value:
    from enum import Enum
    class Type(Enum):
        ANY     = 0
        CONTENT = 1
        HASH    = CONTENT
        UUID    = 2
        URL     = 3
        RAW     = 4

    def __init__(self, text, valueType):
        assert type(text) == str
        assert type(valueType) == Value.Type
        self.text = text
        self.type = valueType
    
    def __lt__(self, other):
        return str(self) < str(other)

    def __eq__(self, other):
        t = type(other)
        if   t == str:
            return self.text == other
        elif t == Value.Type:
            return (other == Value.Type.ANY or self.type == other)
        elif t == Value:
            return (
                self.text == other.text and
                self.type == other.type
            )
        else:
            return False
    
    def __hash__(self):
        return hash(str(self))

    def __str__(self):
        return self.text
    
    def IsHash(self):
        return self.type == Value.Type.CONTENT

    def FromText(text):
        if (re.match('^hash:\/\/sha256\/.{64}$', text) or
            re.match('^https?:\/\/.*\.well-known\/genid\/\w{8}-\w{4}-\w{4}-\w{4}-\w{12}$', text)):
            type = Value.Type.CONTENT
        elif re.match('^\w{8}-\w{4}-\w{4}-\w{4}-\w{12}$', text):
            type = Value.Type.UUID
        elif re.match('^https?://', text):
            type = Value.Type.URL
        else:
            type = Value.Type.RAW

        return Value(text, type)

#=============================================================================#

class Verb:

    def __init__(self, value):
        assert type(value) == Value
        self.value = value
        self.triples = set()
    
    def __lt__(self, other):
        return str(self) < str(other)
    
    def __eq__(self, other):
        return hash(self) == hash(other)
    
    def __hash__(self):
        return hash(str(self))

    def __str__(self):
        return self.value.text

    def Text(self):
        return self.value.text

    def FromText(text, index=None):
        """Returns a node associated with *text*"""
        text = text.strip()
        
        # If the text is already indexed, use that
        if index and text in index.verbLookup:
            return index.verbLookup[text]

        value = Value.FromText(text)
        verb = Verb(value)

        # Update the index
        if index:
            index.verbLookup[text] = verb
            index.verbs.add(verb)

        return verb

#=============================================================================#

class Node:

    def __init__(self, value=None):
        self.value = value
        self.inwardTriples = set()
        self.outwardTriples = set()
    
    def __lt__(self, other):
        return str(self) < str(other)
    
    def __eq__(self, other):
        return hash(self) == hash(other)
    
    def __hash__(self):
        return hash(str(self))

    def __str__(self):
        return self.value.text

    def Text(self):
        return self.value.text

    def Type(self):
        return self.value.type

    def IsHash(self):
        return self.value.type == Value.Type.CONTENT

    def FromText(text, index=None):
        """Returns a node associated with *text*"""
        text = text.strip()
        
        # If the text is already indexed, use that
        if index and text in index.nodeLookup:
            return index.nodeLookup[text]

        value = Value.FromText(text)
        node = Node()
        node.value = value

        # Update the index
        if index:
            index.nodeLookup[text] = node
            index.nodes.add(node)

        return node

#=============================================================================#

class Triple:

    def __init__(self, subject, verb, object):
        assert type(subject) == Node
        assert type(verb) == Verb
        assert type(object) == Node
        self.subject = subject
        self.verb = verb
        self.object = object
    
    def __lt__(self, other):
        return str(self) < str(other)

    def __eq__(self, other):
        return hash(self) == hash(other)
    
    def __hash__(self):
        return hash(str(self))

    def __str__(self):
        return str(self.subject) + '\t' + str(self.verb) + '\t' + str(self.object)

    def Subject(self):
        return parts[0]

    def Verb(self):
        return parts[1]

    def Object(self):
        return parts[2]

    def Matches(self, subject=None, verb=None, object=None):
        return (
            (subject    == None or self.subject == subject  ) and
            (verb       == None or self.verb    == verb     ) and
            (object     == None or self.object  == object   )
        )

    def FromNQuad(nQuad, index=None):
        """Returns a triple extracted from *nQuad*"""

        nQuadString = str(nQuad)

        # If the text is already indexed, use that
        if index and nQuadString in index.tripleLookup:
            return index.tripleLookup[nQuadString]

        subject = Node.FromText(nQuad[0][0], index)
        verb = Verb.FromText(nQuad[1][0], index)
        object = Node.FromText(nQuad[2][0], index)

        triple = Triple(subject, verb, object)

        # Make connections
        subject.outwardTriples.add(triple)
        object.inwardTriples.add(triple)
        verb.triples.add(triple)

        # Update the index
        if index:
            index.tripleLookup[nQuadString] = triple
            index.triples.add(triple)

        return triple

#=============================================================================#

class Index:
    def __init__(self, nQuads=[]):
        self.nodeLookup = dict()
        self.verbLookup = dict()
        self.tripleLookup = dict()

        self.nodes = set()
        self.verbs = set()
        self.triples = set()

        # Parse n-quads
        for nQuad in nQuads:
            Triple.FromNQuad(nQuad, index=self)

    def Ingest(self, nQuad):
        Triple.FromNQuad(nQuad, index=self)

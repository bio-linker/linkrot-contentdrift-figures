import re
from uuid import uuid4 as UUID
import sys

from nquads import NQuads
from prestongraph import *


def main():

    url = None
    latestVersion = None
    crawlUUID = None
    for line in sys.stdin:
        nQuads = NQuads.Parse(line)
        for nQuad in nQuads:
            triple = Triple.FromNQuad(nQuad)
            # Watch for newer versions for the current URL
            if (
                triple.subject.Type() == Value.Type.CONTENT and
                triple.verb == "http://purl.org/pav/previousVersion" and
                triple.object.Type() == Value.Type.CONTENT
            ):
                latestVersion = str(triple.subject)
            # Watch for existing qualified generations
            elif (
                triple.subject.Type() == Value.Type.CONTENT and
                triple.verb == "http://www.w3.org/ns/prov#qualifiedGeneration" and
                triple.object.Type() == Value.Type.UUID
            ):
                # No need to log a new download event
                url = None
            # Check for the start of a download event
            elif (
                crawlUUID and
                triple.subject.Type() == Value.Type.URL and
                triple.verb == "http://purl.org/pav/hasVersion" and
                triple.object.Type() == Value.Type.CONTENT
            ):
                # Create a generation for the previous
                if url and latestVersion:
                    PrintQualifiedGeneration(url, latestVersion, crawlUUID)

                # Start reading triples for the next URL
                url = str(triple.subject)
                latestVersion = str(triple.object)
            # Check for a new crawl UUID
            elif triple.object == "http://www.w3.org/ns/prov#Activity":
                crawlUUID = str(triple.subject)
                url = None
                latestVersion = None

#=============================================================================#

def PrintQualifiedGeneration(url, latestVersion, crawlUUID):
    qualGenUUID = UUID()

    print("<%s> <%s> <%s> ." %
        (str(latestVersion), "http://www.w3.org/ns/prov#qualifiedGeneration", str(qualGenUUID))
    )

    print("<%s> <%s> <%s> ." %
        (str(qualGenUUID), "http://www.w3.org/1999/02/22-rdf-syntax-ns#type", "http://www.w3.org/ns/prov#Generation")
    )
    
    print("<%s> <%s> <%s> ." %
        (str(qualGenUUID), "http://www.w3.org/ns/prov#activity", str(crawlUUID))
    )

    print("<%s> <%s> <%s> ." %
        (str(qualGenUUID), "http://www.w3.org/ns/prov#used", str(url)),
    )

#=============================================================================#

if __name__ == "__main__":
    file = None
    if len(sys.argv) > 1:
        import io
        inputPath = sys.argv[1]
        file = open(inputPath, "r")
        sys.stdin = io.StringIO(file.read())
    
    main()
    
    if file:
        file.close()

# class NQuads:
#     delimiters = {
#         '<' : '>',
#         '"' : '"'
#     }

#     # TODO: retain the "@en" flag on text values
#     def Parse(text):
#         nquads = []
#         groups = []
#         inGroup = False
#         subgroupStart = None
#         subgroups = []
#         delimiter = ''
#         for i, c in enumerate(text):
#             if inGroup:
#                 if c == delimiter:
#                     subgroup = text[subgroupStart : i]
#                     subgroups.append(subgroup)
#                     delimiter = ''
#                 elif delimiter == '':
#                     # Treat back-to-back delimiters as one group
#                     if c in NQuads.delimiters:
#                         delimiter = NQuads.delimiters[c]
#                         subgroupStart = i + 1
#                     # Spaces only end the group when outside a pair of delimiters
#                     elif c.isspace():
#                         groups.append(tuple(subgroups))
#                         inGroup = False
#                         subgroups = []
#             else:
#                 if c == '.':
#                     nquads.append(groups)
#                     groups = []
#                 elif c in NQuads.delimiters:
#                     delimiter = NQuads.delimiters[c]
#                     subgroupStart = i + 1
#                     inGroup = True
#         return nquads

# #=============================================================================#

# class Value:
#     from enum import Enum
#     class Type(Enum):
#         ANY     = 0
#         CONTENT = 1
#         HASH    = CONTENT
#         UUID    = 2
#         URL     = 3
#         RAW     = 4

#     def __init__(self, text, valueType):
#         assert type(text) == str
#         assert type(valueType) == Value.Type
#         self.text = text
#         self.type = valueType
    
#     def __lt__(self, other):
#         return str(self) < str(other)

#     def __eq__(self, other):
#         t = type(other)
#         if   t == str:
#             return self.text == other
#         elif t == Value.Type:
#             return (other == Value.Type.ANY or self.type == other)
#         elif t == Value:
#             return (
#                 self.text == other.text and
#                 self.type == other.type
#             )
#         else:
#             return False

#     def __str__(self):
#         return self.text
    
#     def IsHash(self):
#         return self.type == Value.Type.CONTENT

#     def FromText(text):
#         if (re.match('^hash:\/\/sha256\/.{64}$', text) or
#             re.match('^https?:\/\/.*\.well-known\/genid\/\w{8}-\w{4}-\w{4}-\w{4}-\w{12}$', text)):
#             type = Value.Type.CONTENT
#         elif re.match('^\w{8}-\w{4}-\w{4}-\w{4}-\w{12}$', text):
#             type = Value.Type.UUID
#         elif re.match('^https?://', text):
#             type = Value.Type.URL
#         else:
#             type = Value.Type.RAW

#         return Value(text, type)

# #=============================================================================#

# class Verb:

#     def __init__(self, value):
#         assert type(value) == Value
#         self.value = value
#         self.triples = []
    
#     def __lt__(self, other):
#         return str(self) < str(other)
    
#     def __eq__(self, other):
#         t = type(other)
#         if  t == str:
#             return self.value == other
#         else:
#             return self.value == other.value

#     def __str__(self):
#         return self.value.text

#     def Text(self):
#         return self.value.text

#     def FromText(text, index=None):
#         """Returns a node associated with *text*"""
#         text = text.strip()
        
#         # If the text is already indexed, use that
#         if index and text in index.verbLookup:
#             return index.verbLookup[text]

#         value = Value.FromText(text)
#         verb = Verb(value)

#         # Update the index
#         if index:
#             index.verbLookup[text] = verb
#             index.verbs.append(verb)

#         return verb

# #=============================================================================#

# class Node:

#     def __init__(self, value=None):
#         self.value = value
#         self.inwardTriples = []
#         self.outwardTriples = []
    
#     def __lt__(self, other):
#         return str(self) < str(other)
    
#     def __eq__(self, other):
#         t = type(other)
#         if  t == str:
#             return self.value == other
#         else:
#             return (
#                 self.value == other.value
#             )

#     def __str__(self):
#         return self.value.text

#     def Text(self):
#         return self.value.text

#     def Type(self):
#         return self.value.type

#     def IsHash(self):
#         return self.value.type == Value.Type.CONTENT

#     def FromText(text, index=None):
#         """Returns a node associated with *text*"""
#         text = text.strip()
        
#         # If the text is already indexed, use that
#         if index and text in index.nodeLookup:
#             return index.nodeLookup[text]

#         value = Value.FromText(text)
#         node = Node()
#         node.value = value

#         # Update the index
#         if index:
#             index.nodeLookup[text] = node
#             index.nodes.append(node)

#         return node

# #=============================================================================#

# class Triple:

#     def __init__(self, subject, verb, object):
#         assert type(subject) == Node
#         assert type(verb) == Verb
#         assert type(object) == Node
#         self.subject = subject
#         self.verb = verb
#         self.object = object
    
#     def __lt__(self, other):
#         return str(self) < str(other)

#     def __eq__(self, other):
#         return (
#             self.subject    == other.subject    and
#             self.verb       == other.verb       and
#             self.object     == other.object
#         )

#     def __str__(self):
#         return str(self.subject) + '\t' + str(self.verb) + '\t' + str(self.object)

#     def Subject(self):
#         return parts[0]

#     def Verb(self):
#         return parts[1]

#     def Object(self):
#         return parts[2]

#     def Matches(self, subject=None, verb=None, object=None):
#         return (
#             (subject    == None or self.subject == subject  ) and
#             (verb       == None or self.verb    == verb     ) and
#             (object     == None or self.object  == object   )
#         )

#     def FromNQuad(nQuad, index=None):
#         """Returns a triple extracted from *nQuad*"""

#         nQuadString = str(nQuad)

#         # If the text is already indexed, use that
#         if index and nQuadString in index.tripleLookup:
#             return index.tripleLookup[nQuadString]

#         subject = Node.FromText(nQuad[0][0], index)
#         verb = Verb.FromText(nQuad[1][0], index)
#         object = Node.FromText(nQuad[2][0], index)

#         triple = Triple(subject, verb, object)

#         # Make connections
#         subject.outwardTriples.append(triple)
#         object.inwardTriples.append(triple)
#         verb.triples.append(triple)

#         # Update the index
#         if index:
#             index.tripleLookup[nQuadString] = triple
#             index.triples.append(triple)

#         return triple

# #=============================================================================#

# class Index:
#     def __init__(self, nQuads):
#         self.nodeLookup = dict()
#         self.verbLookup = dict()
#         self.tripleLookup = dict()

#         self.nodes = list()
#         self.verbs = list()
#         self.triples = list()

#         # Parse n-quads
#         for nQuad in nQuads:
#             Triple.FromNQuad(nQuad, index=self)

# #=============================================================================#

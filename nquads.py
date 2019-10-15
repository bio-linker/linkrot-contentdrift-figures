# Functions for parsing and manipulating n-quads

class NQuads:
    delimiters = {
        '<' : '>',
        '"' : '"'
    }

    # TODO:
    # - Retain the "@en" flag on text values
    # - Function to convert to back to string
    def Parse(text : str):
        nquads = []
        groups = []
        inGroup = False
        subgroupStart = None
        subgroups = []
        delimiter = ''
        for i, c in enumerate(text):
            if inGroup:
                if c == delimiter:
                    subgroup = text[subgroupStart : i]
                    subgroups.append(subgroup)
                    delimiter = ''
                elif delimiter == '':
                    # Treat back-to-back delimiters as one group
                    if c in NQuads.delimiters:
                        delimiter = NQuads.delimiters[c]
                        subgroupStart = i + 1
                    # Spaces only end the group when outside a pair of delimiters
                    elif c.isspace():
                        groups.append(tuple(subgroups))
                        inGroup = False
                        subgroups = []
            else:
                if c == '.':
                    nquads.append(groups)
                    groups = []
                elif c in NQuads.delimiters:
                    delimiter = NQuads.delimiters[c]
                    subgroupStart = i + 1
                    inGroup = True
        return nquads

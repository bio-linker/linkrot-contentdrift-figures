# RDF N-Quads patterns were taken from https://www.w3.org/TR/n-quads/#sec-grammar
import re

def group(regex, name=""):
    return "(%s%s)" % (
        "" if name == "" else "?P<" + name + ">",
        regex
    )

def either(regexes : tuple):
     return group(r'|'.join(regexes))

HEX = group(r'[0-9]|[A-F]|[a-f]')
UCHAR = group(r'[^\W\d_]')
ECHAR = group(r'''\[tbnrf"'\]''')
IRIREF = group(r'<([^\x00-\x20<>"{}|^`\\]|' + UCHAR + r')*>')
STRING_LITERAL_QUOTE = group(r'"([^\x22\x5C\x0A\x0D]|' + ECHAR + r'|' + UCHAR + r')*"')
LANGTAG = group(r'@[a-zA-Z]+(-[a-zA-Z0-9]+)*')
PN_CHARS_BASE = group(r'[A-Z]|[a-z]|[\u00C0-\u00D6]|[\u00D8-\u00F6]|[\u00F8-\u02FF]|[\u0370-\u037D]|[\u037F-\u1FFF]|[\u200C-\u200D]|[\u2070-\u218F]|[\u2C00-\u2FEF]|[\u3001-\uD7FF]|[\uF900-\uFDCF]|[\uFDF0-\uFFFD]|[\u10000-\uEFFFF]')
PN_CHARS_U = group(PN_CHARS_BASE + r'|_|:')
PN_CHARS = group(PN_CHARS_U + r'|-|[0-9]|\u00B7|[\u0300-\u036F]|[\u203F-\u2040]')
BLANK_NODE_LABEL = group(r'_:(' + PN_CHARS_U + r'|[0-9])((' + PN_CHARS + r'|.)*' + PN_CHARS + r')?')
EOL = group('[\x0D\x0A]+')

literal = group(STRING_LITERAL_QUOTE + r'(\^\^' + IRIREF + r'|' + LANGTAG + r')?')
subject = either((IRIREF, BLANK_NODE_LABEL))
predicate = group(IRIREF)
object_ = either((IRIREF, BLANK_NODE_LABEL, literal))
graph_label = either((IRIREF, BLANK_NODE_LABEL))
statement = group(group(subject, "subject") + ' ' + group(predicate, "predicate") + ' ' + group(object_, "object") + '( ' + group(graph_label, "context") + ')? \.')
nquads_doc = group(statement + '?(' + EOL + statement + ')*' + EOL + '?')

statement_pattern = re.compile(statement)

output = re.match(statement, "<cats> <eat> <fish> .")

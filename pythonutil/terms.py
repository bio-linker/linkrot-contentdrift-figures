def pamper(text):
    return "<%s>" % text

DESCRIPTION = pamper("http://purl.org/dc/terms/description")
HAS_QUALIFIED_GENERATION = pamper("http://www.w3.org/ns/prov#qualifiedGeneration")
STARTED_AT_TIME = pamper("http://www.w3.org/ns/prov#startedAtTime")
TYPE = pamper("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
USED = pamper("http://www.w3.org/ns/prov#used")
WAS_INFLUENCED_BY = pamper("http://www.w3.org/ns/prov#activity")
WAS_INFORMED_BY = pamper("http://www.w3.org/ns/prov#wasInformedBy")
WAS_GENERATED_BY = pamper("http://www.w3.org/ns/prov#wasGeneratedBy")
WAS_STARTED_BY = pamper("http://www.w3.org/ns/prov#wasStartedBy")
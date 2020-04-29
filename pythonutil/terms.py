def pamper(text):
    return "<%s>" % text

ACTIVITY = pamper("http://www.w3.org/ns/prov#Activity")
CREATED_BY = pamper("http://purl.org/pav/createdBy")
DESCRIPTION = pamper("http://purl.org/dc/terms/description")
GENERATION = pamper("http://www.w3.org/ns/prov#Generation")
HAD_MEMBER = pamper("http://www.w3.org/ns/prov#hadMember")
HAS_QUALIFIED_GENERATION = pamper("http://www.w3.org/ns/prov#qualifiedGeneration")
HAS_TYPE = pamper("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
HAS_VERSION = pamper("http://purl.org/pav/hasVersion")
STARTED_AT_TIME = pamper("http://www.w3.org/ns/prov#startedAtTime")
TYPE = pamper("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
USED = pamper("http://www.w3.org/ns/prov#used")
WAS_ASSOCIATED_WITH = pamper("http://www.w3.org/ns/prov#wasAssociatedWith")
WAS_INFLUENCED_BY = pamper("http://www.w3.org/ns/prov#activity")
WAS_INFORMED_BY = pamper("http://www.w3.org/ns/prov#wasInformedBy")
WAS_GENERATED_BY = pamper("http://www.w3.org/ns/prov#wasGeneratedBy")
WAS_STARTED_BY = pamper("http://www.w3.org/ns/prov#wasStartedBy")
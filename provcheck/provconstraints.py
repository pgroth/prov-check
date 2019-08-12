"""prov-constraints.py: Check prov-constraints

Usage: provconstraints.py <path of turtle file to check>
"""

import rdflib
import os
import sys
import getopt
from rdflib.plugins.sparql.processor import prepareQuery
from rdflib.plugins.sparql.processor import processUpdate



#Testing queries
qMakeCycle = '''
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>

    INSERT DATA {
        c:start c:precedes c:two .
        c:two   c:precedes c:three .
        c:three c:strictlyPrecedes c:start .
    }
'''


#Check cycles
qCheckCycle = '''
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>

select ?x where { ?x (c:precedes+|c:strictlyPrecedes+)/c:strictlyPrecedes ?x .}

'''



###############################################
# SPARQL Query for Constraints
##############################################

## Activity Ordering Constraint Insert

start_precedes_end = '''
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>

    INSERT {
         ?start c:precedes ?end .
    }
    where {
        ?act a prov:Activity .
        ?act prov:qualifiedEnd ?end .
        ?act prov:qualifiedStart ?start .
    }
'''

start_start_ordering = '''
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>

    INSERT {
         ?start1 c:precedes ?start2 .
    }
    where {
        ?act a prov:Activity .
        ?act prov:qualifiedStart ?start1 .
        ?act prov:qualifiedStart ?start2 .
    }

'''

end_end_ordering = '''
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>

    INSERT {
         ?end1 c:precedes ?end2 .
    }
    where {
        ?act a prov:Activity .
        ?act prov:qualifiedEnd ?end1 .
        ?act prov:qualifiedEnd ?end2 .
    }

'''

usage_within_activity1 = '''
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>

    INSERT {
         ?start c:precedes ?use .
    }
    where {
        ?act a prov:Activity .
        ?act prov:qualifiedStart ?start .
        ?act prov:qualifiedUsage ?use .
    }

'''

usage_within_activity2 = '''
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>

    INSERT {
         ?use c:precedes ?end .
    }
    where {
        ?act a prov:Activity .
        ?act prov:qualifiedEnd ?end .
        ?act prov:qualifiedUsage ?use .
    }

'''

generation_within_activity1 = '''
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>

    INSERT {
         ?start c:precedes ?gen .
    }
    where {
        ?act a prov:Activity .
        ?act prov:qualifiedStart ?start .
        ?act prov:qualifiedGeneration ?gen .
    }

'''

generation_within_activity2 = '''
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>

    INSERT {
         ?gen c:precedes ?end .
    }
    where {
        ?act a prov:Activity .
        ?act prov:qualifiedEnd ?end .
        ?act prov:qualifiedGeneration ?gen .
    }

'''

wasInformedBy_ordering = '''
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>

    INSERT {
         ?start c:precedes ?end .
    }
    where {
        ?act1 prov:qualifiedCommunication ?com.
        ?com prov:activity ?act2.
        ?act1 a prov:Activity .
        ?act2 a prov:Activity .
        ?act1 prov:qualifiedStart ?start .
        ?act2 prov:qualifiedEnd ?end .
    }
'''

## Entity Ordering Constraint Insert

generation_precedes_invalidation = '''
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>

    INSERT {
         ?gen c:precedes ?inv .
    }
    where {
        ?e a prov:Entity .
        ?e prov:qualifiedGeneration ?gen .
        ?e prov:qualifiedInvalidation ?inv .
    }
'''

generation_precedes_usage = '''
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>

    INSERT {
         ?gen c:precedes ?use .
    }
    where {
        ?e a prov:Entity .
        ?e prov:qualifiedGeneration ?gen .
        ?e prov:qualifiedUsage ?use .

    }
'''

usage_precedes_invalidation = '''
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>

    INSERT {
         ?use c:precedes ?inv .
    }
    where {
        ?e a prov:Entity .
        ?e prov:qualifiedInvalidation ?inv .
        ?e prov:qualifiedUsage ?use .

    }
'''

generation_generation_ordering = '''
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>

    INSERT {
         ?gen1 c:precedes ?gen2 .
    }
    where {
        ?e a prov:Entity .
        ?e prov:qualifiedGeneration ?gen1 .
        ?e prov:qualifiedGeneration ?gen2 .

    }
'''

invalidation_invalidation_ordering = '''
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>

    INSERT {
         ?inv1 c:precedes ?inv2 .
    }
    where {
        ?e a prov:Entity .
        ?e prov:qualifiedInvalidation ?inv1 .
        ?e prov:qualifiedInvalidation ?inv2 .
    }
'''

derivation_usage_generation_ordering = '''
    #e2 prov:wasDerivedFrom e1
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>

    INSERT {
         ?use1 c:precedes ?gen2 .
    }
    where {
        ?e1 a prov:Entity .
        ?e2 a prov:Entity .
        ?e2 prov:qualifiedDerivation ?d .
        ?d prov:entity ?e1 .
        ?d prov:hadGeneration ?gen2 .
        ?d prov:hadUsage ?use1 .
        ?use1 prov:entity ?e1 .
        ?e2 prov:qualifiedGeneration ?gen2 .

    }
'''

derivation_generation_generation_ordering = '''
    #e2 prov:wasDerivedFrom e1
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>

    INSERT {
         ?gen1 c:strictlyPrecedes ?gen2 .
    }
    where {
        ?e1 a prov:Entity .
        ?e2 a prov:Entity .
        ?e2 prov:qualifiedDerivation ?d .
        ?d prov:entity ?e1 .
        ?e1 prov:qualifiedGeneration ?gen1 .
        ?e2 prov:qualifiedGeneration ?gen2 .

    }
'''

wasStartedBy_ordering1 = '''
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>

    INSERT {
         ?gen c:precedes ?start .
    }
    where {
        ?e a prov:Entity .
        ?e prov:qualifiedGeneration ?gen1 .
        ?a prov:qualifiedStart ?start .
        ?start prov:entity ?e .
    }
'''

wasStartedBy_ordering2 = '''
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>

    INSERT {
         ?start c:precedes ?inv .
    }
    where {
        ?e a prov:Entity .
        ?e prov:qualifiedInvalidation ?inv .
        ?a prov:qualifiedStart ?start .
        ?start prov:entity ?e .
    }
'''

wasEndedBy_ordering1 = '''
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>

    INSERT {
         ?gen c:precedes ?end .
    }
    where {
        ?e a prov:Entity .
        ?e prov:qualifiedGeneration ?gen1 .
        ?a prov:qualifiedEnd ?end .
        ?end prov:entity ?e .
    }
'''

wasEndedBy_ordering2 = '''
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>

    INSERT {
         ?end c:precedes ?inv .
    }
    where {
        ?e a prov:Entity .
        ?e prov:qualifiedInvalidation ?inv .
        ?a prov:qualifiedEnd ?end .
        ?end prov:entity ?e .
    }
'''

specialization_generation_ordering = '''
    #e2 prov:specializationOf e1
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>

    INSERT {
         ?gen1 c:strictlyPrecedes ?gen2 .
    }
    where {
        ?e1 a prov:Entity .
        ?e2 a prov:Entity .
        ?e2 prov:specializationOf ?e1 .
        ?e1 prov:qualifiedGeneration ?gen1 .
        ?e2 prov:qualifiedGeneration ?gen2 .

    }
'''



specialization_invalidation_ordering = '''
    #e1 prov:specializationOf e2
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>

    INSERT {
         ?inv1 c:strictlyPrecedes ?inv2 .
    }
    where {
        ?e1 a prov:Entity .
        ?e2 a prov:Entity .
        ?e1 prov:specializationOf ?e2 .
        ?e1 prov:qualifiedInvalidation ?inv1 .
        ?e2 prov:qualifiedInvalidation ?inv2 .

    }
'''

## Agent Ordering Constraints

wasAssociatedWith_ordering1 = '''
    #agent as entity
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>

    INSERT {
        ?start c:precedes ?inv .
    }
    where {
        ?ag a prov:Agent .
        ?act a prov:Activity .
        ?act prov:qualifiedAssociation ?assoc .
        ?assoc prov:agent ?ag .
        ?act prov:qualifiedStart ?start .
        ?ag prov:qualifiedInvalidation ?inv .

    }
'''

wasAssociatedWith_ordering2 = '''
    #agent as entity
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>

    INSERT {
        ?gen c:precedes ?end .
    }
    where {
        ?ag a prov:Agent .
        ?act a prov:Activity .
        ?act prov:qualifiedAssociation ?assoc .
        ?assoc prov:agent ?ag .
        ?ag prov:qualifiedGeneration ?gen .
        ?act prov:qualifiedEnd ?end .

    }
'''

wasAssociatedWith_ordering3 = '''
    # agent as an activity
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>

    INSERT {
        ?start c:precedes ?end .
    }
    where {
        ?ag a prov:Agent .
        ?act a prov:Activity .
        ?act prov:qualifiedAssociation ?assoc .
        ?assoc prov:agent ?ag .
        ?act prov:qualifiedStart ?start .
        ?ag prov:qualifiedEnd ?end .

    }
'''

wasAssociatedWith_ordering4 = '''
    #activity as agent
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>

    INSERT {
        ?start c:precedes ?end .
    }
    where {
        ?ag a prov:Agent .
        ?act a prov:Activity .
        ?act prov:qualifiedAssociation ?assoc .
        ?assoc prov:agent ?ag .
        ?ag prov:qualifiedStart ?start .
        ?act prov:qualifiedEnd ?end .

    }
'''

wasAttributedTo_ordering1 = '''
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>

    INSERT {
       ?gen1 c:precedes ?gen2 .
    }
    where {
        ?ag a prov:Agent .
        ?e a prov:Entity .
        ?e prov:qualifiedAttribution ?attr .
        ?attr prov:agent ?ag .
        ?ag prov:qualifiedGeneration ?gen1 .
        ?e prov:qualifiedGeneration ?gen2 .
    }
'''

wasAttributedTo_ordering2 = '''
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>

    INSERT {
       ?start c:precedes ?gen .
    }
    where {
        ?ag a prov:Agent .
        ?e a prov:Entity .
        ?e prov:qualifiedAttribution ?attr .
        ?attr prov:agent ?ag .
        ?ag prov:qualifiedStart ?start .
        ?e prov:qualifiedGeneration ?gen .
    }
'''

actedOnBehalfOf_ordering1 = '''
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>

    INSERT {
       ?gen c:precedes ?inv .
    }
    where {
        ?ag1 a prov:Agent .
        ?ag2 a prov:Agent .
        ?ag2 prov:qualifiedDelegation ?del .
        ?del prov:agent ?ag1 .
        ?ag1 prov:qualifiedGeneration ?gen .
        ?ag2 prov:qualifiedInvalidation ?inv .
    }
'''

actedOnBehalfOf_ordering2 = '''
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>

    INSERT {
       ?start c:precedes ?end .
    }
    where {
        ?ag1 a prov:Agent .
        ?ag2 a prov:Agent .
        ?ag2 prov:qualifiedDelegation ?del .
        ?del prov:agent ?ag1 .
        ?ag1 prov:qualifiedStart ?start .
        ?ag2 prov:qualifiedEnd ?end .
    }
'''

### Uniqueness Constraints

unique_generation = '''
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>

    select ?e where {
        ?e prov:qualifiedGeneration ?gen1 .
        ?gen1 prov:activity ?act .
        ?e prov:qualifiedGeneration ?gen2 .
        ?gen2 prov:activity ?act .
        FILTER (?gen1 != ?gen2)
    }
'''

unique_invalidation = '''
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>

    select ?e where {
        {
            ?e prov:qualifiedInvalidation ?inv1 .
            ?inv1 prov:activity ?act .
            ?e prov:qualifiedInvalidation ?inv2 .
            ?inv2 prov:activity ?act .
            OPTIONAL {?inv1 prov:atTime ?t1 .
            ?inv2 prov:atTime ?t2 .}
            FILTER (?inv1 != ?inv2 || ?t1 != ?t2)
        }

    }
'''

unique_wasStartedBy = '''
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>

    select ?a where {
        ?a prov:qualifiedStart ?start1 .
        ?a prov:qualifiedStart ?start2 .
        ?start1 prov:hadActivity ?starter .
        ?start2 prov:hadActivity ?starter .
        FILTER ( ?start1 != ?start2)
    }
'''

unique_wasEndedBy = '''
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>

    select ?a where {
        ?a prov:qualifiedEnd ?end1 .
        ?a prov:qualifiedEnd ?end2 .
        ?end1 prov:hadActivity ?ender .
        ?end2 prov:hadActivity ?ender .
        FILTER (?end1 != ?end2)
    }
'''

unique_startTime = '''
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>

    select ?a where {
        ?a prov:qualifiedStart ?start .
        ?start prov:atTime ?t1 .
        ?a prov:startedAtTime ?t2 .
        FILTER (?t1 != ?t2)
    }
'''

unique_endTime = '''
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>

    select ?a where {
        ?a prov:qualifiedEnd ?end .
        ?end prov:atTime ?t1 .
        ?a prov:endedAtTime ?t2 .
        FILTER (?t1 != ?t2)
    }
'''

##Impossibility Constraints

impossible_unspecified_derivation_generation_use = '''
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>

    select ?d where {
        { ?d a prov:Derivation .
        ?d prov:hadGeneration ?g .
        FILTER NOT EXISTS { ?d prov:hadActivity ?a . }
        }
        UNION {
        ?d a prov:Derivation .
        ?d prov:hadUsage ?u .
        FILTER NOT EXISTS { ?d prov:hadActivity ?a . }
        }
        UNION {
        ?d a prov:Derivation .
        ?d prov:hadUsage ?u .
        ?d prov:hadGeneration ?g .
        FILTER NOT EXISTS { ?d prov:hadActivity ?a . }
        }
    }
'''

impossible_specializaton_reflexive = '''
 PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>

    select ?e where {
        ?e prov:specializationOf+ ?e .
    }
'''

impossible_property_overlap = '''
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>

    select ?x where {
        ?x a ?class1 .
        ?x a ?class2 .
        FILTER ( ?class1 != ?class2 &&
                ?class1 IN (prov:Usage,
                            prov:Generation,
                            prov:Invalidation,
                            prov:Start,
                            prov:End,
                            prov:Communication,
                            prov:Attribution,
                            prov:Association,
                            prov:Delegation,
                            prov:Derivation) &&
                ?class2 IN (prov:Usage,
                            prov:Generation,
                            prov:Invalidation,
                            prov:Start,
                            prov:End,
                            prov:Communication,
                            prov:Attribution,
                            prov:Association,
                            prov:Delegation,
                            prov:Derivation) )

    }
'''

impossible_object_property_overlap = '''
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>

    select ?x where {
        ?x a ?class1 .
        ?x a ?class2 .
        FILTER ( ?class1 != ?class2 &&
                ?class1 IN (prov:Entity, prov:Activity, prov:Agent) &&
                ?class2 IN (prov:Usage,
                            prov:Generation,
                            prov:Invalidation,
                            prov:Start,
                            prov:End,
                            prov:Communication,
                            prov:Attribution,
                            prov:Association,
                            prov:Delegation,
                            prov:Derivation) )

    }
'''

entity_activity_disjoint = '''
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>

    select ?e where {
        ?e a prov:Entity, prov:Activity .
    }
'''

membership_empty_collection = '''
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>

    select ?c where {
        ?c prov:hadMember ?m .
        ?c a prov:EmptyCollection .
    }
'''

##Key Constraints
key_generation = '''
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>

    select ?g where {
            {
            ?g a prov:Generation .
            ?e1 prov:qualifiedGeneration ?g .
            ?e2 prov:qualifiedGeneration ?g .
            FILTER ( ?e1 != ?e2 )
            }
            UNION
            {
            ?g a prov:Generation .
            ?g prov:activity ?a1 .
            ?g prov:activity ?a2 .
            FILTER ( ?a1 != ?a2)
            }
            UNION
            {
            ?g a prov:Generation .
            ?g prov:atTime ?t1 .
            ?g prov:atTime ?t2 .
            FILTER ( ?t1 != ?t2)
            }
    }
'''

key_used = '''
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>

    select ?u where {
            {
            ?u a prov:Usage .
            ?a1 prov:qualifiedUsage ?u .
            ?a2 prov:qualifiedUsage ?u .
            FILTER ( ?a1 != ?a2 )
            }
            UNION
            {
            ?u a prov:Usage .
            ?u prov:entity ?e1 .
            ?u prov:entity ?e2 .
            FILTER ( ?e1 != ?e2)
            }
            UNION
            {
            ?u a prov:Usage .
            ?u prov:atTime ?t1 .
            ?u prov:atTime ?t2 .
            FILTER ( ?t1 != ?t2)
            }
    }
'''

key_communication = '''
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>

    select ?c where {
            {
            ?c a prov:Communication .
            ?a1 prov:qualifiedCommunication ?c .
            ?a2 prov:qualifiedCommunication ?c .
            FILTER ( ?a1 != ?a2 )
            }
            UNION
            {
            ?c a prov:Communication  .
            ?c prov:activity ?a1 .
            ?c prov:activity ?a2 .
            FILTER ( ?a1 != ?a2)
            }

    }
'''

key_start = '''
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>

    select ?s where {
            {
            ?s a prov:Start .
            ?a1 prov:qualifiedStart ?s .
            ?a2 prov:qualifiedStart ?s .
            FILTER ( ?a1 != ?a2 )
            }
            UNION
            {
            ?s a prov:Start  .
            ?s prov:entity ?e1 .
            ?s prov:entity ?e2 .
            FILTER ( ?e1 != ?e2)
            }
            UNION
            {
            ?s a prov:Start  .
            ?s prov:hadActivity ?a1 .
            ?s prov:hadActivity ?a2 .
            FILTER ( ?a1 != ?a2)
            }
            UNION
            {
            ?s a prov:Start  .
            ?s prov:atTime ?t1 .
            ?s prov:atTime ?t2 .
            FILTER ( ?t1 != ?t2)
            }

    }
'''

key_end = '''
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>

    select ?e where {
            {
            ?e a prov:End .
            ?a1 prov:qualifiedEnd ?e .
            ?a2 prov:qualifiedEnd ?e .
            FILTER ( ?a1 != ?a2 )
            }
            UNION
            {
            ?e a prov:End .
            ?e prov:entity ?e1 .
            ?e prov:entity ?e2 .
            FILTER ( ?e1 != ?e2)
            }
            UNION
            {
            ?e a prov:End .
            ?e prov:hadActivity ?a1 .
            ?e prov:hadActivity ?a2 .
            FILTER ( ?a1 != ?a2)
            }
            UNION
            {
            ?e a prov:End .
            ?e prov:atTime ?t1 .
            ?e prov:atTime ?t2 .
            FILTER ( ?t1 != ?t2)
            }

    }
'''

key_invalidation = '''
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>

    select ?inv where {
            {
            ?inv a prov:Invalidation .
            ?e1 prov:qualifiedInvalidation ?inv .
            ?e2 prov:qualifiedInvalidation ?inv .
            FILTER ( ?e1 != ?e2 )
            }
            UNION
            {
            ?inv a prov:Invalidation .
            ?inv prov:activity ?a1 .
            ?inv prov:activity ?a2 .
            FILTER ( ?a1 != ?a2)
            }
            UNION
            {
            ?inv a prov:Invalidation .
            ?inv prov:atTime ?t1 .
            ?inv prov:atTime ?t2 .
            FILTER ( ?t1 != ?t2)
            }

    }
'''

key_derivation = '''
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>

    select ?d where {
            {
            ?d a prov:Derivation .
            ?e1 prov:qualifiedDerivation ?d .
            ?e2 prov:qualifiedDerivation ?d .
            FILTER ( ?e1 != ?e2 )
            }
            UNION
            {
            ?d a prov:Derivation .
            ?d prov:entity ?e1 .
            ?d prov:entity ?e2 .
            FILTER ( ?e1 != ?e2 )
            }
            UNION
            {
            ?d a prov:Derivation .
            ?d prov:hadActivity ?a1 .
            ?d prov:hadActivity ?a2 .
            FILTER ( ?a1 != ?a2 )
            }
            UNION
            {
            ?d a prov:Derivation .
            ?d prov:hadUsage ?u1 .
            ?d prov:hadUsage ?u2 .
            FILTER ( ?u1 != ?u2 )
            }
            UNION
            {
            ?d a prov:Derivation .
            ?d prov:hadGeneration ?g1 .
            ?d prov:hadGeneration ?g2 .
            FILTER ( ?g1 != ?g2 )
            }
    }
'''

key_attribution = '''
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>

    select ?a where {
            {
            ?a a prov:Attribution .
            ?e1 prov:qualifiedAttribution ?a .
            ?e2 prov:qualifiedAttribution ?a .
            FILTER ( ?e1 != ?e2 )
            }
            UNION
            {
            ?a a prov:Attribution .
            ?a prov:agent ?ag1 .
            ?a prov:agent ?ag2 .
            FILTER ( ?ag1 != ?ag2 )
            }
    }
'''

key_association = '''
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>

    select ?asc where {
            {
            ?asc a prov:Association .
            ?a1 prov:qualifiedAssociation ?asc .
            ?a2 prov:qualifiedAssociation ?asc .
            FILTER ( ?a1 != ?a2 )
            }
            UNION
            {
            ?asc a prov:Association .
            ?asc prov:agent ?ag1 .
            ?asc prov:agent ?ag2 .
            FILTER ( ?ag1 != ?ag2 )
            }
            UNION
            {
            ?asc a prov:Association .
            ?asc prov:hadPlan ?p1 .
            ?asc prov:hadPlan ?p2 .
            FILTER ( ?p1 != ?p2 )
            }
    }
'''

key_delegation = '''
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>

    select ?dg where {
            {
            ?dg a prov:Delegation .
            ?a1 prov:qualifiedDelegation ?dg .
            ?a2 prov:qualifiedDelegation ?dg .
            FILTER ( ?a1 != ?a2 )
            }
            UNION
            {
            ?dg a prov:Delegation .
            ?dg prov:agent ?ag1 .
            ?dg prov:agent ?ag2 .
            FILTER ( ?ag1 != ?ag2 )
            }
            UNION
            {
            ?dg a prov:Delegation .
            ?dg prov:hadActivity ?a1 .
            ?dg prov:hadActivity ?a2 .
            FILTER ( ?a1 != ?a2 )
            }
    }
'''

key_influence = '''
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>

    select ?inf where {
            {
            ?inf a prov:Influence .
            ?t1 prov:qualifiedInfluence ?inf .
            ?t2 prov:qualifiedInfluence ?inf .
            FILTER ( ?t1 != ?t2 )
            }
            UNION
            {
            ?inf a prov:Influence .
            ?inf ?rel ?t1 .
            ?inf ?rel ?t2 .
            FILTER ( ?rel IN (prov:agent,
                              prov:entity,
                              prov:activity)
                     && ?t1 != ?t2  )
            }
    }
'''

##type constraints for relations

type_used = '''
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>

    select ?u where {
        ?u a prov:Usage .
        FILTER NOT EXISTS { ?u prov:entity ?e . ?a prov:qualifiedUsage ?u . }
    }
'''

type_association = '''
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>

    select ?asc where {
        ?asc a prov:Association .
        FILTER NOT EXISTS { ?a prov:qualifiedAssociation ?asc . }
    }
'''

type_attribution = '''
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>

    select ?att where {
        ?att a prov:Attribution .
        FILTER NOT EXISTS { ?att prov:agent ?ag . ?e prov:qualifiedAttribution ?att . }
    }
'''

type_generation = '''
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>

    select ?gen where {
        ?gen a prov:Generation .
        FILTER NOT EXISTS { ?e prov:qualifiedGeneration ?gen . }
    }
'''

type_communication = '''
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>

    select ?c where {
        ?c a prov:Communication .
        FILTER NOT EXISTS { ?c prov:activity ?a2 . ?a1 prov:qualifiedCommunication ?c . }
    }
'''

type_delegation = '''
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>

    select ?d where {
        ?d a prov:Delegation .
        FILTER NOT EXISTS { ?d prov:agent ?ag2 . ?ag1 prov:qualifiedDelegation ?d . }
    }
'''

type_influence = '''
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>

    select ?i where {
        ?i a prov:Influence .
        FILTER NOT EXISTS { ?i prov:influencer|prov:agent ?w2 . ?w prov:qualifiedInfluence|prov:qualifiedAssociation ?i . }
    }
'''

type_invalidation = '''
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>

    select ?i where {
        ?i a prov:Invalidation .
        FILTER NOT EXISTS { ?i prov:activity ?a . ?w prov:qualifiedInvalidation ?i . }
    }
'''

##--> need to do this check better
type_start = '''
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>

    select ?i where {
        ?s a prov:Start .
        FILTER NOT EXISTS {?a prov:qualifiedInvalidation ?s . ?s prov:entity|prov:hadActivity ?b }

    }
'''

# --> don't know if we are required to have atTime on all events
# --> if so this check belongs in the ordering constraints
merge_invalidation = '''
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>

    select ?i ?i2 where {
        ?e a prov:Entity .
        ?e prov:qualifiedInvalidation ?i .
        ?e prov:qualifiedInvalidation ?i2 .
        ?i prov:atTime ?t .
        ?i2 prov:atTime ?t2 .
        FILTER ( !sameTerm(?i, ?i2) && ?t != ?t2 )
    }
'''

merge_generation = '''
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>

    select ?g ?g2 where {
        ?e a prov:Entity .
        ?e prov:qualifiedGeneration ?g .
        ?e prov:qualifiedGeneration ?g2 .
        ?g prov:atTime ?t .
        ?g2 prov:atTime ?t2 .
        FILTER ( !sameTerm(?g, ?g2) && ?t != ?t2 )
    }
'''

merge_start = '''
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>

    select ?g ?g2 where {
        ?a a prov:Activity .
        ?a prov:qualifiedStart ?s .
        ?a prov:qualifiedStart ?s2 .
        ?s prov:atTime ?t .
        ?s2 prov:atTime ?t2 .
        FILTER ( !sameTerm(?s, ?s2) && ?t != ?t2 )
    }
'''



###########################

def orderingConstraints(g):
    processUpdate(g, start_precedes_end)
    processUpdate(g, start_start_ordering)
    processUpdate(g, end_end_ordering)
    processUpdate(g, usage_within_activity1)
    processUpdate(g, usage_within_activity2)
    processUpdate(g, generation_within_activity1)
    processUpdate(g, generation_within_activity2)
    processUpdate(g, wasInformedBy_ordering)
    processUpdate(g, generation_precedes_invalidation)
    processUpdate(g, generation_precedes_usage)
    processUpdate(g, usage_precedes_invalidation)
    processUpdate(g, generation_generation_ordering)
    processUpdate(g, invalidation_invalidation_ordering)
    processUpdate(g, derivation_usage_generation_ordering)
    processUpdate(g, derivation_generation_generation_ordering)
    processUpdate(g, wasStartedBy_ordering1)
    processUpdate(g, wasStartedBy_ordering2)
    processUpdate(g, wasEndedBy_ordering1)
    processUpdate(g, wasEndedBy_ordering2)
    processUpdate(g, specialization_generation_ordering)
    processUpdate(g, specialization_invalidation_ordering)
    processUpdate(g, wasAssociatedWith_ordering1)
    processUpdate(g, wasAssociatedWith_ordering2)
    processUpdate(g, wasAssociatedWith_ordering3)
    processUpdate(g, wasAssociatedWith_ordering4)
    processUpdate(g, wasAttributedTo_ordering1)
    processUpdate(g, wasAttributedTo_ordering2)
    processUpdate(g, actedOnBehalfOf_ordering1)
    processUpdate(g, actedOnBehalfOf_ordering2)
    return g

def checkUniqueness(g):
    queries = [unique_generation, unique_invalidation,
               unique_wasStartedBy,
               unique_wasEndedBy,
               unique_startTime,
               unique_endTime]
    for q in queries:
        if not check(g, q):
            print('uniqueness')
            return False

    return True

def checkImpossibility(g):
    queries = [impossible_unspecified_derivation_generation_use,
               impossible_specializaton_reflexive,
               impossible_property_overlap,
               impossible_object_property_overlap,
               entity_activity_disjoint,
               membership_empty_collection]
    for q in queries:
        if not check(g, q):
            print('impossibility')
            return False

    return True

def checkKeyConstraints(g):
    queries = [key_generation,
               key_used,
               key_communication,
               key_start,
               key_end,
               key_invalidation,
               key_derivation,
               key_attribution,
               key_association,
               key_delegation,
               key_influence]
    for q in queries:
        if not check(g, q):
            print('keyconstraints')
            return False

    return True

def checkTypeConstraints(g):
    queries = [type_used,
               type_attribution,
               type_communication,
               type_delegation,
               type_generation,
               type_influence,
               type_association,
               merge_generation,
               merge_start]
    for q in queries:
        if not check(g, q):
            print('typeconstraints')
            return False

    return True


def check(g, q):
    bindings = g.query(q)
    if len(bindings) > 0:
        #for b in bindings:
        #    print b
        #print q
        return False
    else:
        return True

def checkCycle(g):
    g1 = orderingConstraints(g)
    res = check(g1, qCheckCycle)
    if not res:
        print('cycle')
    return res


def validate(filename):
    g = rdflib.Graph()
    g.parse(filename, format='turtle')
    #print g.serialize(format='turtle')

    result = checkTypeConstraints(g) and \
                checkKeyConstraints(g) and \
                checkCycle(g) and \
                checkUniqueness(g) and \
                checkImpossibility(g)
    print(filename + ' ' + str(result))
    if result == True:
        return 'PASS'
    else:
        return 'FAIL'


    #print g.serialize(format='turtle')

def testCycleDetection():
    g = rdflib.Graph()
    processUpdate(g, qMakeCycle)
    print(g.serialize(format='turtle'))
    print(checkCycle(g))

def testAllConstraints(dirs):
    dir = os.listdir(dirs)
    notcorrect = 0
    numberoftestcases = 0
    for f in dir:
        if f.endswith('.ttl'):
            numberoftestcases = numberoftestcases + 1
            res = validate(dirs + f)
            if not res in f:
                print("Not correct")
                notcorrect = notcorrect + 1

    print('(' + str(numberoftestcases - notcorrect) + '/' + str(numberoftestcases) + ')')




#testCycleDetection()
#testAllConstraints('./constraints/')
#testAllConstraints('./provo-constraints/')
#testAllConstraints('./provdm-constraints/')

#the one that doesn't work
#validate('./provdm-constraints/prov-dm-ex23_start-PASS.ttl')


def main():
    # parse command line options
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h", ["help"])
    except getopt.GetoptError as msg:
        print(msg)
        print("for help use --help")
        sys.exit(2)
    # process options
    for o, a in opts:
        if o in ("-h", "--help"):
            print(__doc__)
            sys.exit(0)

    for arg in args:
        validate(arg)

if __name__ == "__main__":
    main()

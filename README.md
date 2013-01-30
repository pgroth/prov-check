prov-check
==========

Making sure your provenance is all good.

This project is an implementation of the [W3C Constraints of the PROV Data Model](http://www.w3.org/TR/prov-constraints/) using [SPARQL](http://www.w3.org/TR/sparql11-query/).

##Current Status##

* Be kind - this is super alpha software
* You can find the code in provcheck/provconstraints.py
* All constraints defined in the documented are implemented.
* Passing (279/280) test cases: all 157 unit tests, 81 prov-o examples and 40/41 prov-dm examples as defined in the [PROV-Constraints Test Case Guide](https://dvcs.w3.org/hg/prov/raw-file/default/testcases/process.html)
* Uses a lot of sparql 1.1
* Currently, only supports qualified "style" prov forms
* Works only with prov-o serializations

##TODO##
* Support expansion of short forms
* Do a check of all blank node handling
* Recheck that all inferences are correctly handled
* Nice documentation
* Add a license
* Separate sparql queries out from code
* Remote check

----------------------
This project prov:wasDerivedFrom https://github.com/pgroth/prov-constraints-validator-spin

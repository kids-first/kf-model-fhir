# General FHIR Feedback and Questions

## Guidance process

- Community issues, feedback, and guidance channels are scattered across https://chat.fhir.org, http://community.fhir.org/ (not https!), https://confluence.hl7.org/display/FHIR, https://www.hl7.org/myhl7/managelistservs.cfm?ref=nav, https://jira.hl7.org/projects/FHIR/issues/, https://gforge.hl7.org/gf/project/fhir, https://stackoverflow.com/questions/tagged/hl7_fhir, and who knows where else. That really needs to be consolidated and clarified.
  - Differentiation for its own sake (chat vs community) should be eliminated.
  - If there's an expectation of adherence to a formal feedback process, link to the process first (https://confluence.hl7.org/display/HL7/Specification+Feedback#SpecificationFeedback-newSubmittingnewfeedback), not to a submission page (https://jira.hl7.org/projects/FHIR/issues).
  - Deactivate obsolete venues (gforge vs jira, wiki vs confluence).

## StructureDefinitions

- The definition inheritence model works differently to seemingly every programming language model. SDs themselves only support single inheritence, and then each instance declaration can declare conformance to multiple SDs of one single base type (presumably as long as those SDs are all compatible with each other). In contrast, programming languages that support multiple object inheritence coordinate the inheritence chain in the object _definition_ and then create instances of those singular definitions. This difference is a bit confusing. For one thing, it creates a weird type identification inconsistency where e.g. if you generate an instance of a subdefinition of `Patient` called `Participant`, then that instance is one of type `Patient` _not_ of `Participant` even though it must conform to `Participant`'s requirements which could deviate significantly from `Patient`'s.

- There are odd redundancies or seemingly unnecessary attributes on conformance resources:
  - Type could be generated from baseDefinition. Why have both?
  - Type vs resourceType is confusing. Should be base_type and type.
  - ID could be generated from url. Why have both?

## Identifiers

- Why are underscores not allowed in resource IDs? Use of underscores is extremely prevalent in identifier schemes.

## SearchParameter

- Are there examples for how to auto-create and add SearchParameters for Extensions?
- Is there a document showing what SearchParameter type to use for different value types?
- SearchParameter multi-resource applicability: <https://chat.fhir.org/#narrow/stream/179166-implementers/topic/SearchParameter.20that.20applies.20to.20multiple.20resource.20types>
- `"status"` is a field requiring PublicationStatus code. When set to `"draft"`, a SearchParameter is found to be not working. In a development setting, is there a way to flag if this SearchParameter is in use?
- What is the function of `'sliceName'` in a StructureDefinition and how does it relate to Extension SearchParameters?
- Is there documentation on FHIR path? 
- We would prefer to use a standard path traversal language, not something custom. FHIR lets you use XPATH, but XPATH is for XML. How do we apply it to JSON?

## CodeSystem

- Ambiguity in rules for setting the URI: <https://chat.fhir.org/#narrow/stream/179202-terminology/topic/code.20system.20URI.20determination.20ambiguity>

## ValueSet

- Is CodeSystem an upstream dependency of ValueSet? Can we DELETE and re-POST CodeSystem without cascade DELETE and re-POST of ValueSet?

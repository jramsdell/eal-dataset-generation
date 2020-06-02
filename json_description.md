# Json Object Definitions

**Location**:
* location_id :: Str // Hash of (section_id + paragraph_id) 
- page_id :: String
* page_title :: String
- paragraph_id :: String
* sectionId :: [String] // [page_id, section_id)
* sectionHeadings :: [String] // [section_heading]

**AnnotatedText**:
- content :: String
- entities :: [EntityMention]

**EntityMention**: 
- entity_name :: String
- entity_id :: String
- mention :: String
- target_mention :: String
- start :: Int
- end :: Int

**Context**:
- target_entity :: String
- location :: Location
- sentence :: AnnotatedText
- paragraph: :: AnnotatedText

**Aspect**:
- aspect_id :: String // section_id
- location :: Location
- aspect_content :: AnnotatedText
- aspect_name :: String   // a.k.a. the section's header  


**AspectLinkExample**:
- unhashed_id :: String
- id :: String (MD5 hash of unhashed_id
- context :: Context 
- true_aspect :: String // aspect id of the correct candidate aspect
- candidate_aspects :: [Aspect] 


# Json Object Details

### Location

**location_id :: Str**
This is 

- page_id :: String
* page_title :: String
- paragraph_id :: String
* sectionId :: [String] // [page_id, section_id)
* sectionHeadings :: [String] // [section_heading]

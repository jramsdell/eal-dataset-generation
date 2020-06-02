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
A *Location* provides information about where the context, or a canddidate aspect, are located within a page.

**location_id :: Str**  
This is a unique id assigned to each location.

**page_id :: String**  
The id of the page in which a context/aspect is located (e.x. "enwiki:Chocolate%20chip%20cookie").

**page_title :: String**  
The title of the page in which a context/aspect is located (e.x. "Chocolate chip cookie").

**paragraph_id :: Optional<String>**  
The id of the paragraph in which a context is located. As this only applies to the context, Aspect Locations do not include this field.

**section_id :: [String]**
This is a two element array that contains the page_id and section_id as elements.

* sectionHeadings :: [String] // [section_heading]

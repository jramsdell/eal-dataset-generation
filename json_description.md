# Json Object Definitions

**Location**:
* location_id :: Str // Hash of (section_id + paragraph_id) 
- page_id :: String
* page_title :: String
- paragraph_id :: Optional<String>
* sectionId :: [String] // [page_id, section_id)
* sectionHeadings :: [String] // [section_heading]

**AnnotatedText**:
- content :: String
- entities :: [EntityMention]

**EntityMention**: 
- entity_name :: String
- entity_id :: String
- mention :: String
- target_mention :: Optional<Boolean>
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
This is a two element array that contains the page_id and section_id as elements. (e.x. ["enwiki:Chocolate%20chip%20cookie", "Composition%20and%20variants"])

**sectionHeadings :: [String]** 
In this implementation, the array only contains a single element, which is the heading of a top-level section. (e.x. ["Composition and variants"])

## AnnotatedText
An *AnnotatedText* represents a piece of text (sentence or paragraph) that has been annotated with entity links.

**content :: String**  
This is the raw, unprocessed text that was annotated.

**entities :: [EntityMention]**  
This is a list of linked entities that are contained in the text.

## EntityMention
An *EntityMention* represents a linked entity found within text. For this dataset, an entity is a link to a Wikipedia page. There are additional information associated with the link (such as the anchor text) which are also stored as fields.

**entity_name :: String**  
The name of the Wikipedia page that the entity links to (e.x. "Chocolate chip cookies")

**entity_id :: String**  
The unique id of the Wikipedia page that the entity links to (e.x. "enwiki:Chocolate%20chip%20cookies").

**mention :: String**  
The anchor text of the entity link.


target_mention :: Boolean
- start :: Int
- end :: Int

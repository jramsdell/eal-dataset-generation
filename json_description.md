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
- id :: String // (MD5 hash of unhashed_id)
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


**target_mention :: Optional<Boolean>**  
  This field is only included in the Context's "sentence" and "paragraph" entities.
  EntityMentions located in Aspects do not utilize this field.
  When True, it represents that this is the target entity mention that links to a section in a Wikipedia page, and this is used to determine the ground truth for candidate aspects. 
  
**start :: Int**  
The start coordinates of the anchor text located in the raw, unprocessed text in which the link occurs.

**end :: Int**  
The end coordinates of the anchor text located in the raw, unprocessed text in which the link occurs.

## Context
The *Context* represents the sentence and paragraph that contains the target entity mention (that links to a Wikipedia Aspect).

**target_entity : String**  
The page id of the target entity contained within the context. 

**location :: Location**  
The Location describing in what page/section the context occurs.

**sentence  :: AnnotatedText**  
The sentence containing the target entity.

**paragraph: :: AnnotatedText**  
The paragraph containing the target entity.

## Aspect
An *Aspect* in this dataset represents a top-level section within a Wikipedia page.
The Aspect contains information about where in a page it is located, along with text and associated annotations.

**aspect_id :: String** 
The unique id for the aspect. For this dataset, it is: page_id + "/" + section_id (e.x. "enwiki:Chocolate%20chip%20cookie/Composition%20and%20variants").

**location :: Location**  
Provides information about the page, and section, that the Aspect represents.

**aspect_content :: AnnotatedText** 
Contains the raw text of the associated section, and also the entities linked to this section in Wikipedia.
Note that this also includes the text of any sub-sections contained in the section (and the headers of these sub-sections).

**aspect_name :: String**  
The name of the aspect, which in this dataset is associated with the name of a top-level section (e.x. "Composition and variants").


## AspectLinkExample
An *AspectLinkExample* is an example where an entity mention links to a section in a Wikipedia page (most entity links in Wikipedia do not directly link to sections). This contains all the information relevant to this example (the entity that was linked, the context surrounding the target entity, the aspects of the page that the entity linked to, etc.).

**unhashed_id :: String**  
A unique id used to generate a hashed id. Its format is: page_id/section_id/paragraph_id(target_entity_mention_start, target_entity_mention_end)

**id :: String**  
This is the MD5 hashed version of the unhashed_id. *Note*: This is the id that is used to uniquely refer to each AspectLinkExample in the benchmark files.

**context :: Context**  
The context in which the target entity is occurs (see Context for more information).

**true_aspect :: String**  
This represents the ground truth of the example, in which an entity mention links to a section in a Wikipedia page.
The associated section is the "true aspect", as opposed to the other sections contained in that page.
This field is the aspect_id field found within the correct Aspect (which is located among the Aspects inside the candidate_aspects list).

**candidate_aspects :: [Aspect]**  
The list of Aspects representing the top-level sections of the Wikipedia page that was linked to by the target entity mention. 

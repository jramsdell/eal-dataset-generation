Location:
* location_id :: Str // Hash of (section_id + paragraph_id) 
- page_id :: String
* page_title :: String
- paragraph_id :: String
* sectionId :: [String] // [page_id, section_id)
* sectionHeadings :: [String] // [section_heading]

AnnotatedText:
- content :: String
- entities :: [EntityMention]

EntityMention: 
- entity_name :: String
- entity_id :: String
- mention :: String
- target_mention :: String
- start :: Int
- end :: Int

Context:
- target_entity :: String
- location :: Location
- sentence :: AnnotatedText
- paragraph: :: AnnotatedText


Aspect:
- aspect_id :: String // page_id + section_id
- location :: Location
- aspect_content :: AnnotatedText
- aspect_name :: String   // a.k.a. the section's header  


AspectLinkExample:
- unhashed_id :: String // 
- id :: String (MD5 hash of unhashed_id
- context :: Context 
- true_aspect :: Id   // should be `aspect_id`
- candidate_aspects :: [Aspect] 


Does this make sense? 

I think your current fields map 1:1 on this. But let me know your thoughts...

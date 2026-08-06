============================================================
CLIP_001 (direct prompt-to-video)
============================================================
DURATION: 10 seconds
SCENE: Cozy family living room, warm wood tones, soft fabric sofa, warm afternoon gold light. Opening clip -- no prior state.
CHARACTER ANIMATION: Zayd walks in from screen-left, grocery bag swinging gently, tired-but-cheerful expression. Amira turns her head to watch him enter.
GEMINI_CHARACTER_LOCK -- char_001_zayd: 7-year-old boy, warm light-brown skin, round face, very large deep-brown eyes, thick dark-brown hair with small forehead tuft, soft-blue knee-length thobe, cream trousers, peach slip-on shoes.
GEMINI_CHARACTER_LOCK -- char_002_amira: 5-year-old girl, warm light-brown skin, rosy round cheeks, very large hazel eyes, soft lavender hijab, pale-yellow knee-length dress, mint leggings, cream shoes.
VOICE IDENTITY -- char_001_zayd: bright eager boy, medium-high pitch, medium pace (faster when excited), warm and innocent tone. (not speaking this clip)
VOICE IDENTITY -- char_002_amira: sweet gentle young girl, high natural pitch, slow-medium pace, soft and emotionally clear tone. (not speaking this clip)
SCENE DIRECTION: Zayd tired-but-cheerful; Amira neutral, curious.
DIALOGUE + EXACT TIMING: none this clip.
WARDROBE: wardrobe_zayd_default, wardrobe_amira_default -- unchanged from canonical.
LOCATION: loc_family_living_room.
PROP STATE: prop_grocery_bag_01 held in Zayd's hand throughout.
ENVIRONMENT ANIMATION: none major, static room.
CAMERA: wide shot, eye-level, static, no movement. Screen direction: Zayd enters from left, ends left-of-center. Ending frame: Zayd fully in frame left-of-center, Amira right-of-center watching him.
LIGHTING: warm afternoon gold interior light, soft shadows.
CONTINUITY FROM PREVIOUS CLIP: none (opening clip).
ANIMATION STYLE: 3D animated children's feature-film style, soft rounded shapes, large expressive eyes, warm pastel palette, cinematic soft lighting, smooth natural motion, natural blinking and breathing on both characters.
AVOID: do not alter either character's clothing, skin tone, face shape, or proportions from the locks above. Do not add extra characters. Do not exceed 10 seconds. Do not give either character dialogue this clip.

============================================================
CLIP_002 (direct prompt-to-video)
============================================================
DURATION: 10 seconds
SCENE: Same living room, continuing directly from CLIP_001.
CHARACTER ANIMATION: Zayd sets the grocery bag down with a soft motion. Amira's expression shifts to a warm grateful smile as she turns fully toward him.
GEMINI_CHARACTER_LOCK -- char_001_zayd: (same as CLIP_001)
GEMINI_CHARACTER_LOCK -- char_002_amira: (same as CLIP_001)
VOICE IDENTITY -- char_002_amira: sweet gentle young girl, high natural pitch, slow-medium pace, soft and emotionally clear tone.
VOICE IDENTITY -- char_001_zayd: bright eager boy, medium-high pitch, medium pace, warm and innocent tone. (not speaking this clip)
SCENE DIRECTION: Amira grateful and warm; Zayd neutral, attentive, listening.
DIALOGUE + EXACT TIMING: char_002_amira, 2.5s-5.8s: "Alhamdulillah, thank you for helping me carry these!"
WARDROBE: unchanged from CLIP_001.
LOCATION: loc_family_living_room (same).
PROP STATE: prop_grocery_bag_01 -- transitions from Zayd's hand to the floor during this clip.
ENVIRONMENT ANIMATION: none major.
CAMERA: medium shot, eye-level, static. Screen direction unchanged (Zayd left, Amira right). Ending frame: Amira mid-smile just after finishing her line.
LIGHTING: same warm afternoon light, continuous.
CONTINUITY FROM PREVIOUS CLIP: inherits CLIP_001's ending state -- Zayd just finished entering, now setting the bag down; Amira now fully turned toward him.
ANIMATION STYLE: 3D animated children's feature-film style, soft rounded shapes, large expressive eyes, warm pastel palette, cinematic soft lighting, accurate lip sync on Amira only, no mouth movement on Zayd, natural blinking and breathing on both.
AVOID: do not alter clothing/skin/face from locks. Do not exceed 10 seconds. Do not speed up Amira's dialogue -- it fits naturally in the window. Do not give Zayd dialogue this clip.

============================================================
CLIP_003 (direct prompt-to-video)
============================================================
DURATION: 10 seconds
SCENE: Same living room, continuing directly from CLIP_002.
CHARACTER ANIMATION: Zayd's expression brightens into a full open smile, small natural shrug during his line. Amira listens with a soft smile and gentle nod.
GEMINI_CHARACTER_LOCK -- char_001_zayd: (same as CLIP_001)
GEMINI_CHARACTER_LOCK -- char_002_amira: (same as CLIP_001)
VOICE IDENTITY -- char_001_zayd: bright eager boy, medium-high pitch, medium pace, warm and innocent tone.
VOICE IDENTITY -- char_002_amira: sweet gentle young girl, high natural pitch, slow-medium pace, soft tone. (not speaking this clip)
SCENE DIRECTION: Zayd warm and content; Amira content, listening.
DIALOGUE + EXACT TIMING: char_001_zayd, 2.0s-5.2s: "Of course! That's what family is for."
WARDROBE: unchanged.
LOCATION: loc_family_living_room (same).
PROP STATE: prop_grocery_bag_01 resting on the floor near Zayd's feet, not held.
ENVIRONMENT ANIMATION: none major.
CAMERA: medium-close shot, eye-level, static. Screen direction unchanged. Ending frame: both characters smiling warmly.
LIGHTING: same warm light, continuous.
CONTINUITY FROM PREVIOUS CLIP: inherits CLIP_002's ending state -- Amira just finished thanking him, bag now on the floor.
ANIMATION STYLE: same as CLIP_001/002, accurate lip sync on Zayd only, no mouth movement on Amira, natural blinking and breathing.
AVOID: do not alter clothing/skin/face from locks. Do not exceed 10 seconds. Do not give Amira dialogue this clip. Do not reverse the established screen positions.

============================================================
CLIP_004 (direct prompt-to-video)
============================================================
DURATION: 10 seconds
SCENE: Transition from loc_family_living_room to loc_family_kitchen -- warm family kitchen, wooden dining table, tiled counter, soft daytime light. Explicit, scripted location change.
CHARACTER ANIMATION: both characters walk together toward the kitchen counter, natural walking motion. Zayd carries prop_grocery_bag_01 and sets it on the counter near the end.
GEMINI_CHARACTER_LOCK -- char_001_zayd: (same identity as CLIP_001-003)
GEMINI_CHARACTER_LOCK -- char_002_amira: (same identity as CLIP_001-003)
VOICE IDENTITY -- char_001_zayd / char_002_amira: (same profiles as above; neither speaks this clip)
SCENE DIRECTION: both neutral, purposeful, content.
DIALOGUE + EXACT TIMING: none this clip.
WARDROBE: unchanged from CLIP_001-003.
LOCATION: loc_family_kitchen (NEW -- camera axis intentionally re-established here, not an error).
PROP STATE: prop_grocery_bag_01 -- picked back up by Zayd off-screen between clips, carried here, set on the counter by the end of this clip.
ENVIRONMENT ANIMATION: minimal ambient kitchen detail, no major background action.
CAMERA: wide shot, eye-level, slow pan following their movement left to right. Ending frame: both standing at the counter, bag set down.
LIGHTING: soft daytime kitchen light, different baseline from the living room's warm gold (real room change, not a lighting error).
CONTINUITY FROM PREVIOUS CLIP: inherits CLIP_003's ending emotional state (warm, content) but explicitly changes location per the script.
ANIMATION STYLE: same house style, natural walking motion, natural blinking and breathing.
AVOID: do not alter clothing/skin/face from locks. Do not exceed 10 seconds. Do not give either character dialogue this clip. Do not lose the grocery bag prop between clips.

============================================================
CLIP_005 (direct prompt-to-video)
============================================================
DURATION: 10 seconds
SCENE: Same kitchen, continuing directly from CLIP_004 -- both now seated at the table.
CHARACTER ANIMATION: both characters bow their heads slightly together.
GEMINI_CHARACTER_LOCK -- char_001_zayd: (same identity as above)
GEMINI_CHARACTER_LOCK -- char_002_amira: (same identity as above)
VOICE IDENTITY -- char_001_zayd: bright eager boy, medium-high pitch, medium pace, warm and innocent tone.
VOICE IDENTITY -- char_002_amira: sweet gentle young girl, high natural pitch, slow-medium pace, soft tone.
SCENE DIRECTION: both calm, sincere.
DIALOGUE + EXACT TIMING: char_001_zayd AND char_002_amira together, 2.0s-3.5s: "Bismillah."
WARDROBE: unchanged.
LOCATION: loc_family_kitchen (same as CLIP_004).
PROP STATE: prop_grocery_bag_01 now off-frame on the counter, not held or visible.
ENVIRONMENT ANIMATION: none major.
CAMERA: medium shot, eye-level, static. Ending frame: both seated calmly, just finished speaking.
LIGHTING: same daytime kitchen light as CLIP_004, continuous.
CONTINUITY FROM PREVIOUS CLIP: inherits CLIP_004's ending state -- both now seated at the table, bag on the counter.
ANIMATION STYLE: same house style, accurate synchronized lip sync on both speakers, natural blinking and breathing.
AVOID: do not alter clothing/skin/face from locks. Do not exceed 10 seconds. Do not modify the exact wording "Bismillah" (real dua_002 evidence -- must not be paraphrased).

============================================================
CLIP_006 (direct prompt-to-video)
============================================================
DURATION: 10 seconds
SCENE: Same kitchen, continuing directly from CLIP_005, closing beat of the scene.
CHARACTER ANIMATION: Amira's expression brightens into a content, grateful smile.
GEMINI_CHARACTER_LOCK -- char_001_zayd: (same identity as above)
GEMINI_CHARACTER_LOCK -- char_002_amira: (same identity as above)
VOICE IDENTITY -- char_002_amira: sweet gentle young girl, high natural pitch, slow-medium pace, soft tone.
VOICE IDENTITY -- char_001_zayd: bright eager boy, medium-high pitch, medium pace, warm tone. (not speaking this clip)
SCENE DIRECTION: Amira content and grateful; Zayd content, listening.
DIALOGUE + EXACT TIMING: char_002_amira, 2.0s-4.0s: "Alhamdulillah, that was good."
WARDROBE: unchanged.
LOCATION: loc_family_kitchen (same as CLIP_004/005).
PROP STATE: prop_grocery_bag_01 remains off-frame on the counter.
ENVIRONMENT ANIMATION: none major.
CAMERA: medium-close shot, eye-level, static, gentle fade out beginning at 9.0s. Ending frame: both smiling warmly, faded to black.
LIGHTING: same daytime kitchen light, continuous, gentle instrumental music swell begins at 8.0s.
CONTINUITY FROM PREVIOUS CLIP: inherits CLIP_005's ending state -- both just said Bismillah, now finishing the meal.
ANIMATION STYLE: same house style, accurate lip sync on Amira only, natural blinking and breathing.
AVOID: do not alter clothing/skin/face from locks. Do not exceed 10 seconds. Do not modify the exact wording "Alhamdulillah" (real dua_003 evidence). This is the final clip -- do not add continuity-to instructions for a nonexistent CLIP_007.

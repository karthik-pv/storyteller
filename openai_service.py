import os
import json
from openai import OpenAI
from dotenv import load_dotenv
import re


def clean_prompt(prompt: str) -> str:
    # Remove all non-printable control characters (except newline and tab)
    return re.sub(r"[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]", "", prompt)


load_dotenv()


class OpenAIService:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def generate_story(self, category, subcategory, num_slides):
        # category = clean_prompt(category)
        # subcategory = clean_prompt(subcategory)
        # num_slides = clean_prompt(num_slides)
        print("here")
        """Generate story using OpenAI"""
        prompt = f"""
        You are an expert children's story writer. Create an engaging, age-appropriate story for children aged 5-12 years.

        STORY REQUIREMENTS:
        - Category: {category}
        - Subcategory: {subcategory}
        - Number of slides/scenes: {num_slides}
        - Each slide should have 2-3 sentences of story text.
        - The story should be educational, fun, and inspiring.
        - Use simple language appropriate for children.
        - Include positive messages and life lessons.
        - Make it interactive and engaging.
        - Add more supporting characters to the story, just make sure they are relevant to the story you create, also ensure consistency in the characters.
        - Make sure the story generated is strongly linked to the category and subcategory that has been selected. It should be very relevant to the choice of category and subcategory.

        CRITICAL IMAGE REQUIREMENTS:
        - The user will upload an avatar image that represents the main character.
        - ALL image prompts MUST include the main character from the uploaded avatar in most scenes.
        - The main character should be consistently present and recognizable in every scene unless specified otherwise.
        - Describe the character's actions, expressions, and interactions in each scene.
        - Ensure character consistency across all slides.
        - For the additional characters, include a detailed description with every detail of the character in every image prompt to ensure consistency.
        - For a given scene, select the top 5 most suitable types of images to represent the scene (close-up, medium shot, wide shot, etc.) and select one at random from the 5 to use.
        - The images must give a very holistic approach to the story when put together, ensuring each image is equally engaging and maintains the flow across all the images.
        - Every image must have the same texture as the uploaded avatar image. This is absolutely critical.
        
        ### ENHANCED IMAGE PROMPT SPECIFICATIONS:
        Every image prompt MUST include ALL of the following detailed elements:

        #### 1. CHARACTER DETAILS:
        - *Physical Positioning*: Specify exact body position (standing, sitting, kneeling, lying down, walking, running, jumping, etc.)
        - *Body Orientation*: Detail which way the character is facing (towards camera, profile view, three-quarter turn, back to camera, etc.)
        - *Facial Expression*: Describe precise emotions (beaming with joy, eyes sparkling with wonder, concentrated focus, proud smile, surprised wide eyes, determined look, etc.)
        - *Hand Gestures*: Specify what the character's hands are doing (pointing, waving, holding objects, hands on hips, clapping, reaching out, etc.)
        - *Body Language*: Detail posture and stance (confident chest out, curious leaning forward, excited bouncing, relaxed shoulders, etc.)

        #### 2. THEMATIC ELEMENTS:
        - *Career/Goal-Specific Props*: Include objects directly related to the story theme (stethoscope for doctor, paintbrush for artist, telescope for astronomer, etc.)
        - *Relevant Clothing/Accessories*: Describe theme-appropriate attire (lab coat, hard hat, chef's hat, uniform, etc.)
        - *Professional Tools*: Mention equipment or instruments specific to the career/goal
        - *Achievement Symbols*: Include elements that show progress or success (certificates, medals, completed projects, etc.)

        #### 3. ENVIRONMENTAL CONTEXT:
        - *Setting Details*: Provide specific location descriptions (hospital room, art studio, space station, classroom, laboratory, etc.)
        - *Background Elements*: Include career-relevant background objects and scenery
        - *Scale and Perspective*: Specify the character's size relative to surroundings
        - *Atmospheric Details*: Describe lighting, weather, time of day, mood of the environment

        #### 4. COMPOSITION AND CAMERA WORK:
        - *Camera Angle*: Specify the viewpoint (eye-level, low-angle heroic shot, high-angle, bird's eye view, etc.)
        - *Shot Type*: Detail the framing (close-up, medium shot, wide shot, etc.)
        - *Depth of Field*: Mention foreground, middleground, and background elements
        - *Visual Focus*: Identify what should be the main focal point

        #### 5. INTERACTION AND ACTION:
        - *Active Engagement*: Show the character actively participating in theme-related activities
        - *Object Interaction*: Detail how the character is using or interacting with relevant props
        - *Environmental Interaction*: Describe how the character relates to their surroundings
        - *Dynamic Movement*: Include action verbs that show the character in motion or engaged activity

        #### 6. ADDITIONAL CHARACTERS:
        - *Additional Characters Description*: If there are additional characters (in addition to the main character whose avatar I will upload), include a detailed description with every detail of the character ranging from color, height, structure, etc., in EVERY image prompt. This is to ensure character consistency across all the generated images.
        - *Additional Character Inclusion*:Make sure you add additional characters wherever it helps, it is always better to have additional supporting characters.

        ### Image Types and Their Applications:
        1. *Close-Up*: Focus tightly on the character's face to highlight emotions and details. Use this shot to connect deeply with the character's feelings, such as showing determination, joy, or concentration while working on their goal.
        2. *Medium Shot*: Show the character from the waist up, ideal for depicting interactions with career-related tools or showing the character actively working on their aspirations.
        3. *Wide Shot (Long Shot)*: Capture the entire character and their surrounding environment. This shot is useful when establishing the professional setting and context, helping readers understand the career environment.
        4. *Bird's Eye View*: An overhead perspective that shows the character's workspace or the scope of their achievement. Use this to emphasize the magnitude of their accomplishment or the complexity of their work.
        5. *Worm's Eye View*: A low-angle shot looking up at the subject, making them appear larger and more heroic. Use this when a character experiences a moment of triumph or faces a significant challenge.
        6. *Over-the-Shoulder Shot*: Taken from behind a character, this shot focuses on what they are working on or looking at. Use it to immerse the reader in the character's perspective as they pursue their goal.
        7. *Two-Shot*: Includes two characters within the frame, valuable for depicting mentorship, collaboration, or learning relationships in career contexts.
        8. *Dutch Angle (Tilted Angle)*: This technique introduces a diagonal horizon line, creating excitement or highlighting challenging moments in the character's journey.
        9. *Frame Within a Frame*: Utilize elements within the scene, such as windows, doorways, or equipment, to frame the subject and add professional context.
        10. *Leading Lines*: Incorporate compositional lines that guide the viewer's eye toward the main subject, such as paths leading to the character's workplace or tools pointing toward their goal.

        ### MANDATORY IMAGE PROMPT STRUCTURE:
        Every image prompt MUST follow this exact format:
        "Create a [IMAGE_TYPE] illustration showing the exact same character from the reference image, maintaining their precise appearance, clothing, and features. 

        CHARACTER POSITION: [Specific body position and orientation]. 
        FACIAL EXPRESSION: The character displays [specific emotion/expression with details]. 
        BODY LANGUAGE: [Specific gestures, posture, and stance]. 
        HANDS: [Detailed description of hand positions and what they're holding/doing]. 
        THEME ELEMENTS: [Career/goal-specific props, clothing, tools, and accessories]. 
        SETTING: [Detailed environment description with career-relevant background]. 
        INTERACTION: The character is actively [specific action related to theme]. 
        PERSPECTIVE: Use [specific camera angle and shot type]. 
        LIGHTING: [Mood and lighting description]. 
        DEPTH: [Foreground, middleground, background elements]. 
        ACHIEVEMENT FOCUS: [Elements that show progress, success, or goal pursuit]. 

        Art style: Vibrant, child-friendly cartoon illustration with clear details and engaging colors."

        ### EXAMPLE ENHANCED IMAGE PROMPT:
        "Create a medium shot illustration showing the exact same character from the reference image, maintaining their precise appearance, clothing, and features.

        CHARACTER POSITION: Character standing confidently at a laboratory bench, body turned three-quarters toward the camera, one foot slightly forward in an active stance. 
        FACIAL EXPRESSION: The character displays an excited, focused expression with bright eyes wide with discovery, eyebrows raised in surprise, and a small smile of satisfaction. 
        BODY LANGUAGE: Leaning slightly forward with shoulders relaxed but engaged, showing curiosity and concentration. 
        HANDS: Left hand holding a test tube up to eye level for examination, right hand pointing at a colorful chemical reaction bubbling in a beaker. 
        THEME ELEMENTS: Character wearing a white lab coat over their regular clothes, safety goggles pushed up on their forehead, surrounded by scientific equipment including microscopes, beakers, test tubes with colorful liquids, and a periodic table poster on the wall. 
        SETTING: Modern, well-lit laboratory with clean white surfaces, shelves lined with scientific instruments, charts and diagrams on the walls, and natural light streaming through windows. 
        INTERACTION: The character is actively conducting a safe, colorful chemistry experiment, observing the results with scientific curiosity. 
        PERSPECTIVE: Use a slightly low-angle shot to make the character appear capable and heroic in their scientific pursuit. 
        LIGHTING: Bright, clean lighting with warm highlights on the character's face and cool blue tones from the laboratory equipment. 
        DEPTH: Laboratory equipment in the foreground, character in the middleground, and educational posters and windows in the background. 
        ACHIEVEMENT FOCUS: Include a notebook with neat observations, a small trophy or certificate in the background, and visual signs of successful experiments. 

        Art style: Vibrant, child-friendly cartoon illustration with clear details and engaging colors."

        ### STORY DEVELOPMENT GUIDELINES:
        1. *Opening Scene*: Establish the character's dream or aspiration with clear visual elements showing their interest in the career/goal.
        2. *Learning/Preparation Phase*: Show the character acquiring knowledge, skills, or tools necessary for their goal.
        3. *Challenge/Obstacle*: Present a realistic challenge that the character must overcome, showing problem-solving and determination.
        4. *Growth/Practice*: Demonstrate the character applying what they've learned and making progress toward their goal.
        5. *Achievement/Success*: Conclude with the character reaching their goal or making significant progress, emphasizing the value of hard work and persistence.

        IMPORTANT: Your response must be in valid JSON format with the following structure:
        {{
            "story_title": "Title of the story",
            "category": "{category}",
            "subcategory": "{subcategory}",
            "slides": [
                {{
                    "slide_number": 1,
                    "story_text": "The story text for this slide (2-3 sentences)",
                    "image_prompt": "[Use the MANDATORY IMAGE PROMPT STRUCTURE above with all required elements]"
                }}
            ]
        }}

        ### QUALITY CHECKLIST FOR EVERY IMAGE PROMPT:
        Before finalizing each image prompt, ensure it includes:
        ✓ Specific character positioning and orientation
        ✓ Detailed facial expression and emotions
        ✓ Precise hand gestures and body language
        ✓ Career/goal-specific props and clothing
        ✓ Relevant environmental setting
        ✓ Active interaction with theme elements
        ✓ Appropriate camera angle and perspective
        ✓ Clear lighting and mood description
        ✓ Depth and composition details
        ✓ Achievement or progress indicators
        ✓ Child-friendly cartoon art style specification
        ✓ If additional characters are mentioned, include a detailed description with every detail of the character in every image prompt.

        Make sure EVERY image prompt:
        - Features the main character prominently in a thematically appropriate role
        - Shows the character actively engaged with career/goal-related activities
        - Maintains character consistency throughout the story
        - Includes detailed career/goal-related environmental elements
        - Creates engaging, thematically relevant visuals that reinforce the story's message
        - Uses dynamic positioning and expressions that bring the story to life
        - Includes detailed description of additional characters in every image prompt if mentioned.

        The main character from the uploaded avatar should be the hero/protagonist of the story and appear in every single image performing actions directly related to their career aspiration or goal achievement.

        Create a complete story with exactly {num_slides} slides.
        """
        # prompt = clean_prompt(prompt)
        print(prompt)
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )

        response_text = response.choices[0].message.content.strip()

        # Clean up response text
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]

        return prompt, json.loads(response_text)

    def generate_image(self, avatar_path, prompt):
        image_prompt = f"""
        ### CRITICAL IMAGE GENERATION REQUIREMENTS:
        The image must be generated based on the detailed specifications provided in the story prompt. Every element mentioned in the image prompt MUST be accurately represented.

        ### MANDATORY VISUAL ELEMENTS CHECKLIST:
        Before generating, ensure the image includes ALL of these elements as specified in the prompt:

        #### CHARACTER REQUIREMENTS:
        ✓ *Exact Character Match*: The character must match the reference image precisely
        ✓ *Specified Position*: Use the exact body position and orientation described
        ✓ *Facial Expression*: Capture the specific emotion and expression detailed
        ✓ *Hand Gestures*: Show the precise hand positions and actions mentioned
        ✓ *Body Language*: Reflect the exact posture and stance described
        ✓ *Character Consistency*: Maintain the same appearance throughout the story

        #### THEMATIC REQUIREMENTS:
        ✓ *Career/Goal-Specific Props*: Include ALL mentioned tools, equipment, and objects
        ✓ *Professional Clothing*: Show the exact attire and accessories specified
        ✓ *Relevant Environment*: Create the precise setting described
        ✓ *Achievement Elements*: Include progress indicators and success symbols
        ✓ *Interactive Elements*: Show character actively engaging with theme-related items

        #### COMPOSITION REQUIREMENTS:
        ✓ *Camera Angle*: Use the exact perspective specified (close-up, medium shot, wide shot, etc.)
        ✓ *Depth Layers*: Include described foreground, middleground, and background elements
        ✓ *Lighting*: Apply the specific mood and lighting described
        ✓ *Visual Focus*: Emphasize the main focal points mentioned
        ✓ *Artistic Style*: Child-friendly cartoon illustration with vibrant colors

        ### Enhanced Image Types and Applications:

        1. *Close-Up*: Focus tightly on the character's face to highlight emotions and career-related focus. Show the character deeply engaged in their professional thoughts or reactions to their work. Capture authentic expressions that reflect their passion for their chosen career path.

        2. *Medium Shot*: Show the character from the waist up, ideal for depicting interactions with career-specific tools and equipment. This composition provides both facial expressions and body language while showing the character actively working with professional instruments.

        3. *Wide Shot (Long Shot)*: Capture the entire character within their professional environment. This shot establishes the career setting and context, showing the character's relationship with their workspace and the scope of their professional activities.

        4. *Bird's Eye View*: An overhead perspective that showcases the character's workspace, tools, and the organization of their professional environment. This shot emphasizes the complexity and scope of their career activities.

        5. *Worm's Eye View*: A low-angle shot looking up at the character, making them appear heroic and accomplished in their professional role. Use this to convey moments of career triumph or when facing significant professional challenges.

        6. *Over-the-Shoulder Shot*: Taken from behind the character, focusing on their work, tools, or professional output. This technique immerses the viewer in the character's professional perspective, showing what they're creating or working on.

        7. *Two-Shot*: Involves the character with a mentor, colleague, or someone they're helping in their professional capacity. This shot strengthens the connection during professional learning or teaching moments.

        8. *Dutch Angle (Tilted Angle)*: Use this technique during exciting career moments, breakthrough discoveries, or when the character is overcoming professional challenges. Capture dynamic professional action.

        9. *Frame Within a Frame*: Utilize career-relevant elements like computer screens, microscope views, or architectural structures to frame the subject, adding professional context and depth.

        10. *Leading Lines*: Incorporate professional elements that guide the viewer's eye toward the character's work - such as assembly lines, architectural elements, or laboratory equipment arrangements.

        11. *Rule of Thirds*: Place the character and their professional tools strategically within the grid to create balanced, professional compositions that highlight both the character and their career environment.

        12. *Symmetry and Balance*: Arrange professional elements evenly to create organized, professional compositions that reflect the order and precision of many careers.

        13. *Asymmetry*: Use dynamic arrangements of professional tools and equipment for visual interest while maintaining professional authenticity.

        14. *Foreground, Middleground, and Background*: Layer career-relevant elements at different depths - tools in foreground, character in middleground, professional environment in background.

        15. *Negative Space*: Use clean, professional spacing to emphasize the character and their most important professional tools or achievements.

        ### ENHANCED IMAGE GENERATION SPECIFICATIONS:

        #### THEMATIC ACCURACY REQUIREMENTS:
        - *Career Authenticity*: All professional elements must be accurate to the specified career
        - *Age-Appropriate Tools*: Show simplified, child-friendly versions of professional equipment
        - *Safety Considerations*: Include appropriate safety gear and safe work practices
        - *Inspirational Elements*: Add visual cues that inspire children about the career
        - *Educational Value*: Include elements that teach about the profession

        #### ENVIRONMENTAL AUTHENTICITY:
        - *Professional Settings*: Accurately represent real professional environments
        - *Appropriate Scale*: Size elements appropriately for the character and setting
        - *Realistic Layouts*: Arrange professional spaces logically and authentically
        - *Supporting Details*: Include background elements that support the career theme
        - *Context Clues*: Add visual elements that clearly indicate the professional field

        #### CHARACTER INTERACTION REQUIREMENTS:
        - *Active Engagement*: Show the character actively using professional tools
        - *Competent Handling*: Demonstrate proper use of career-specific equipment
        - *Professional Posture*: Reflect appropriate professional body language
        - *Confident Expression*: Show the character's comfort and skill in their chosen field
        - *Goal-Oriented Action*: Illustrate the character working toward their professional objectives

        ### ARTISTIC STYLE SPECIFICATIONS:

        #### Visual Style Requirements:
        - *Child-Friendly Aesthetic*: Bright, engaging colors that appeal to children
        - *Clear Details*: Sharp, easily recognizable professional elements
        - *Vibrant Colors*: Use a colorful palette that maintains professional authenticity
        - *Smooth Textures*: Clean, polished surfaces appropriate for children's illustrations
        - *Consistent Lighting*: Maintain consistent lighting that enhances the professional environment

        #### Technical Specifications:
        - *High Resolution*: Ensure all professional details are clearly visible
        - *Balanced Composition*: Professional elements should be well-distributed
        - *Appropriate Contrast*: Professional tools should stand out clearly
        - *Color Harmony*: Professional colors should complement the overall palette
        - *Detail Clarity*: Career-specific elements must be easily identifiable

        ### IMAGE PROMPT PROCESSING:
        {prompt}

        ### MANDATORY GENERATION REQUIREMENTS:

        *1. CHARACTER FIDELITY*: The character must exactly match the reference image in all physical characteristics while being placed in the specified professional context.

        *2. THEMATIC INTEGRATION*: Every career-related element mentioned in the prompt must be accurately represented and integrated naturally into the scene.

        *3. PROFESSIONAL AUTHENTICITY*: All career-specific tools, clothing, and environments must be authentic to the profession while being appropriate for children.

        *4. ACTIVE ENGAGEMENT*: The character must be shown actively participating in career-related activities, not just posing with professional props.

        *5. EDUCATIONAL VALUE*: The image should clearly communicate information about the career or goal being pursued.

        *6. INSPIRATIONAL QUALITY*: The image should inspire children to consider the career path and see it as achievable.

        *7. SAFETY CONSCIOUSNESS*: Include appropriate safety measures and equipment where relevant to the profession.

        *8. AGE-APPROPRIATE REPRESENTATION*: Simplify complex professional concepts while maintaining accuracy.

        *Maintain the same artistic style and texture as the reference image provided. Ensure visual characteristics such as color, lighting, and detail match closely, creating a harmonious overall aesthetic.*

        *Focus on capturing natural, career-focused actions of the character, ensuring they appear genuinely engaged in their professional activities. The character should be immersed in their work environment, demonstrating competence and enthusiasm for their chosen career path.*

        ### QUALITY VERIFICATION:
        Before finalizing the image, verify:
        - All specified career elements are present and accurate
        - Character matches reference image exactly
        - Professional environment is authentic and appropriate
        - Character is actively engaged in career-related activities
        - Image inspires and educates about the career path
        - Artistic style is consistent and child-friendly
        - All safety and age-appropriate considerations are met
        """
        print(image_prompt)
        try:
            with open(avatar_path, "rb") as avatar_file:
                result = self.client.images.edit(
                    model="gpt-image-1",
                    image=avatar_file,
                    prompt=image_prompt,
                    size="1024x1024",
                    output_format="jpeg",
                )
                return result.data[0].b64_json, image_prompt
        except Exception as e:
            print(f"Error with image editing: {e}")

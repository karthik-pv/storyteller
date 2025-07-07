import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class OpenAIService:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def generate_story(self, category, subcategory, num_slides):
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

CRITICAL IMAGE REQUIREMENTS:
- The user will upload an avatar image that represents the main character.
- ALL image prompts MUST include the main character from the uploaded avatar in most scenes.
- The main character should be consistently present and recognizable in every scene unless specified otherwise.
- Describe the character's actions, expressions, and interactions in each scene.
- Ensure character consistency across all slides.

### Image Types:
For the images in this story, consider the following types and use them accordingly based on the scene's emotional and narrative focus:

1. **Close-Up**: Focus tightly on the character's face to highlight emotions and details. Use this shot to connect deeply with the character's feelings, such as showing fear, joy, or surprise.

2. **Medium Shot**: Show the character from the waist up. This is ideal for depicting interactions between characters, providing both facial expressions and body language. Use it to create a sense of dialogue or connection during key moments.

3. **Wide Shot (Long Shot)**: Capture the entire character and their surrounding environment. This shot is useful when establishing the setting and context, helping readers understand where the story takes place, especially when introducing new locations or changes in scenery.

4. **Bird's Eye View**: An overhead perspective that makes characters appear small or vulnerable, emphasizing the vastness of their surroundings. This shot can be used to create a sense of wonder or to show the enormity of challenges faced by the characters.

5. **Worm's Eye View**: A low-angle shot looking up at the subject, making them appear larger and more imposing. Use this when a character is experiencing a moment of power or significance, such as facing a towering obstacle.

6. **Over-the-Shoulder Shot**: Taken from behind a character, this shot focuses on what they are looking at. Use it to immerse the reader in the character's perspective, making them feel more involved in the scene.

7. **Two-Shot**: Includes two characters within the frame and is valuable for depicting interactions or relationships. Use it to emphasize the connection between characters during important dialogues or shared experiences.

8. **Dutch Angle (Tilted Angle)**: This technique introduces a diagonal horizon line, creating a sense of unease or tension. Use it during exciting or dynamic moments to heighten suspense or action.

9. **Frame Within a Frame**: Utilize elements within the scene, such as windows or doorways, to frame the subject. This adds depth and focuses attention, creating a more engaging visual narrative.

10. **Leading Lines**: Incorporate compositional lines that guide the viewer's eye toward the main subject. Use this technique to draw attention to important elements in the scene, such as paths leading to the character or significant objects.

11. **Rule of Thirds**: Divide the composition into a 3x3 grid and place key elements along these lines or at their intersections. This creates a balanced image and directs attention to vital aspects of the story.

12. **Symmetry and Balance**: Arrange elements evenly to create a harmonious composition. This style can evoke a sense of order and stability, appealing to a younger audience in calm or soothing scenes.

13. **Asymmetry**: Place elements unevenly for visual interest and dynamic tension. This approach can engage viewers more and encourage exploration of the illustration.

14. **Foreground, Middleground, and Background**: Layer elements at different depths to create a sense of space and dimension. This technique makes the scene more immersive and can add drama or context to interactions.

15. **Negative Space**: Use open space around the subject to highlight it, keeping the composition uncluttered. This helps emphasize the main subject and can create a focused, impactful image.

### Detailed Instructions for Selecting Image Types and Writing Scene Descriptions

1. **Understand the Scene's Purpose**: Determine what the main focus is for the scene. Ask yourself:
    - What emotion do you want to convey? (e.g., happiness, sadness, fear, surprise)
    - What action is the character taking? (e.g., exploring, interacting, feeling, achieving)
    - What is the setting or environment, and how does it relate to the character's experience?

2. **Choosing the Image Type**: Based on the scene's focus, choose the appropriate image type from the list provided and refer to the detailed examples:
   - **Close-Up**: For strong emotions or important reactions.
   - **Medium Shot**: For scenes with dialogue or interaction.
   - **Wide Shot**: For introducing new settings or scenes.
   - **Bird's Eye View**: For dramatic perspectives emphasizing vulnerability.
   - **Worm's Eye View**: For moments of empowerment.
   - **Over-the-Shoulder Shot**: To immerse in the character's perspective.
   - **Two-Shot**: When two characters are interacting.
   - **Dutch Angle**: During moments of action or tension.
   - **Frame Within a Frame**: To create focus using elements in the scene.
   - **Leading Lines**: To guide the viewer's eye to the main subject.
   - **Rule of Thirds**: For a balanced composition.
   - **Symmetry and Balance**: For calm or stable scenes.
   - **Asymmetry**: For dynamic scenes.
   - **Foreground, Middleground, and Background**: For depth and immersion.
   - **Negative Space**: To keep focus on the main subject.

3. **Writing the Scene Description**: Combine the details from the selected image type with the character's actions, expressions, and the setting to create a vivid picture. Be specific about what the viewer will see and feel. Use descriptive adjectives and verbs that evoke emotion or action.

   **Example Scene Description** for a **Wide Shot**:
   "The sun shone brightly over the magical garden as Max ventured in. The colorful flowers swayed gently in the breeze, and butterflies danced around him, creating a joyful atmosphere. Max, with his eyes wide in wonder, stood in the midst of it all, feeling like an explorer in a world of enchantment."

### Example for Structuring in JSON Format
Here's how it looks together in a sample JSON format based on the instructions provided:

```json
{{  
    "story_title": "Max's Magical Garden Adventure",  
    "category": "Adventure",  
    "subcategory": "Fantasy",  
    "slides": [  
        {{  
            "slide_number": 1,  
            "story_text": "Max discovered a secret door in his backyard and stepped into a magical garden full of color and joy. He couldn't help but smile as butterflies fluttered around him.",  
            "image_prompt": "Create a wide shot showing Max in the center of a vibrant garden overflowing with flowers and butterflies, reflecting his sense of wonder."  
        }},  
        {{  
            "slide_number": 2,  
            "story_text": "As he walked through the garden, he met Benny the Rabbit, who wore glasses and looked excited. Welcome to my home! Benny said with a big grin.",  
            "image_prompt": "Create a medium shot of Max and Benny standing close together, showcasing their expressions of excitement and friendship."  
        }}  
    ]  
}}
```

Final Step: Choose the best type for each scene, ensuring that the selected image type enhances the emotional impact and clarity of the story being told. Use the examples and suggestions provided as templates for crafting similarly vivid and effective descriptions for each slide.

IMPORTANT: Your response must be in valid JSON format with the following structure:
{{
    "story_title": "Title of the story",
    "category": "{category}",
    "subcategory": "{subcategory}",
    "slides": [
        {{
            "slide_number": 1,
            "story_text": "The story text for this slide (2-3 sentences)",
            "image_prompt": "Create a fantasy scene showing the exact same character from the reference image, maintaining their precise appearance, clothing, and features, [specific scene description]. Keep the character's identity completely consistent with the reference."
        }}
    ]
}}

Make sure EVERY image prompt:
- Features the main character prominently
- Describes the character's specific actions and expressions
- Maintains character consistency throughout the story
- Includes detailed scene descriptions
- Specifies cartoon/illustration art style suitable for children
- Creates engaging, child-friendly visuals

The main character from the uploaded avatar should be the hero/protagonist of the story and appear in every single image.

Create a complete story with exactly {num_slides} slides.
"""

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

        return json.loads(response_text)

    def generate_image(self, avatar_path, prompt):
        """Generate image using OpenAI DALL-E with image editing"""
        image_prompt = f"""
### Image Types
For the images in this story, consider the following types and use them accordingly based on the scene's emotional and narrative focus. Choose the most appropriate type based on the actions and emotions presented in the scene.

1. **Close-Up**: Focus tightly on the character's face to highlight their emotions and details. This shot connects deeply with the character's feelings—such as fear, joy, or surprise. Capture authentic expressions, ensuring that the character is not directly looking into the camera but immersed in their experience.

2. **Medium Shot**: Show the character from the waist up, which is ideal for depicting interactions. This composition provides both facial expressions and body language, enhancing the dialogue or connection between characters. Maintain a natural pose, as characters engage in conversation or action.

3. **Wide Shot (Long Shot)**: Capture the entire character and their surrounding environment. This shot establishes the setting and context, helping readers understand where the story takes place. Particularly useful when introducing a new location or showing interactions within a broader scene. Ensure the character appears involved in their environment rather than staged.

4. **Bird's Eye View**: An overhead perspective that makes characters seem small or vulnerable, emphasizing the vastness of their surroundings. This shot provides a sense of wonder or highlights the challenges faced by the characters. Aim for a natural feel, showcasing interaction with the environment.

5. **Worm's Eye View**: A low-angle shot looking up at the character, making them appear larger and more imposing. Use this perspective to convey moments of power or significance. Ensure the character exhibits their significance naturally in the scene without posing for the camera.

6. **Over-the-Shoulder Shot**: Taken from behind a character, focusing on what they see. This narrative technique immerses the viewer in the character's perspective, heightening the sense of involvement. Capture candid moments that reflect the character's emotions or reactions to what they observe.

7. **Two-Shot**: Involves two characters within the frame, ideal for showcasing their interactions and relationships. This shot strengthens the connection during dialogue or shared experiences. Ensure the characters are engaged with each other, creating a natural atmosphere.

8. **Dutch Angle (Tilted Angle)**: This technique introduces a diagonal horizon line, injecting a sense of tension or excitement. Use it to heighten suspense during dynamic moments. Capture spontaneous reactions from characters in a non-staged manner.

9. **Frame Within a Frame**: Utilize natural elements, such as trees or doorways, to frame the subject. This adds depth and focuses attention on the character or action, elevating the visual narrative. Aim for a candid composition where the character interacts within the framed element.

10. **Leading Lines**: Incorporate compositional elements that guide the viewer's eye toward the main subject, helping to create a clearer narrative flow. Ensure paths or objects in the scene lead naturally to the character or focal action.

11. **Rule of Thirds**: Divide the composition into a 3x3 grid, placing key elements along these lines or at their intersections. This creates a balanced and aesthetically pleasing image. Maintain a natural focus where the character fits organically into the grid.

12. **Symmetry and Balance**: Arrange elements evenly to create a harmonious and stable composition. This appeals to younger audiences in calm or soothing scenes. Show characters in relaxed poses that complement the symmetrical balance.

13. **Asymmetry**: Use an uneven arrangement of elements for visual intrigue and energy. This approach captivates viewers and invites exploration of the scene. Capture natural interactions that maintain an engaging but balanced asymmetrical feel.

14. **Foreground, Middleground, and Background**: Layer elements at different depths to create a sense of space and dimension. This technique enhances immersion and can add context or drama to interactions. Ensure characters are naturally placed within these layers.

15. **Negative Space**: Utilize open space around the subject to maximize focus and clarity. This tactic prevents clutter in the image and emphasizes the main subject effectively. Encourage a natural look that aligns with the overall narrative flow.

### IMAGE PROMPT:
{prompt}

**Maintain the same artistic style and texture as the reference image provided. Ensure visual characteristics such as color, lighting, and detail match closely, creating a harmonious overall aesthetic.**

**Focus on capturing natural, candid actions of the character, ensuring they appear genuine and true to their personality. Avoid having the character stare directly into the camera; instead, illustrate them engaging with their environment in a spontaneous and relatable manner.**
"""
        try:
            with open(avatar_path, "rb") as avatar_file:
                result = self.client.images.edit(
                    model="gpt-image-1",
                    image=avatar_file,
                    prompt=image_prompt,
                    size="1024x1024",
                    output_format="jpeg",
                )
                return result.data[0].b64_json
        except Exception as e:
            print(f"Error with image editing: {e}")
            # Fallback to regular image generation
            try:
                fallback_prompt = f"Children's book illustration: {prompt}. Cartoon style, colorful, child-friendly, high quality digital art."
                result = self.client.images.generate(
                    model="dall-e-2",
                    prompt=fallback_prompt,
                    size="1024x1024",
                    response_format="b64_json",
                )
                return result.data[0].b64_json
            except Exception as fallback_error:
                print(f"Fallback image generation also failed: {fallback_error}")
                raise fallback_error

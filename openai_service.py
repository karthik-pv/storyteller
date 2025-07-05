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
- Each slide should have 2-3 sentences of story text
- Story should be educational, fun, and inspiring
- Use simple language appropriate for children
- Include positive messages and life lessons
- Make it interactive and engaging

CRITICAL IMAGE REQUIREMENTS:
- The user will upload an avatar image that represents the main character
- ALL image prompts MUST include the main character from the uploaded avatar
- The main character should be consistently present and recognizable in every scene
- Describe the character's actions, expressions, and interactions in each scene
- Ensure character consistency across all slides

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
        """Generate image using OpenAI with exact main.py approach"""
        with open(avatar_path, "rb") as avatar_file:
            result = self.client.images.edit(
                model="gpt-image-1",
                image=avatar_file,
                prompt=prompt,
                size="1024x1024",
                output_format="jpeg",
            )
            return result.data[0].b64_json

import os
import base64
from openai import OpenAI
from PIL import Image
from io import BytesIO

# Load your OpenAI API key from environment variable
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 5 dummy story prompts for a kids' story (reduced from 10 to stay within API limits)
story_prompts = [
    "Create a fantasy scene showing the exact same character from the reference image, maintaining their precise appearance, clothing, and features, waking up in a magical treehouse bedroom with glowing crystals and floating books. Keep the character's identity completely consistent with the reference.",
    "Show the identical character from the reference image, with the same exact appearance, style, and characteristics, having breakfast with friendly forest creatures at an enchanted table with golden plates and sparkling juice. Maintain perfect character consistency with the reference image.",
    "Display the same character from the reference image, preserving their exact look, outfit, and personality, riding a flying dragon to a magical school while waving at fairy friends. Ensure the character looks exactly like the reference in every detail.",
    "Illustrate the exact character from the reference image, keeping their precise appearance, clothing, and features identical, playing magical soccer with unicorns and elves on a rainbow field. Maintain complete visual consistency with the reference character.",
    "Show the same character from the reference image, with identical appearance, style, and characteristics, in a cozy magical cottage getting ready for bed while a friendly wizard reads them a bedtime story. Preserve the character's exact look from the reference image."
]

# Ensure output directory exists
output_dir = "generated_images"
os.makedirs(output_dir, exist_ok=True)

# Generate 5 images, each referencing the avatar
for idx, prompt in enumerate(story_prompts, 1):
    print(f"Generating image {idx}...")
    with open("avatar.jpg", "rb") as avatar_file:
        # Pass the file object directly
        result = client.images.edit(
            model="gpt-image-1",
            image=[avatar_file],
            prompt=prompt,
            size="1024x1024",
            output_format="jpeg"
        )
        # Decode the base64 image
        image_base64 = result.data[0].b64_json
        image_bytes = base64.b64decode(image_base64)
        image = Image.open(BytesIO(image_bytes))
        # Save the image
        out_path = os.path.join(output_dir, f"story_image_{idx}.jpg")
        image.save(out_path, format="JPEG", quality=90)
        print(f"Saved: {out_path}")

print("All 5 images generated successfully!")
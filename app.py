import os
import base64
import shutil
import json
import uuid
import random
from flask import Flask, render_template, request, jsonify
from openai_service import OpenAIService
from categories_service import categories_service
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
openai_service = OpenAIService()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/manual")
def manual():
    return render_template("manual.html")


@app.route("/health")
def health_check():
    return jsonify({"status": "healthy"})


@app.route("/api/categories", methods=["GET"])
def get_categories():
    try:
        categories = categories_service.get_all_categories()
        return jsonify({"success": True, "categories": categories})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/generate-story", methods=["POST"])
def generate_story():
    try:
        data = request.json
        selected_categories = data.get("selected_categories", [])
        num_slides = data.get("num_slides", 5)

        # Filter out empty strings from selected categories
        selected_categories = [cat for cat in selected_categories if cat.strip()]
        print(f"Selected categories: {selected_categories}")

        if selected_categories:
            # Random selection from selected categories
            selected_category = random.choice(selected_categories)

            # Get all available subcategories for the selected category
            all_categories = categories_service.get_all_categories()
            if selected_category not in all_categories:
                return jsonify({"error": f"Invalid category: {selected_category}"}), 400

            available_subcategories = all_categories[selected_category]
            selected_subcategory = random.choice(available_subcategories)

            category = selected_category
            subcategory = selected_subcategory
        else:
            # Completely random selection from all categories
            category, subcategory = (
                categories_service.get_random_category_and_subcategory()
            )

        print(
            f"Using category: {category}, subcategory: {subcategory}, slides: {num_slides}"
        )

        # Generate the story and get the base prompt
        story_data = openai_service.generate_story(category, subcategory, num_slides)

        # Create the base prompt that was sent to GPT
        base_prompt = f"""You are an expert children's story writer. Create an engaging, age-appropriate story for children aged 5-12 years.

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

1. **Close-Up**: Focus tightly on the character's face to highlight emotions and details.
2. **Medium Shot**: Show the character from the waist up. Ideal for depicting interactions.
3. **Wide Shot (Long Shot)**: Capture the entire character and their surrounding environment.
4. **Bird's Eye View**: An overhead perspective that makes characters appear small or vulnerable.
5. **Worm's Eye View**: A low-angle shot looking up at the subject, making them appear larger.
6. **Over-the-Shoulder Shot**: Taken from behind a character, focusing on what they are looking at.
7. **Two-Shot**: Includes two characters within the frame for depicting interactions.
8. **Dutch Angle (Tilted Angle)**: Creates a sense of unease or tension with diagonal horizon.
9. **Frame Within a Frame**: Utilize elements within the scene to frame the subject.
10. **Leading Lines**: Incorporate compositional lines that guide the viewer's eye.
11. **Rule of Thirds**: Divide composition into 3x3 grid for balanced placement.
12. **Symmetry and Balance**: Arrange elements evenly for harmonious composition.
13. **Asymmetry**: Place elements unevenly for visual interest and dynamic tension.
14. **Foreground, Middleground, and Background**: Layer elements at different depths.
15. **Negative Space**: Use open space around the subject to highlight it.

[Additional detailed instructions for selecting image types and writing scene descriptions...]

The main character from the uploaded avatar should be the hero/protagonist of the story and appear in every single image.

Create a complete story with exactly {num_slides} slides."""

        print("Story generated successfully")
        return jsonify(
            {"success": True, "story": story_data, "base_prompt": base_prompt}
        )
    except Exception as e:
        print(f"Error generating story: {str(e)}")
        print(f"Error details: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/generate-story-session", methods=["POST"])
def generate_story_session():
    try:
        avatar_file = request.files.get("avatar")
        story_data_json = request.form.get("story_data")

        if not avatar_file or not story_data_json:
            return jsonify({"error": "Missing avatar or story data"}), 400

        story_data = json.loads(story_data_json)
        session_id = str(uuid.uuid4())
        output_dir = f"static/avatars/{session_id}"
        os.makedirs(output_dir, exist_ok=True)

        avatar_path = os.path.join(output_dir, "avatar.jpg")
        avatar_file.save(avatar_path)

        story_path = os.path.join(output_dir, "story.json")
        with open(story_path, "w") as f:
            json.dump(story_data, f)

        return jsonify(
            {
                "success": True,
                "session_id": session_id,
                "story": story_data,
                "total_slides": len(story_data.get("slides", [])),
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route(
    "/api/generate-story-image/<session_id>/<int:slide_number>", methods=["POST"]
)
def generate_story_image(session_id, slide_number):
    try:
        data = request.json
        image_prompt = data.get("image_prompt")
        story_text = data.get("story_text", "")

        avatar_path = f"static/avatars/{session_id}/avatar.jpg"
        if not os.path.exists(avatar_path):
            return jsonify({"error": "Avatar not found"}), 400

        image_base64 = openai_service.generate_image(avatar_path, image_prompt)

        return jsonify(
            {
                "success": True,
                "image_base64": image_base64,
                "filename": f"story_slide_{slide_number}.jpg",
                "slide_number": slide_number,
                "story_text": story_text,
                "image_prompt": image_prompt,
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/generate-stream", methods=["POST"])
def generate_images_stream():
    try:
        avatar_file = request.files["avatar"]
        if not avatar_file:
            return jsonify({"error": "No avatar file uploaded"}), 400

        prompts = []
        prompt_index = 1
        while prompt_index <= 20:
            prompt = request.form.get(f"prompt_{prompt_index}", "").strip()
            if prompt:
                prompts.append(prompt)
            prompt_index += 1

        if not prompts:
            return jsonify({"error": "No prompts provided"}), 400

        session_id = str(uuid.uuid4())
        output_dir = f"static/avatars/{session_id}"
        os.makedirs(output_dir, exist_ok=True)

        avatar_path = os.path.join(output_dir, "avatar.jpg")
        avatar_file.save(avatar_path)

        return jsonify(
            {
                "session_id": session_id,
                "total_prompts": len(prompts),
                "prompts": prompts,
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/generate-single/<session_id>/<int:idx>", methods=["POST"])
def generate_single_image(session_id, idx):
    try:
        prompt = request.json.get("prompt")
        if not prompt:
            return jsonify({"error": "No prompt provided"}), 400

        avatar_path = f"static/avatars/{session_id}/avatar.jpg"
        if not os.path.exists(avatar_path):
            return jsonify({"error": "Avatar not found"}), 400

        image_base64 = openai_service.generate_image(avatar_path, prompt)

        return jsonify(
            {
                "success": True,
                "image_base64": image_base64,
                "filename": f"story_image_{idx}.jpg",
                "prompt": prompt,
                "index": idx,
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/get-avatar/<session_id>", methods=["GET"])
def get_avatar(session_id):
    try:
        avatar_path = f"static/avatars/{session_id}/avatar.jpg"
        if not os.path.exists(avatar_path):
            return jsonify({"error": "Avatar not found"}), 400

        with open(avatar_path, "rb") as avatar_file:
            avatar_base64 = base64.b64encode(avatar_file.read()).decode("utf-8")

        return jsonify(
            {"success": True, "avatar_base64": avatar_base64, "filename": "avatar.jpg"}
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/cleanup/<session_id>", methods=["POST"])
def cleanup_session(session_id):
    try:
        avatar_dir = f"static/avatars/{session_id}"
        if os.path.exists(avatar_dir):
            shutil.rmtree(avatar_dir)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    os.makedirs("static/avatars", exist_ok=True)
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)

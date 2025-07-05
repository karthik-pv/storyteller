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

        story_data = openai_service.generate_story(category, subcategory, num_slides)
        return jsonify({"success": True, "story": story_data})
    except Exception as e:
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

import os
import base64
import zipfile
import shutil
from flask import Flask, render_template, request, send_file, jsonify
from openai import OpenAI
from PIL import Image
from io import BytesIO
import tempfile
import uuid
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Load your OpenAI API key from environment variable
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate_images():
    try:
        # Get uploaded avatar
        avatar_file = request.files["avatar"]
        if not avatar_file:
            return jsonify({"error": "No avatar file uploaded"}), 400

        # Get prompts from form
        prompts = []
        for i in range(1, 6):
            prompt = request.form.get(f"prompt_{i}", "").strip()
            if prompt:
                prompts.append(prompt)

        if not prompts:
            return jsonify({"error": "No prompts provided"}), 400

        # Create unique session directory
        session_id = str(uuid.uuid4())
        output_dir = f"static/generated/{session_id}"
        os.makedirs(output_dir, exist_ok=True)

        # Store avatar locally first (exactly like main.py approach)
        avatar_path = os.path.join(output_dir, "avatar.jpg")
        avatar_file.save(avatar_path)

        generated_images = []

        # Generate images using the EXACT same logic as main.py
        for idx, prompt in enumerate(prompts, 1):
            print(f"Generating image {idx}...")

            # Open the saved avatar file exactly like main.py does
            with open(avatar_path, "rb") as avatar_file_obj:
                # Pass the file object directly - EXACT same as main.py
                result = client.images.edit(
                    model="gpt-image-1",
                    image=avatar_file_obj,
                    prompt=prompt,
                    size="1024x1024",
                    output_format="jpeg",
                )

                # Decode the base64 image - EXACT same as main.py
                image_base64 = result.data[0].b64_json
                image_bytes = base64.b64decode(image_base64)
                image = Image.open(BytesIO(image_bytes))

                # Save the image - EXACT same as main.py
                filename = f"story_image_{idx}.jpg"
                out_path = os.path.join(output_dir, filename)
                image.save(out_path, format="JPEG", quality=90)

                generated_images.append(
                    {
                        "filename": filename,
                        "path": f"generated/{session_id}/{filename}",
                        "prompt": prompt,
                    }
                )

                print(f"Saved: {out_path}")

        # Add avatar to the generated images list so it's included in zip
        generated_images.append(
            {
                "filename": "avatar.jpg",
                "path": f"generated/{session_id}/avatar.jpg",
                "prompt": "Original avatar image",
            }
        )

        return jsonify(
            {"success": True, "session_id": session_id, "images": generated_images}
        )

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/generate-stream", methods=["POST"])
def generate_images_stream():
    """Generate images one by one and return each as it's completed"""
    try:
        # Get uploaded avatar
        avatar_file = request.files["avatar"]
        if not avatar_file:
            return jsonify({"error": "No avatar file uploaded"}), 400

        # Get prompts from form
        prompts = []
        for i in range(1, 6):
            prompt = request.form.get(f"prompt_{i}", "").strip()
            if prompt:
                prompts.append(prompt)

        if not prompts:
            return jsonify({"error": "No prompts provided"}), 400

        # Create unique session directory
        session_id = str(uuid.uuid4())
        output_dir = f"static/generated/{session_id}"
        os.makedirs(output_dir, exist_ok=True)

        # Store avatar locally first
        avatar_path = os.path.join(output_dir, "avatar.jpg")
        avatar_file.save(avatar_path)

        return jsonify({"session_id": session_id, "total_prompts": len(prompts)})

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/generate-single/<session_id>/<int:idx>", methods=["POST"])
def generate_single_image(session_id, idx):
    """Generate a single image for the given session and index"""
    try:
        prompt = request.json.get("prompt")
        if not prompt:
            return jsonify({"error": "No prompt provided"}), 400

        output_dir = f"static/generated/{session_id}"
        avatar_path = os.path.join(output_dir, "avatar.jpg")

        if not os.path.exists(avatar_path):
            return jsonify({"error": "Avatar not found"}), 400

        print(f"Generating image {idx}...")

        # Open the saved avatar file exactly like main.py does
        with open(avatar_path, "rb") as avatar_file_obj:
            # Pass the file object directly - EXACT same as main.py
            result = client.images.edit(
                model="gpt-image-1",
                image=avatar_file_obj,
                prompt=prompt,
                size="1024x1024",
                output_format="jpeg",
            )

            # Decode the base64 image - EXACT same as main.py
            image_base64 = result.data[0].b64_json
            image_bytes = base64.b64decode(image_base64)
            image = Image.open(BytesIO(image_bytes))

            # Save the image - EXACT same as main.py
            filename = f"story_image_{idx}.jpg"
            out_path = os.path.join(output_dir, filename)
            image.save(out_path, format="JPEG", quality=90)

            print(f"Saved: {out_path}")

            return jsonify(
                {
                    "success": True,
                    "filename": filename,
                    "path": f"generated/{session_id}/{filename}",
                    "prompt": prompt,
                    "index": idx,
                }
            )

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/download/<session_id>")
def download_zip(session_id):
    try:
        # Create zip file
        zip_path = f"static/generated/{session_id}.zip"
        image_dir = f"static/generated/{session_id}"

        # Create zip with all files (including avatar)
        with zipfile.ZipFile(zip_path, "w") as zipf:
            for filename in os.listdir(image_dir):
                if filename.endswith(
                    (".jpg", ".jpeg", ".png")
                ):  # Include all image files
                    file_path = os.path.join(image_dir, filename)
                    zipf.write(file_path, filename)

        # Send the zip file
        response = send_file(
            zip_path, as_attachment=True, download_name=f"story_images_{session_id}.zip"
        )

        # Clean up: Delete the entire session folder and zip file after sending
        def cleanup():
            try:
                # Remove the session directory (contains avatar and generated images)
                if os.path.exists(image_dir):
                    shutil.rmtree(image_dir)
                    print(f"Cleaned up directory: {image_dir}")

                # Remove the zip file
                if os.path.exists(zip_path):
                    os.remove(zip_path)
                    print(f"Cleaned up zip file: {zip_path}")
            except Exception as e:
                print(f"Cleanup error: {str(e)}")

        # Schedule cleanup after response is sent
        response.call_on_close(cleanup)

        return response

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # Ensure directories exist
    os.makedirs("static", exist_ok=True)
    os.makedirs("static/generated", exist_ok=True)
    app.run(debug=True)

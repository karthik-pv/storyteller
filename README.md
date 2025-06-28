# AI Story Image Generator - Flask Web App

A Flask web application that generates story images using OpenAI's API with character consistency.

## Features

- Upload avatar images
- Enter custom story prompts
- Generate story images with character consistency
- View generated images in the browser
- Download all images as a ZIP file

## Setup

1. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

2. Set your OpenAI API key as an environment variable:

   ```
   set OPENAI_API_KEY=your_api_key_here
   ```

   Or add it to your `.env` file.

3. Run the Flask app:

   ```
   python app.py
   ```

4. Open your browser and go to: `http://localhost:5000`

## Usage

1. Upload an avatar image (character reference)
2. Enter up to 5 story prompts in the text areas
3. Click "Generate Story Images"
4. View the generated images on the page
5. Download all images as a ZIP file

## Requirements

- Python 3.7+
- OpenAI API key
- Required packages (see requirements.txt)

## Deployment

This Flask app can be deployed to platforms like Heroku, Railway, or any cloud provider that supports Python web applications.

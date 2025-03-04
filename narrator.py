import os
from openai import OpenAI
import base64
import json
import time
import simpleaudio as sa
import errno
from PIL import Image
from elevenlabs import generate, play, set_api_key, voices
import threading

client = OpenAI()

set_api_key(os.environ.get("ELEVENLABS_API_KEY"))

def encode_image(image_path):
    while True:
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode("utf-8")
        except IOError as e:
            if e.errno != errno.EACCES:
                # Not a "file in use" error, re-raise
                raise
            # File is being written to, wait a bit and retry
            time.sleep(0.1)


def play_audio(text):
    audio = generate(text, voice=os.environ.get("ELEVENLABS_VOICE_ID"))

    print("Audio generated")
    unique_id = base64.urlsafe_b64encode(os.urandom(30)).decode("utf-8").rstrip("=")

    dir_path = os.path.join("narration", unique_id)
    os.makedirs(dir_path, exist_ok=True)
    file_path = os.path.join(dir_path, "audio.wav")

    with open(file_path, "wb") as f:
        f.write(audio)

    #subprocess.run(["python", "play_audio_sub.py", file_path])
    play(audio)


def generate_new_line(base64_image):
    return [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Describe this image"},
                {
                    "type": "image_url",
                    "image_url": f"data:image/jpeg;base64,{base64_image}",
                },
            ],
        },
    ]


def analyze_image(base64_image, script):
    response = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "system",
                "content": """
                You are Sir David Attenborough. Narrate the picture of the human as if it is a nature documentary.
                Make it snarky and funny. Don't repeat yourself. Make it short. If I do anything remotely interesting, make a big deal about it!
                """,
            },
        ]
        + script
        + generate_new_line(base64_image),
        max_tokens=500,
    )
    response_text = response.choices[0].message.content
    return response_text


def main():
    script = []

    while True:
        # path to your image
        image_path = os.path.join(os.getcwd(), "./frames/frame.jpg")

        # getting the base64 encoding
        base64_image = encode_image(image_path)

        # analyze posture
        print("👀 David is watching...")
        print("Analysis started")
        analysis_start = time.time()

        analysis = analyze_image(base64_image, script=script)

        print("Analysis finished ", time.time()-analysis_start)


        print("🎙️ David says:")
        print(analysis)


        #thread = threading.Thread(target=play_audio, args=(analysis,))
        print("Starting audio play for this image")
        if os.path.exists(image_path):
            image = Image.open(image_path)
            image.show()
        #thread.start()
        #play_audio(analysis)

        #script = script + [{"role": "assistant", "content": analysis}]

        play_audio(analysis)
        # wait for 5 seconds
        time.sleep(1)


if __name__ == "__main__":
    main()

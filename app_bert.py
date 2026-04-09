


# # from collections import Counter
# # from pydoc import text
# from flask_cors import CORS
# from flask import Flask, request, jsonify
# from transformers import pipeline
# from pymongo import MongoClient
# from datetime import datetime
# import json
# import random
# import requests
# import whisper
# import os
# import re
# # from datasets import load_dataset
# # dataset = load_dataset("go_emotions")

# app = Flask(__name__)
# CORS(app)

# whisper_model = None

# print("🔥 Starting SoulEase Emotion Server...")
# print("🔥 Loading Pretrained Emotion Model...")

# # -----------------------------
# # Emotion Detection Model
# # -----------------------------
# emotion_pipeline = pipeline(
#     "text-classification",
#     # model="j-hartmann/emotion-english-distilroberta-base"
#     model="SamLowe/roberta-base-go_emotions",
#     return_all_scores=True 
# )

# print("✅ Emotion Model Loaded Successfully!")

# # -----------------------------
# # Whisper Speech Model
# # -----------------------------
# # print("🎤 Loading Whisper Model...")
# # whisper_model = whisper.load_model("base")
# # print("✅ Whisper Model Loaded!")

# # -----------------------------
# # MongoDB Connection
# # -----------------------------
# # client = MongoClient("mongodb://127.0.0.1:27017/")
# client = MongoClient(os.environ.get("MONGO_URI"))
# db = client["soulease"]
# journal_collection = db["journal_entries"]

# # -----------------------------
# # Load Suggestions JSON
# # -----------------------------
# with open("suggestions.json", "r") as f:
#     suggestion_data = json.load(f)

# # -----------------------------
# # Emotion → Strategy Mapping
# # -----------------------------
# emotion_strategy = {
#     "sadness": "uplift",
#     "anger": "calm",
#     "fear": "calm",
#     "joy": "energize",
#     "love": "energize",
#     "surprise": "energize"
# }

# # -----------------------------
# # Jamendo API Setup
# # -----------------------------
# JAMENDO_CLIENT_ID = "4cae87d6"

# emotion_music_tags = {
#     "sadness": "piano",
#     "anger": "ambient",
#     "fear": "calm",
#     "joy": "pop",
#     "love": "acoustic",
#     "surprise": "chill"
# }

# # -----------------------------
# # Podcast Search Terms
# # -----------------------------
# podcast_search_terms = {
#     "sadness": "mental health podcast",
#     "anger": "calming podcast",
#     "fear": "anxiety podcast",
#     "joy": "motivation podcast",
#     "love": "self love podcast",
#     "surprise": "mindfulness podcast"
# }

# # -----------------------------
# # Fetch Dynamic Music
# # -----------------------------
# def fetch_music_from_jamendo(emotion):

#     tag = emotion_music_tags.get(emotion.lower(), "chill")

#     url = f"https://api.jamendo.com/v3.0/tracks/?client_id={JAMENDO_CLIENT_ID}&tags={tag}&limit=3&audioformat=mp32"

#     try:

#         # response = requests.get(url).json()
#         response = requests.get(url, timeout=5).json()

#         music_results = []

#         for track in response.get("results", []):

#             audio_url = track.get("audio")

#             if not audio_url:
#                 continue

#             music_results.append({
#                 "id": str(track.get("id")),
#                 "title": f"{track['name']} - {track['artist_name']}",
#                 "type": "Music",
#                 "category": "Music",
#                 "duration": "3 min",
#                 "color": "bg-slate-50",
#                 "sourceUrl": audio_url
#             })

#         return music_results

#     except Exception as e:

#         print("Jamendo API error:", e)
#         return []


# # -----------------------------
# # Fetch Podcasts
# # -----------------------------
# def fetch_podcasts(emotion):

#     term = podcast_search_terms.get(emotion.lower(), "mindfulness podcast")

#     url = f"https://itunes.apple.com/search?term={term}&media=podcast&limit=3"

#     try:

#         # response = requests.get(url).json()
#         response = requests.get(url, timeout=5).json()

#         podcasts = []

#         for item in response.get("results", []):

#             podcasts.append({
#                 "id": str(item.get("collectionId")),
#                 "title": item.get("collectionName"),
#                 "type": "Podcast",
#                 "category": "Podcast",
#                 "duration": "10 min",
#                 "color": "bg-slate-50",
#                 "sourceUrl": item.get("trackViewUrl")
#             })

#         return podcasts

#     except Exception as e:

#         print("Podcast API error:", e)
#         return []


# # -----------------------------
# # Suggestion Generator
# # -----------------------------
# def get_dynamic_suggestions(emotion):

#     strategy = emotion_strategy.get(emotion.lower(), "uplift")
#     data = suggestion_data.get(strategy, {})

#     results = {}

#     for content_type in data:

#         items = data[content_type]

#         if items:
#             selected = random.sample(items, min(1, len(items)))
#             results[content_type] = selected
#         else:
#             results[content_type] = []

#     results["explore_more"] = {
#         "music": f"https://www.youtube.com/results?search_query={strategy}+music",
#         "exercise": f"https://www.youtube.com/results?search_query={strategy}+exercise",
#         "podcast": f"https://www.youtube.com/results?search_query={strategy}+podcast",
#         "video": f"https://www.youtube.com/results?search_query={strategy}+motivational+video"
#     }

#     return results


# # -----------------------------
# # MAIN PREDICTION ROUTE
# # -----------------------------
# @app.route("/predict", methods=["POST"])
# def predict():

#     data = request.json

#     if not data or "text" not in data:
#         return jsonify({"error": "Text field is required"}), 400

#     text = data["text"]
#     user_id = data.get("userId", "demo_user")

#     try:

#         # sentences = [s.strip() for s in re.split(r'[.!?]| but | however | although ', text.lower()) if s.strip()]
#         sentences = [s.strip() for s in re.split(r'[.!?]| but | however | although ', text.lower()) if s.strip()]

#         if not sentences:
#             sentences = [text.lower()]
        
#         emotion_scores = {}
        
#         for i, sentence in enumerate(sentences):
#             # results = emotion_pipeline(sentence, top_k=None)
#             results = emotion_pipeline(sentence)[0]   # 🔥 FIX
            

#             weight = (i + 1) / len(sentences)

#             for item in results:
#                 emo = item["label"]
#                 score = item["score"] * weight

#                 emotion_scores[emo] = emotion_scores.get(emo, 0) + score

#         # 🔥 sharpen emotional differences
#         for emo in emotion_scores:
#             emotion_scores[emo] = emotion_scores[emo] ** 1.3
#         total = sum(emotion_scores.values())

#         if total == 0:
#             emotion = "neutral"
#             secondary_emotion = None
#             confidence = 0.5
#             sorted_emotions = []
#             intensity = "low"
#         else:
#             for emo in emotion_scores:
#                 emotion_scores[emo] /= total

#             # sorted_emotions = sorted(emotion_scores.items(), key=lambda x: x[1], reverse=True)
#             sorted_emotions = sorted(emotion_scores.items(), key=lambda x: x[1], reverse=True)

#             emotion = sorted_emotions[0][0]
#             confidence = sorted_emotions[0][1]

#             # if sorted_emotions and sorted_emotions[0][0] == "neutral":
#             #     for emo, score in sorted_emotions:
#             #         if emo != "neutral" and score > 0.1:
#             #             emotion = emo
#             #             confidence = score
#             #             break

#             # non_neutral = [e for e in sorted_emotions if e[0] != "neutral"]

#             # if non_neutral:
#             #     top_non_neutral = non_neutral[0]


#             #     if sorted_emotions[0][0] == "neutral" and top_non_neutral[1] > 0.2:
#             #         emotion = top_non_neutral[0]
#             #         confidence = top_non_neutral[1]
            

#             # if sorted_emotions and sorted_emotions[0][0] == "neutral" and len(sorted_emotions) > 1:
#             #     if sorted_emotions[1][1] > 0.15:  
#             #         emotion = sorted_emotions[1][0]
#             #         confidence = sorted_emotions[1][1]
            
#             # ✅ Clean neutral handling (ONLY this logic)
#             top_emotion, top_score = sorted_emotions[0]

#             if top_emotion == "neutral":
#                 for emo, score in sorted_emotions[1:]:
#                     if score > 0.15:   # meaningful emotion
#                         top_emotion = emo
#                         top_score = score
#                         break

#             emotion = top_emotion
#             confidence = top_score
            
#             # ✅ ADD HERE
#             if emotion == "desire":
#                 regret_patterns = ["wish i had", "should have", "could have", "if only", "replaying"]

#                 if any(p in text.lower() for p in regret_patterns):
#                     emotion = "remorse"
            
#             if confidence > 0.75:
#                 intensity = "high"
#             elif confidence > 0.45:
#                 intensity = "medium"
#             else:
#                 intensity = "low"

            
#             # if len(sorted_emotions) > 1:
#             #     second_emotion, second_score = sorted_emotions[1]

#             # # shift only if weak dominance
#             # if confidence < 0.5 and second_score > 0.1:
#             #     emotion = second_emotion
#             #     confidence = second_score
            
#             if len(sorted_emotions) > 1:
#                 second_emotion, second_score = sorted_emotions[1]
            
#             # secondary_emotion = None
            
#             # for emo, score in sorted_emotions[1:]:
#             #     if emo != "neutral" and score > 0.05:
#             #         secondary_emotion = emo
#             #         break
#             secondary_emotion = None

#             # if len(sorted_emotions) > 1:
#             #     second_emotion, second_score = sorted_emotions[1]

#             # if second_emotion != emotion and second_score > 0.15:
#             #         secondary_emotion = second_emotion
#             # secondary_emotion = None

#             for emo, score in sorted_emotions[1:]:
#                 if emo != "neutral" and emo != emotion and score > 0.18:
#                     secondary_emotion = emo
#                     break
                    
#             is_conflicted = False

#             non_neutral = [e for e in sorted_emotions if e[0] != "neutral"]
#             if secondary_emotion and len(non_neutral) > 1:
#                     if abs(non_neutral[0][1] - non_neutral[1][1]) < 0.15:
#                         is_conflicted = True
       
#         dynamic_suggestions = get_dynamic_suggestions(emotion)

#         # Music
#         jamendo_music = fetch_music_from_jamendo(emotion)
#         if jamendo_music:
#             dynamic_suggestions["music"] = jamendo_music

#         # Podcast
#         podcasts = fetch_podcasts(emotion)
#         if podcasts:
#             dynamic_suggestions["podcast"] = podcasts

#         # Save journal
#         journal_collection.insert_one({
#             "userId": user_id,
#             "text": text,
#             "emotion": emotion,
#             "confidence": round(confidence * 100, 2),
#             "timestamp": datetime.utcnow()
#         })

#         # return jsonify({
#         #     "emotion": emotion,
#         #     "confidence": round(confidence * 100, 2),
#         #     "suggestions": dynamic_suggestions
#         # })
#         return jsonify({
#             "emotion": emotion,
#             "secondary_emotion": secondary_emotion,
#             "confidence": round(confidence * 100, 2),
#             "intensity": intensity,
#             "all_emotions": sorted_emotions, 
#             "suggestions": dynamic_suggestions,
#             "is_conflicted": is_conflicted,
#         })

#     except Exception as e:

#         print("Prediction error:", e)

#         return jsonify({
#             "emotion": "neutral",
#             "confidence": 50,
#             "suggestions": {}
#         })

# # -----------------------------
# # SPEECH TO TEXT ROUTE
# # -----------------------------

# @app.route("/speech-to-text", methods=["POST"])
# def speech_to_text():

#     if "audio" not in request.files:
#         return jsonify({"error": "Audio file required"}), 400

#     audio_file = request.files["audio"]
#     temp_path = "temp_audio.wav"
#     audio_file.save(temp_path)

#     try:
#         global whisper_model

#         if whisper_model is None:
#             whisper_model = whisper.load_model("tiny")

#         result = whisper_model.transcribe(temp_path)

#         text = result["text"].strip()

#         os.remove(temp_path)

#         return jsonify({
#             "text": text
#         })

#     except Exception as e:
#         print("Whisper error:", e)

#         if os.path.exists(temp_path):
#             os.remove(temp_path)

#         return jsonify({
#             "text": ""
#         })
        
# @app.route("/")
# def home():
#     return "AI Server Running 🚀"

# if __name__ == "__main__":

#     print("🚀 SoulEase Emotion Server Running...")

#     app.run(
#         host="0.0.0.0",
#         # port=5001,
#         port=int(os.environ.get("PORT", 5001)),
#         debug=True,
#         use_reloader=False
#     )
    



from flask_cors import CORS
from flask import Flask, request, jsonify
from transformers import pipeline
from pymongo import MongoClient
from datetime import datetime
import json
import random
import requests
import os
import re

app = Flask(__name__)
CORS(app)

print("🔥 Starting SoulEase Emotion Server...")

# -----------------------------
# Lazy Load Model (IMPORTANT FIX)
# -----------------------------
emotion_pipeline = None

# -----------------------------
# MongoDB Connection
# -----------------------------
client = MongoClient(os.environ.get("MONGO_URI"))
db = client["soulease"]
journal_collection = db["journal_entries"]

# -----------------------------
# Load Suggestions JSON
# -----------------------------
with open("suggestions.json", "r") as f:
    suggestion_data = json.load(f)

# -----------------------------
# Emotion → Strategy Mapping
# -----------------------------
emotion_strategy = {
    "sadness": "uplift",
    "anger": "calm",
    "fear": "calm",
    "joy": "energize",
    "love": "energize",
    "surprise": "energize"
}

# -----------------------------
# Jamendo API Setup
# -----------------------------
JAMENDO_CLIENT_ID = "4cae87d6"

emotion_music_tags = {
    "sadness": "piano",
    "anger": "ambient",
    "fear": "calm",
    "joy": "pop",
    "love": "acoustic",
    "surprise": "chill"
}

# -----------------------------
# Podcast Search Terms
# -----------------------------
podcast_search_terms = {
    "sadness": "mental health podcast",
    "anger": "calming podcast",
    "fear": "anxiety podcast",
    "joy": "motivation podcast",
    "love": "self love podcast",
    "surprise": "mindfulness podcast"
}

# -----------------------------
# Fetch Music
# -----------------------------
def fetch_music_from_jamendo(emotion):
    tag = emotion_music_tags.get(emotion.lower(), "chill")
    url = f"https://api.jamendo.com/v3.0/tracks/?client_id={JAMENDO_CLIENT_ID}&tags={tag}&limit=3&audioformat=mp32"

    try:
        response = requests.get(url, timeout=5).json()
        music_results = []

        for track in response.get("results", []):
            audio_url = track.get("audio")
            if not audio_url:
                continue

            music_results.append({
                "id": str(track.get("id")),
                "title": f"{track['name']} - {track['artist_name']}",
                "type": "Music",
                "category": "Music",
                "duration": "3 min",
                "color": "bg-slate-50",
                "sourceUrl": audio_url
            })

        return music_results

    except Exception as e:
        print("Jamendo API error:", e)
        return []

# -----------------------------
# Fetch Podcasts
# -----------------------------
def fetch_podcasts(emotion):
    term = podcast_search_terms.get(emotion.lower(), "mindfulness podcast")
    url = f"https://itunes.apple.com/search?term={term}&media=podcast&limit=3"

    try:
        response = requests.get(url, timeout=5).json()
        podcasts = []

        for item in response.get("results", []):
            podcasts.append({
                "id": str(item.get("collectionId")),
                "title": item.get("collectionName"),
                "type": "Podcast",
                "category": "Podcast",
                "duration": "10 min",
                "color": "bg-slate-50",
                "sourceUrl": item.get("trackViewUrl")
            })

        return podcasts

    except Exception as e:
        print("Podcast API error:", e)
        return []

# -----------------------------
# Suggestions
# -----------------------------
def get_dynamic_suggestions(emotion):
    strategy = emotion_strategy.get(emotion.lower(), "uplift")
    data = suggestion_data.get(strategy, {})

    results = {}

    for content_type in data:
        items = data[content_type]
        if items:
            results[content_type] = random.sample(items, 1)
        else:
            results[content_type] = []

    results["explore_more"] = {
        "music": f"https://www.youtube.com/results?search_query={strategy}+music",
        "exercise": f"https://www.youtube.com/results?search_query={strategy}+exercise",
        "podcast": f"https://www.youtube.com/results?search_query={strategy}+podcast",
        "video": f"https://www.youtube.com/results?search_query={strategy}+motivational+video"
    }

    return results

# -----------------------------
# MAIN ROUTE
# -----------------------------
@app.route("/predict", methods=["POST"])
def predict():

    global emotion_pipeline

    # 🔥 Lazy load model
    if emotion_pipeline is None:
        print("🔥 Loading Emotion Model...")
        emotion_pipeline = pipeline(
            "text-classification",
            model="SamLowe/roberta-base-go_emotions",
            device=-1
        )
        print("✅ Model Loaded!")

    data = request.json

    if not data or "text" not in data:
        return jsonify({"error": "Text field is required"}), 400

    text = data["text"]
    user_id = data.get("userId", "demo_user")

    try:
        sentences = [s.strip() for s in re.split(r'[.!?]| but | however | although ', text.lower()) if s.strip()]
        if not sentences:
            sentences = [text.lower()]

        emotion_scores = {}

        for i, sentence in enumerate(sentences):
            results = emotion_pipeline(sentence)[0]
            weight = (i + 1) / len(sentences)

            for item in results:
                emo = item["label"]
                score = item["score"] * weight
                emotion_scores[emo] = emotion_scores.get(emo, 0) + score

        for emo in emotion_scores:
            emotion_scores[emo] = emotion_scores[emo] ** 1.3

        total = sum(emotion_scores.values())

        if total == 0:
            emotion = "neutral"
            confidence = 0.5
            sorted_emotions = []
        else:
            for emo in emotion_scores:
                emotion_scores[emo] /= total

            sorted_emotions = sorted(emotion_scores.items(), key=lambda x: x[1], reverse=True)

            emotion = sorted_emotions[0][0]
            confidence = sorted_emotions[0][1]

        dynamic_suggestions = get_dynamic_suggestions(emotion)

        journal_collection.insert_one({
            "userId": user_id,
            "text": text,
            "emotion": emotion,
            "confidence": round(confidence * 100, 2),
            "timestamp": datetime.utcnow()
        })

        return jsonify({
            "emotion": emotion,
            "confidence": round(confidence * 100, 2),
            "suggestions": dynamic_suggestions
        })

    except Exception as e:
        print("Prediction error:", e)
        return jsonify({
            "emotion": "neutral",
            "confidence": 50,
            "suggestions": {}
        })

@app.route("/")
def home():
    return "AI Server Running 🚀"

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5001)),
        debug=True,
        use_reloader=False
    )

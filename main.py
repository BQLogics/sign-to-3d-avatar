from flask import Flask, render_template, request
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import nltk
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

@app.route('/')
def home():
    return render_template('animation.html')

@app.route('/animation', methods=['GET', 'POST'])
def animation_view():
    if request.method == 'POST':
        text = request.form.get('sen')
        text = text.lower()  # Ensure text is lowercase
        words = word_tokenize(text)  # Tokenizing the sentence

        tagged = nltk.pos_tag(words)
        tense = {
            "future": len([word for word in tagged if word[1] == "MD"]),
            "present": len([word for word in tagged if word[1] in ["VBP", "VBZ", "VBG"]]),
            "past": len([word for word in tagged if word[1] in ["VBD", "VBN"]]),
            "present_continuous": len([word for word in tagged if word[1] == "VBG"])
        }

        # Define stop words
        stop_words = set(["mightn't", 're', 'wasn', 'wouldn', 'be', 'has', 'that', 'does', 'shouldn', 
                          'do', "you've", 'off', 'for', "didn't", 'm', 'ain', 'haven', "weren't", 
                          'are', "she's", "wasn't", 'its', "haven't", "wouldn't", 'don', 'weren', 
                          's', "you'd", "don't", 'doesn', "hadn't", 'is', 'was', "that'll", 
                          "should've", 'a', 'then', 'the', 'mustn', 'nor', 'as', "it's", 
                          "needn't", 'd', 'have', 'hasn', 'o', "aren't", "you'll", 
                          "couldn't", "you're", "mustn't", 'didn', "doesn't", 'll', 'an', 
                          'hadn', 'whom', 'y', "hasn't", 'itself', 'couldn', 'needn', 
                          "shan't", 'isn', 'been', 'such', 'shan', "shouldn't", 'aren', 
                          'being', 'were', 'did', 'ma', 't', 'having', 'mightn', 've', 
                          "isn't", "won't"])

        # Removing stopwords and applying lemmatization
        lr = WordNetLemmatizer()
        filtered_text = []
        for w, p in zip(words, tagged):
            if w not in stop_words:
                if p[1] in ['VBG', 'VBD', 'VBZ', 'VBN', 'NN']:
                    filtered_text.append(lr.lemmatize(w, pos='v'))
                elif p[1] in ['JJ', 'JJR', 'JJS', 'RBR', 'RBS']:
                    filtered_text.append(lr.lemmatize(w, pos='a'))
                else:
                    filtered_text.append(lr.lemmatize(w))

        # Process tense and words
        words = filtered_text
        temp = []
        for w in words:
            if w == 'I':
                temp.append('Me')
            else:
                temp.append(w)
        words = temp
        probable_tense = max(tense, key=tense.get)

        if probable_tense == "past" and tense["past"] >= 1:
            temp = ["Before"]
            temp += words
            words = temp
        elif probable_tense == "future" and tense["future"] >= 1:
            if "Will" not in words:
                temp = ["Will"]
                temp += words
                words = temp
        elif probable_tense == "present":
            if tense["present_continuous"] >= 1:
                temp = ["Now"]
                temp += words
                words = temp

        # Find animation videos or split words into characters if video not found
        animation_videos = []
        for w in words:
            word_video_path = f"static/{w.capitalize()}.mp4"
            if os.path.isfile(word_video_path):  # If video for the whole word exists
                animation_videos.append(w.capitalize())  # Add the video for the whole word
            else:
                # Split into individual letters if no video for the entire word exists
                for char in w:
                    char_video_path = f"static/{char.upper()}.mp4"
                    if os.path.isfile(char_video_path):
                        animation_videos.append(char.upper())  # Add the video for each letter
                    else:
                        continue  # Skip if the video for the character is not found

        return render_template('animation.html', words=animation_videos, text=text)
    else:
        return render_template('animation.html')

if __name__ == "__main__":
    app.run(debug=True)

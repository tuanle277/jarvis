import pyttsx3
import pyaudio
import wave
import speech_recognition  as sr

class TalkModule:
    def __init__(self):
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 150)  # Speed of speech
        self.tts_engine.setProperty('volume', 1)  # Volume level (0.0 to 1.0)
        
        # Set a more natural voice
        voices = self.tts_engine.getProperty('voices')
        self.tts_engine.setProperty('voice', voices[1].id)  # Typically, voices[1] is a female voice

    def play_sound(self, file_name):
        """Plays a sound file (WAV) if it exists."""
        try:
            chunk = 1024
            wf = wave.open(file_name, 'rb')
            p = pyaudio.PyAudio()

            stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                            channels=wf.getnchannels(),
                            rate=wf.getframerate(),
                            output=True)

            data = wf.readframes(chunk)

            while data:
                stream.write(data)
                data = wf.readframes(chunk)

            stream.stop_stream()
            stream.close()
            p.terminate()
        except FileNotFoundError:
            print(f"Sound file not found: {file_name}")

    def speak(self, text):
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()

    def record_audio(self, file_name, duration=5):
        """Records audio from the microphone and saves it to a file."""
        chunk = 1024  # Record in chunks of 1024 samples
        sample_format = pyaudio.paInt16  # 16 bits per sample
        channels = 1
        fs = 44100  # Record at 44100 samples per second

        p = pyaudio.PyAudio()  # Create an interface to PortAudio

        print('Listening...')

        stream = p.open(format=sample_format,
                        channels=channels,
                        rate=fs,
                        frames_per_buffer=chunk,
                        input=True)

        frames = []  # Initialize array to store frames

        # Store data in chunks for the specified duration
        for _ in range(0, int(fs / chunk * duration)):
            data = stream.read(chunk)
            frames.append(data)

        # Stop and close the stream
        stream.stop_stream()
        stream.close()
        p.terminate()

        # Save the recorded data as a WAV file
        wf = wave.open(file_name, 'wb')
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(sample_format))
        wf.setframerate(fs)
        wf.writeframes(b''.join(frames))
        wf.close()

    def audio_to_text(self, file_name):
        """Converts recorded audio to text using SpeechRecognition library."""
        recognizer = sr.Recognizer()
        with sr.AudioFile(file_name) as source:
            audio_data = recognizer.record(source)
            try:
                text = recognizer.recognize_google(audio_data)
                print(f"Recognized text: {text}")
                return text
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio")
                return "Sorry, I could not understand the audio."
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service; {e}")
                return "Sorry, I could not request results from the speech recognition service."

    def listen_for_keywords(self, keywords):
        """Continuously listens for audio and checks if any keywords are said."""
        recognizer = sr.Recognizer()
        mic = sr.Microphone()

        while True:
            print("Listening for keywords...")
            with mic as source:
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source)

            try:
                text = recognizer.recognize_google(audio)
                print(f"Recognized text: {text}")
                if any(keyword in text.lower() for keyword in keywords):
                    print("Keyword detected, stopping listening.")
                    return text, True
                return text, False
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio")
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service; {e}")
                return "Sorry, I could not request results from the speech recognition service.", False
# Example usage:
if __name__ == "__main__":
    speak_module = TalkModule()
    speak_module.speak("Hello, this is a test.")
    # speak_module.record_audio("test_recording.wav")
    # speak_module.play_sound("test_recording.wav")

# import boto3
# import os
# import pyaudio
# import wave

# class SpeakModule:
#     def __init__(self, aws_access_key_id, aws_secret_access_key, region_name):
#         self.polly = boto3.client(
#             'polly',
#             aws_access_key_id=aws_access_key_id,
#             aws_secret_access_key=aws_secret_access_key,
#             region_name=region_name
#         )

#     def play_sound(self, file_name):
#         """Plays a sound file (WAV) if it exists."""
#         try:
#             chunk = 1024
#             wf = wave.open(file_name, 'rb')
#             p = pyaudio.PyAudio()

#             stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
#                             channels=wf.getnchannels(),
#                             rate=wf.getframerate(),
#                             output=True)

#             data = wf.readframes(chunk)

#             while data:
#                 stream.write(data)
#                 data = wf.readframes(chunk)

#             stream.stop_stream()
#             stream.close()
#             p.terminate()
#         except FileNotFoundError:
#             print(f"Sound file not found: {file_name}")

#     def speak(self, text):
#         response = self.polly.synthesize_speech(
#             Text=text,
#             OutputFormat='mp3',
#             VoiceId='Joanna'  # NTTS voice for more natural sound
#         )

#         audio_stream = response['AudioStream']

#         with open("response.mp3", "wb") as file:
#             file.write(audio_stream.read())

#         os.system("mpg321 response.mp3")

#     def record_audio(self, file_name, duration=5):
#         """Records audio from the microphone and saves it to a file."""
#         chunk = 1024  # Record in chunks of 1024 samples
#         sample_format = pyaudio.paInt16  # 16 bits per sample
#         channels = 1
#         fs = 44100  # Record at 44100 samples per second

#         p = pyaudio.PyAudio()  # Create an interface to PortAudio

#         print('Recording')

#         stream = p.open(format=sample_format,
#                         channels=channels,
#                         rate=fs,
#                         frames_per_buffer=chunk,
#                         input=True)

#         frames = []  # Initialize array to store frames

#         # Store data in chunks for the specified duration
#         for _ in range(0, int(fs / chunk * duration)):
#             data = stream.read(chunk)
#             frames.append(data)

#         # Stop and close the stream
#         stream.stop_stream()
#         stream.close()
#         p.terminate()

#         print('Finished recording')

#         # Save the recorded data as a WAV file
#         wf = wave.open(file_name, 'wb')
#         wf.setnchannels(channels)
#         wf.setsampwidth(p.get_sample_size(sample_format))
#         wf.setframerate(fs)
#         wf.writeframes(b''.join(frames))
#         wf.close()

# # Example usage:
# speak_module = SpeakModule(
#     aws_access_key_id='your_access_key_id',
#     aws_secret_access_key='your_secret_access_key',
#     region_name='us-west-2'  # e.g., 'us-west-2'
# )
# speak_module.speak("Hello, this is a test.")
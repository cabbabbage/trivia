import os
import requests
import time
import random
import speech_recognition as sr
import re
import openai  # Official OpenAI library
from PyQt5.QtCore import QTimer
from openai import OpenAI
import json
from pydub import AudioSegment
from pydub.playback import play
import io
import base64
from playsound import playsound
import pygame

# Set your OpenAI API key. Alternatively, you can set the OPENAI_API_KEY
# environment variable before running this script.

class Character:
    def __init__(self, prompt):
        self.prompt = prompt
        self.question = ""
        self.correct_answer = ""
        self.player_answer = ""
        self.user_text = ""
        with open("key.txt", "r") as file:
            self.api_key = file.readline().strip()



    def fetch_trivia_question(self):
        """Fetch a trivia question from the API and set the question and answers."""
        try:
            response = requests.get("https://opentdb.com/api.php?amount=1&type=multiple")
            data = response.json()
            question_data = data['results'][0]
            self.question = question_data['question']
            self.correct_answer = question_data['correct_answer']
            incorrect_answers = question_data['incorrect_answers']
            all_answers = incorrect_answers + [self.correct_answer]
            random.shuffle(all_answers)
            system_prompt = (
                f"You are a game host with the personality: {self.prompt}. "
                "You are a game show host with a unique personality. Your task is to clearly read the question and all answer options in an engaging way. Ensure each answer option is presented fairly and clearly, without giving away any hints about the correct answer. After reading the options, you may add a brief comment that aligns with your personality to keep the energy engaging. Do not reveal or imply which option is correct. Short and sweet though."

            )
            # Store the answers for later use
            self.answers = all_answers
            response = self.generate_gpt_response(
                system_prompt,
                f"Question: {self.question}\nAnswer options: {', '.join(self.answers)}"
            )

        except Exception as e:
            print(f"Error fetching trivia question: {e}")
            # Wait 2 seconds, then try again
            QTimer.singleShot(2000, self.fetch_trivia_question)

    def get_question_and_answers(self):
        """Return the current question and shuffled answers as a tuple."""
        return self.question, self.answers

    def ask_question(self):

        """Ask the question, wait for a response, and react accordingly."""
        # Generate the question introduction using GPT


        self.voice_read()


        # Listen for the player's answer
        self.player_answer = self.listen()

        # Evaluate the player's answer
        if self.player_answer:
            if self.evaluate_answer(self.player_answer):
                self.gpt_respond_correct()
            else:
                self.gpt_respond_incorrect()

    def generate_gpt_response(self, system_prompt, user_message):
        """Generate a GPT response with audio output."""
        try:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            payload = {
                "model": "gpt-4o-audio-preview",
                "modalities": ["text", "audio"],
                "audio": {"voice": "alloy", "format": "wav"},
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ]
            }

            response = requests.post(url, headers=headers, data=json.dumps(payload))

            if response.status_code != 200:
                raise Exception(f"API request failed with status code {response.status_code}: {response.text}")

            response_data = response.json()

            # Extract text response
            gpt_response_text = "yup"

            # Extract and decode audio response
            audio_data = response_data.get("choices", [{}])[0].get("message", {}).get("audio", {}).get("data")
            if audio_data:
                try:
                    # Delete existing response.wav if it exists
                    if os.path.exists("response.wav"):
                        os.remove("response.wav")

                    # Write the new audio file
                    wav_bytes = base64.b64decode(audio_data)
                    with open("response.wav", "wb") as audio_file:
                        audio_file.write(wav_bytes)
                except Exception as e:
                    print(f"Error handling response.wav: {e}")

            return gpt_response_text

        except Exception as e:
            print(f"OpenAI API error: {e}")
            return "Oops! Something went wrong with the GPT request."


    def gpt_respond_introduction(self):
        """The character introduces itself and announces the game start."""
        system_prompt = (
            f"You are a game host with the personality: {self.prompt}. "
            "Introduce yourself in character. Short Intro. 2 sentences."
        )
        user_message = (
            "Introduce yourself as the game host. "
            "Explain the rules briefly and announce that the game has started. "
            "Let the player know the first question will appear shortly."
        )
        self.generate_gpt_response(system_prompt, user_message)
        self.voice_read()

    def gpt_respond_correct(self):
        """Generate a response for a correct answer."""
        system_prompt = (
            f"You are a game show host with the personality: {self.prompt}. "
            "Respond to a player answering correctly."
        )
        user_message = f"The player answered: {self.correct_answer}. Correct."
        response = self.generate_gpt_response(system_prompt, user_message)
        self.voice_read()

    def gpt_respond_incorrect(self):
        """
        Generate a response for an incorrect answer.
        Provide instructions to compare the player's answer carefully,
        in case it might be a voice-to-text error or a spelling difference.
        """
        system_prompt = (
            f"You are a game show host with the personality: {self.prompt}. "
            "Respond to a player who has answered incorrectly. "
            "Consider if the player's answer might have been a voice recognition error. "
            "Show empathy, sarcasm, hostility, as per the personality, and reveal the correct answer."
        )
        user_message = (
            f"The player answered: {self.player_answer}. Incorrect. "
            f"The correct answer was {self.correct_answer}."
        )
        response = self.generate_gpt_response(system_prompt, user_message)
        self.voice_read()

    def gpt_respond_mock(self):
        """Generate a response for taking too long to answer."""
        system_prompt = (
            f"You are a game show host with the personality: {self.prompt}. "
            "Respond to a player taking too long to answer in a very rude, teasing or humorous way."
        )
        response = self.generate_gpt_response(system_prompt, "The player is taking too long to answer.")
        self.voice_read()

    def voice_read(self):
        pygame.mixer.init()
        pygame.mixer.music.load("response.wav")
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        pygame.mixer.music.stop()
        pygame.mixer.quit()
        os.remove("response.wav")

    def listen(self):
        recognizer = sr.Recognizer()
        mic = sr.Microphone()
        print("Listening for the player's answer... (say 'final answer <your guess>')")

        # Set the initial timeout to a random value between 20 and 40 seconds
        next_mock_time = time.time() + random.randint(20, 40)

        while True:
            # Check if it's time to call the mock response
            if time.time() >= next_mock_time:
                self.gpt_respond_mock()  # Call the mocking response
                # Reset the timer to a new random interval
                next_mock_time = time.time() + random.randint(20, 40)

            with mic as source:
                recognizer.adjust_for_ambient_noise(source)
                try:
                    audio = recognizer.listen(source)
                    user_text = recognizer.recognize_google(audio)
                    self.user_text += ' ' + user_text

                    if self.find_answer():
                        return self.player_answer
                except sr.UnknownValueError:
                    print("Could not understand the audio. Please try again.")
                except sr.RequestError as e:
                    print(f"Error with speech recognition service: {e}")
        return self.player_answer
    
    def answer_click(self, answer):
        self.player_answer = answer



    def find_answer(self):
        """
        Looks for the pattern 'final answer <some text>' in self.user_text.
        If found, store that as self.player_answer and clear the buffer.
        If no match is found, checks if answer.txt is not empty and processes it.
        """
        # Check for 'final answer' in voice chat
        match = re.search(r"final answer\s+(.+)", self.user_text.lower())
        if match:
            print("Answer recorded from voice chat")
            self.player_chat = self.user_text[:match.start()].strip()
            self.player_answer = match.group(1).strip()
            self.gpt_learn_player()
            self.user_text = ""
            return True

        # Check if answer.txt is not empty
        elif os.path.exists("answer.txt") and os.path.getsize("answer.txt") > 0:
            with open("answer.txt", "r") as file:
                answer = file.readline().strip()
                if answer:
                    print("Answer recorded from answer.txt")
                    self.player_answer = answer
                    self.gpt_learn_player()
                    self.user_text = ""

                    # Clear the file
                    open("answer.txt", "w").close()
                    return True

        # No answer found
        return False


    def evaluate_answer(self, player_answer):
        """Basic evaluation: case-insensitive exact match with self.correct_answer."""
        return player_answer.strip().lower() == self.correct_answer.lower()

    def gpt_learn_player(self):
        """
        Updates the "game show host" with player's preceding talk
        so future GPT responses can reflect the player's style or background.
        """
        if not getattr(self, 'player_chat', '').strip():
            return
        system_prompt = (
            f"You are a game show host with the personality: {self.prompt}. "
            f"This is what the player has been talking about: \"{self.player_chat}\". "
            "Use this context to better understand the player and make your "
            "future responses more relevant and personalized."
        )
        self.generate_gpt_response(system_prompt, "")
        self.player_chat = ""


# Example usage: run this script directly to see it in action
if __name__ == "__main__":
    host = Character("a sarcastic, witty British quizmaster")
    host.gpt_respond_introduction()  # Introduce the host and the game
    host.fetch_trivia_question()     # Fetch a trivia question
    # The ask_question loop or logic can be invoked as needed,
    # e.g.:
    host.ask_question()

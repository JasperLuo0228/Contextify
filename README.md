# Contextify
Turning Conversations into Clarity
## Overview
Contextify is a real-time context extraction and definition application designed to enhance your understanding during meetings or presentations. By leveraging speech-to-text and natural language processing (NLP), Contextify identifies key terms, abbreviations, people, events, and technical terms from live voice input. It then provides concise and accurate definitions or explanations, ensuring you stay informed without missing critical details.

This tool is ideal for professionals, students, and anyone seeking clarity in fast-paced or highly technical environments.
## Get Started 
1. Clone the Github Repository
   （git clone https://github.com/JasperLuo0228/Contextify.git）
2. Install Dependencies (see requirements.txt)
   （`pip install -r requirements.txt`）
3. Set up API keys
   （`API_KEY_GOOGLE=your_google_api_key` `API_KEY_WIKIPEDIA=your_wikipedia_api_key`）
4. Run the application
   python app.py
## Inspiration
During meetings or professional conversations, we often encounter technical terms, unfamiliar courses, or references from fields outside our expertise. This can make it challenging to stay focused and fully grasp the ongoing discussion. Additionally, staying updated on global events or news while managing these conversations can be overwhelming. This inspired us to develop Contextify, an app that provides real-time information and context while others introduce new topics. By delivering insights simultaneously, it helps users quickly capture and understand knowledge, making conversations more productive and engaging.
## What it does
Contextify is an AI-powered tool that transcribes speech into text using OpenAI’s Whisper and enriches it with insights via GPT-4o. It identifies key entities like names, companies, and technical terms while integrating the Bing News API to provide real-time relevant updates. Contextify turns conversations into actionable insights, enhancing comprehension and saving time in meetings, research, and multilingual environments.
## How we built
The frontend of Contextify was developed as a macOS app using **SwiftUI**, providing a modern and intuitive user interface.

The backend, built with **FastAPI** and Python, integrates advanced tools like **Whisper** for real-time transcription, **GPT-4o** for contextual entity extraction, and the **Wikipedia API** for instant summaries. Additionally, we incorporated **Bing News API** for real-time updates and graph libraries for data visualization. 
## What's next for Contextify
Moving forward, Contextify aims to further enhance the accuracy of voice recognition technology and refine course-related information, such as credits (Units), to deliver a more seamless and efficient query experience for students. At the same time, Contextify remains dedicated to addressing critical communication challenges in hybrid and remote work environments. By resolving misunderstandings caused by specialized jargon and technical terms, Contextify will integrate cutting-edge features to identify and interpret workplace terminology in real time. These advancements will solidify Contextify’s role as a vital tool for bridging communication gaps, boosting productivity, and fostering a more connected and effective workplace.
## Contributing
We welcome contributions to make Contextify even better. If you have suggestions or want to contribute, please follow these steps:

1. Fork the repository.
2. Make a new branch (`git checkout -b feature-branch`).
3. Make your changes and commit (`git commit -am 'Add some feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Create a new Pull Request.

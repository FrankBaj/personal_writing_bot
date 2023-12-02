# personal_writing_bot
Built a basic bot capable of giving writing advice. I got tired of having to log into my OpenAI account every time, plus I thought it would be a fun project that would give me an opportunity to learn how to build a basic bot.

## Features
- Text-to-Speech Functionality
- Speech-to-Text Functionality
- Export conversations into a .txt file

## Summary
The bot uses the OpenAI API to communicate with the user and generate responses. It also connects to the Azure AI Services API
to perform Speech-to-Text functionality in its replies. And the "speechrecognition" library is used to perform basic speech-to-text
for user input. UI was created using Customtkinter library.

If anyone reading this is interested in using it, just replace the API keys with your own generated API keys.

AZURE AI Services Setup: https://learn.microsoft.com/en-us/azure/ai-services/speech-service/get-started-text-to-speech?tabs=windows%2Cterminal&pivots=programming-language-python


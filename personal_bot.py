import customtkinter
import openai
import os
from threading import Timer
from openai import OpenAI
import datetime
import pyttsx3
import azure.cognitiveservices.speech as speechsdk
import speech_recognition as sr
import threading
import winsound

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")

## Create GUI interface
class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        ## Default TTS Voice
        engine = pyttsx3.init()
        voices = engine.getProperty("voices")
        engine.setProperty("rate", 130)
        engine.setProperty("voice", voices[1].id)

        ## Microsoft Azure TTS Voice
        speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('YOUR_AZURE_SPEECH_KEY'), region=os.environ.get('YOUR_AZURE_SPEECH_REGION'))
        audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
        speech_config.speech_synthesis_voice_name='en-CA-LiamNeural'
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

        # Initialize Speech Recognizer
        r = sr.Recognizer()

        client = OpenAI(
            api_key = os.environ.get('YOUR_OPEN_AI_KEY'),
        )
        message_list = []
        message_list.append(
                {
                'role':'system',
                'content': 'You are a personal assitant for writers. You provide suggestions, feedback, and guidance throughout the writing process. You help users generate ideas, improve sentence structure, correct grammar and spelling errors, suggest synonyms or alternative phrases, offer feedback on clarity and coherence, and provide general writing tips and advice. You learn from user interactions, adapt to individual preferences, and offer personalized recommendations. You also provide encouragement to writers struggling with motivation and productivity.'
                })

        ## When button is pressed, user input is saved and displayed in the text field
        def user_input(event):
            ## Take old input, and put it above the new input
            self.textbox.configure(state='normal') #Set textbox to be editable
            
            input_string = self.inputbox.get('1.0','end')
            # Change text color of User response
            self.textbox.insert("end", "User: " + input_string + "\n\n", tags='user')
            self.textbox.tag_config('user', foreground='#719CFF')
            self.textbox.tag_remove('user', 'end')
            # Autoscroll to bottom of textbox
            self.textbox.see('end')

            #Add user input to messages
            message_list.append({'role':'user', 'content': input_string})

            self.textbox.configure(state='disabled') #Set textbox to be uneditable
            
            self.inputbox.delete('0.0', 'end') # Clear Entry Field of text
            t = Timer(1, bot_response) # Wait 1 second before calling bot_response
            t.start()

        def bot_response():
            self.textbox.configure(state='normal')
            #API call
            response =  client.chat.completions.create(
                    model="gpt-3.5-turbo-1106",
                    messages = message_list,
                    temperature=1.2
                )

            #Bot response
            assistant_message = response.choices[0].message
            message_list.append(assistant_message)

            # Change text color of bot response
            self.textbox.insert("end", "Bot: " + assistant_message.content + "\n\n", tags='Bot')
            self.textbox.tag_config('Bot', foreground='#FFBE71')
            self.textbox.tag_remove('Bot', 'end')
            # Autoscroll to bottom of textbox
            self.textbox.see('end')

            self.textbox.configure(state='disabled')

            #Have the bot speak its replies only when toggle is selected
            if(switch.get() == 1):
                tts_toggle(assistant_message.content)

        def change_appearance_mode_event(new_appearance_mode: str):
            customtkinter.set_appearance_mode(new_appearance_mode)

        def change_scaling_event(new_scaling: str):
            new_scaling_float = int(new_scaling.replace("%", "")) / 100
            customtkinter.set_widget_scaling(new_scaling_float)

        def export_to_file():
            session_divider = '----------------------------' + str(datetime.datetime.now().strftime("%H:%M:%S")) + '\n\n' 
            exported_content = self.textbox.get('1.0','end')
            file = open(r'C:\Users\tiger\Desktop\Personal Bot\chat_history' + '[' + str(datetime.date.today()) + ']' + '.txt', 'a+')
            file.write(session_divider + str(exported_content))
            file.close()
            print('File Exported')

        def record_audio():
            if (self.progressbar_1._mode == "determinate"):
                self.progressbar_1.configure(fg_color='#333333')
                self.progressbar_1.configure(mode="indeterminnate")
                self.progressbar_1.start()
                self.sidebar_button_1.configure(text="Stop Recording")
                
                winsound.Beep(1000,500)
                activate_stt()
            else:
                stop_audio()

        def stop_audio():
            self.progressbar_1.configure(fg_color='#1F538D')
            self.progressbar_1.configure(mode="determinate")
            self.progressbar_1.stop()
            self.progressbar_1.set(0)
            self.sidebar_button_1.configure(text="Record")

        def tts_toggle(message):
            speech_synthesis_result = speech_synthesizer.speak_text_async(message).get()
            if speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = speech_synthesis_result.cancellation_details
                print("Speech synthesis canceled: {}".format(cancellation_details.reason) + "\n Using default voice.")
                engine.say(message)
                engine.runAndWait()
        
        def activate_stt():
            def sub_execute():
                with sr.Microphone() as source:
                    audio_text = r.listen(source)
                    stop_audio()
                    try:
                        self.inputbox.insert("end", r.recognize_google(audio_text))
                    except:
                        self.inputbox.insert("end", "Sorry, I did not get that")
            threading.Thread(target=sub_execute).start()

        self.title("Personal Bot Prototype")
        self.geometry(f"{1100}x{580}")

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        # create sidebar frame
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="Personal Assistant", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Create Sidebar button
        self.sidebar_button_1 = customtkinter.CTkButton(self.sidebar_frame, text='Export Chat Log', command=export_to_file)
        self.sidebar_button_1.grid(row=1, column=0, padx=20, pady=10)

        ## Button to record audio in Sidebar
        self.sidebar_button_1 = customtkinter.CTkButton(self.sidebar_frame, text='Record', command=record_audio)
        self.sidebar_button_1.grid(row=2, column=0, padx=20, pady=10)

        ## Create progress bar in sidebar
        self.progressbar_1 = customtkinter.CTkProgressBar(self.sidebar_frame, fg_color='#1F538D')
        self.progressbar_1.grid(row=3, column=0, padx=(20, 10), pady=(10, 10), sticky="ew")
        self.progressbar_1.set(0)

        ## Create TTS switch in sidebar
        switch = customtkinter.CTkSwitch(master=self.sidebar_frame, text="Text-to-Speech", onvalue=1, offvalue=0)
        switch.grid(row=4, column=0, padx=10, pady=(0, 20))
        
        # Add options to change layout and scaling
        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"],
                                                                       command=change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))
        self.scaling_label = customtkinter.CTkLabel(self.sidebar_frame, text="UI Scaling:", anchor="w")
        self.scaling_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        self.scaling_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["80%", "90%", "100%", "110%", "120%"],
                                                               command=change_scaling_event)
        self.scaling_optionemenu.grid(row=8, column=0, padx=20, pady=(10, 20))


        # Textbox to display user input and bot response
        self.textbox = customtkinter.CTkTextbox(self, width=800, wrap='word', state='disabled', font=('Arial', 15))
        self.textbox.grid(row=0, column=1, columnspan=3, padx=(20, 20), pady=(20, 0), sticky="nsew")
        
        ## text field for entry
        # self.entry = customtkinter.CTkEntry(self, placeholder_text="Your response")
        # self.entry.grid(row=1, column=1, columnspan=2, padx=(20, 20), pady=(20, 20), sticky="nsew")
        # self.entry.bind('<Return>', user_input)
        self.inputbox = customtkinter.CTkTextbox(self, wrap='word', font=('Arial', 15))
        self.inputbox.grid(row=1, column=1, columnspan=2, padx=(20, 20), pady=(20, 0), sticky="nsew")
        self.inputbox.bind('<Return>', user_input)

        ## Button to save user input
        self.main_button = customtkinter.CTkButton(master=self, text="Send", fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"), height=100)
        self.main_button.grid(row=1, column=3, padx=(20, 20), pady=(40, 20), sticky="nsew")
        self.main_button.bind('<ButtonRelease>', user_input)
        
        # Set Default Values
        self.appearance_mode_optionemenu.set("Dark")
        self.scaling_optionemenu.set("100%")

if __name__ == "__main__":
    app = App()
    app.mainloop()

import io
import os
import sys
import json
import shutil
import base64
import whisper
import pandas as pd
import numpy as np
import gradio as gr
from PIL import Image
from openai import OpenAI
#from gradio.themes.utils.theme_dropdown import create_theme_dropdown
sys.path.append(os.getcwd()+'\\libs\\')
from libs.GPT4CreateJsonlDs import CreateJsonLGPT4
from libs.FromJsonlToCSV import JsonlToCSV

class ASSITANTWEBUI():

    def __init__(self):
        self.current_exe_path = os.getcwd()
        self.imgs_path = os.path.join(os.getcwd(), "imgs")
        self.audios_path = os.path.join(os.getcwd(), "audios")
        self.datasets_path = os.path.join(os.getcwd(), "datasets")
        self.ds_in_path = os.path.join(self.datasets_path, "in")
        self.ds_out_path = os.path.join(self.datasets_path, "out")
        #self.dropdown, self.js = create_theme_dropdown()
        self.system_prompt = False
        self.openai_api_key = False
        self.client = False
    
    def set_openai_api_key(self, api_key):
        self.openai_api_key = api_key

    def set_client_type(self, use_gpt):
        if use_gpt == "YES":
            self.client = OpenAI(api_key=self.openai_api_key)
            return self.openai_api_key
        else:
            self.client = OpenAI(base_url="http://localhost:1234/v1", api_key="not-needed")
            return "Using Models From LMStudio. (Use Llava1.5 for text-vision mode)"

    def text_response(self, prompt):
        print("[+] Text response")
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": f"Eres un asistente personal, piensa paso a paso y ayudame en todo lo que necesite porfavor"
                },
                {
                    "role": "user",
                    "content": f"{prompt}"
                }
            ]
        )
        print(response.choices[0].message.content)
        return response.choices[0].message.content


    def text_and_img_response(self, image, prompt):
        print("[+] Text with Image response")
        response = self.client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"{prompt}"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image}"
                        }
                    }
                ],
                }
            ],
            max_tokens=300,
        )
        print(response.choices[0].message.content)
        return response.choices[0].message.content
    
    def process_audio(self, audio):
        print(str(audio))
        
        # OpenAI API
        try:
            os.remove(self.audios_path+"/audio.wav")
            shutil.move(str(audio), self.audios_path+"/audio.wav")
            audio_file= open("audios/audio.wav", "rb")
            transcript = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file, 
                response_format="text"
            )
            print(transcript)
            return transcript
        except Exception as e:
            print(e)
            return ""

        # Local Whisper Usage
        """model = whisper.load_model("base")
        result = model.transcribe("audio.mp3")
        print(result["text"])"""


    ## BASIC USAGE SECTION ##
    def generate_response(self, prompt, image, audio):

        # Process audio from file o micro record
        audio_txt = self.process_audio(audio)
        
        # If image is loaded from webUI
        try:
            if isinstance(image, np.ndarray):
                pil_image = Image.fromarray(image.astype('uint8'), 'RGB')
                buffered = io.BytesIO()
                pil_image.save(buffered, format="JPEG")
                image_str = base64.b64encode(buffered.getvalue()).decode()
                return self.text_and_img_response(image_str, prompt+" "+audio_txt)
            else:
                image_str = image
                return self.text_and_img_response(image_str, prompt+" "+audio_txt)
        except Exception as e:
            return self.text_response(prompt+" "+audio_txt)

    ## UPLOAD FILES SECTION ##
    def get_directory_contents(self, path):
        try:
            return os.listdir(path)
        except Exception as e:
            return 'No Files Found'
    
    def reload_files(self):
        choices = self.get_directory_contents(self.ds_in_path)
        if type(choices) != list:
            gr.CheckboxGroup(label="Select Documents", choices=["No Files Found"], value=["No Files Found"])
        else:
            value = choices[0]
            return gr.CheckboxGroup(label="Select Documents", choices=choices, value=value)
    
    def upload_file(self, uploaded_file):
        if uploaded_file is None:
            return "No se subió ningún archivo."

        if not os.path.exists(self.ds_in_path):
            os.makedirs(self.ds_in_path)

        temp_path = uploaded_file.name
        final_path = os.path.join(self.ds_in_path, os.path.basename(temp_path))
        shutil.move(temp_path, final_path)
        print(f"Archivo guardado en: {final_path}")
        
        directory_contents = self.get_directory_contents(self.ds_in_path)
        return gr.CheckboxGroup(label="Select Documents", choices=directory_contents, value=directory_contents[0])
    
    ## CREATE DATASETS SECTION ##
    def create_user_message(self, row):
        return f"""prompt: {row['prompt']}"""

    def prepare_example_conversation(self, row):
        messages = []
        messages.append({"role": "system", "content": self.system_prompt})

        user_message = self.create_user_message(row)
        messages.append({"role": "user", "content": user_message})

        messages.append({"role": "assistant", "content": row["response"]})

        return {"messages": messages}
    
    def write_jsonl(self, data_list: list, filename: str) -> None:
        with open(filename, "w", encoding='utf-8') as out:
            for ddict in data_list:
                jout = json.dumps(ddict) + "\n"
                out.write(jout)

    
    def create_gpt_dataset(self, use_gpt_4, openai_api_key, files_names, system_prompt):
        self.system_prompt = system_prompt
        # JSONL
        jsonl_ds_manager = CreateJsonLGPT4()
        jsonl_ds_manager.use_openai_model = use_gpt_4
        jsonl_ds_manager.set_open_api_client(openai_api_key)
        output_file_name = '-'.join(files_names)
        output_file_name = output_file_name.replace('.pdf', '')
        json_file_name = jsonl_ds_manager.pdf_to_ds_qa(files_names, self.ds_in_path, self.ds_out_path, output_file_name, 'En base al texto que te voi a pasar y actuando como un profesor, dame 5 preguntas con sus respuestas en idioma castellano, cada pregunta y respuesta a de ser devuelta en formato JSON, donde la clave para la pregunta sera "prompt" y la clave para la repsuesta sera "response", responde unicamente en este formato sin añadir nada mas')

        # JSONL TO CSV
        jsonl_to_csv_manager = JsonlToCSV()
        jsonl_to_csv_manager.from_jsonl_to_csv(json_file_name, self.ds_out_path+'/'+output_file_name+'.csv')

        # CSV TO GPT-JSONL
        df = pd.read_csv(self.ds_out_path+'/'+output_file_name+'.csv', encoding='utf-8')
        print(df.head())
        # train data
        training_data = []
        training_df = df.loc[0:5]
        training_data = training_df.apply(self.prepare_example_conversation, axis=1).tolist()
        for example in training_data[:5]:
            print(example)
        # validation data
        validation_df = df.loc[6:10]
        validation_data = validation_df.apply(self.prepare_example_conversation, axis=1).tolist()

        # save datasets
        training_file_name = self.ds_out_path+'/'+output_file_name+"_finetune_training.jsonl"
        self.write_jsonl(training_data, training_file_name)
        validation_file_name = self.ds_out_path+'/'+output_file_name+"_finetune_validation.jsonl"
        self.write_jsonl(validation_data, validation_file_name)

        return self.ds_out_path+'/'+output_file_name+"_finetune_training.jsonl", self.ds_out_path+'/'+output_file_name+"_finetune_validation.jsonl"


    ## LLM UI ##
    def run_webui(self):
        #webui_theme = gr.Theme.from_hub("braintacles/CrimsonNight")
        directory_contents_list = self.get_directory_contents(self.ds_in_path)

        with gr.Blocks(gr.themes.Default()) as demo:
            
            gr.HTML(f"<div style='width: fit-content;margin: auto;'><img src='https://avatars.githubusercontent.com/u/69433799?v=4' alt='Logo' style='width:100%;height:200px;object-fit:scale-down;border-radius: 25% 10%;'>")  # Ajusta el width según necesites   
            gr.HTML(f"<a href='https://github.com/404-OS' style='text-align: center;'><h2>https://github.com/404-OS</h2></a>")

            gr.Markdown("SYSTEM CONFIGURATION")
            with gr.Row():
                with gr.Column(scale=8):
                    use_gpt4_select = gr.Dropdown(label="Use Chat-GPT4 (OpenAI API-KEY Required)", choices=["YES", "NO"], value="NO", show_label=True, multiselect=False)
                    openai_api_key = gr.Textbox(label="OpenAI API Key (Only if Chat-GPT4 is enabled)")
                with gr.Column(scale=4):
                    #self.dropdown.render()
                    toggle_dark_button = gr.Button(value="Toggle Dark")
                    model_tmp = gr.Dropdown(label="Model Temperature", choices=["0", "0.1", "0.2", "0.3", "0.4", "0.5", "0.6", "0.7", "0.8", "0.9", "1"], value="0.7", show_label=True, multiselect=False)
                    model_max_tokens = gr.Textbox(label="Model max generation tokens", value="-1")
            use_gpt4_select.change(self.set_client_type, inputs=use_gpt4_select, outputs=openai_api_key)
            openai_api_key.change(self.set_openai_api_key, inputs=openai_api_key)

            # MODEL BASIC USAGE SECTION
            with gr.Tab("ASK ME"):
                with gr.Row():
                    response_data = gr.TextArea(label="Response", max_lines=50, value="")
                with gr.Row():
                    prompt = gr.Textbox(label="Write your prompt:", placeholder="¿Ves algo raro en esta imagen?", value="¿Ves algo raro en esta imagen?", lines=5)
                with gr.Row():
                    imagen = gr.Image(label="Process any image", value=self.imgs_path+"/extreme_ironing.jpg")
                    audio = gr.Audio(label="Use microphone or audio file", type="filepath")
                generate_response_button = gr.Button("RESPONDE")
            generate_response_button.click(self.generate_response, inputs=[prompt, imagen, audio], outputs=response_data)

            # CREATE COMPANY DATASETS SECTION
            with gr.Tab("CREATE TRAIN DATASETS FOR CHAT-GPT"):
                with gr.Row():
                    file_upload = gr.File(label="Load and Save Documents")
                files_button = gr.Button("UPLOAD")
                with gr.Row():
                    documents_select = gr.CheckboxGroup(label="Select Documents", choices=directory_contents_list, value=directory_contents_list[0])
                    system_prompt = gr.Textbox(label="Write your system prompt:", placeholder="You are a helpful recipe assistant", value="You are a helpful recipe assistant", lines=5)
                with gr.Row():
                    csv_ds_file = gr.File(label="Download Training Dataset")
                    json_ds_file = gr.File(label="Download Validation Dataset")
                files_reload_button = gr.Button("Reload Available Files")
                create_ds_button = gr.Button("CREATE")
            files_button.click(self.upload_file, inputs=file_upload, outputs=documents_select)
            files_reload_button.click(self.reload_files, inputs=[], outputs=documents_select)
            create_ds_button.click(self.create_gpt_dataset, inputs=[use_gpt4_select, openai_api_key, documents_select, system_prompt], outputs=[csv_ds_file, json_ds_file])

            # CHANGE THEME MODE #
            #self.dropdown.change(None, self.dropdown, None, js=self.js)
            toggle_dark_button.click(
                None,
                js="""
                () => {
                    document.body.classList.toggle('dark');
                }
                """,
            )

        demo.launch(share=True, server_port=8080)# share=True / server_port=80
    
# USAGE
if __name__ == '__main__':
    llms_webui = ASSITANTWEBUI()
    llms_webui.openai_api_key = "your_api_key_here"
    llms_webui.run_webui()
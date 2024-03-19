import os
import json
import fitz  # PyMuPDF
import time
import openai
from openai import OpenAI


class CreateJsonLGPT4():
    
    def __init__(self):
        self.openai_api_client = False
        self.use_openai_model = "YES"
    
    
    def set_open_api_client(self, open_api_key):
        if self.use_openai_model == "NO":
            self.openai_api_client = OpenAI(base_url="http://localhost:1234/v1", api_key="not-needed")
        else:
            self.openai_api_client = OpenAI(api_key=open_api_key)

    def modify_text_with_gpt4(self, instruction, text):
        gpt_work = True
        while gpt_work == True:
            try:
                print('[+] CHAT GPT working')
                response = self.openai_api_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "user", "content": instruction + text}
                    ]
                )
                gpt_work = False
            except openai.error.APIError as e:
                print('[-] Error connecting to GPT')
                time.sleep(10)
        return response.choices[0].message.content

    def pdf_to_ds_qa(self, pdf_files, input_folder, output_folder, output_file_name, instruction):
        """Leer PDFs y obtener JSONL preguntas respuestas."""
        # Nombre del archivo JSONL que se usará para escribir el contenido
        jsonl_filename = f"{output_folder}\{output_file_name}.jsonl"

        # Abrir el archivo JSONL una sola vez
        with open(jsonl_filename, 'w', encoding='utf-8') as jsonl_file:
            # Procesar cada archivo PDF del listado dado
            for pdf_file in pdf_files:
                if pdf_file.endswith(".pdf"):
                    pdf_path = os.path.join(input_folder, pdf_file)
                    doc = fitz.open(pdf_path)

                    # Procesar cada página del PDF
                    for page_num in range(len(doc)):
                        if page_num != 0:
                            print("[+] Processing page: "+str(page_num))
                            page = doc[page_num]
                            page_text = page.get_text()
                            print(page_text)
                            page_text_gpt = self.modify_text_with_gpt4(instruction, page_text)
                            page_text_gpt = page_text_gpt.replace('[', '')
                            page_text_gpt = page_text_gpt.replace(']', '')
                            print(page_text_gpt)

                            # JSONL
                            # Dividir el texto en un array de JSONs
                            json_objects = page_text_gpt.split('},')
            
                            for json_num, json_object in enumerate(json_objects):
                                if json_num != len(json_objects) -1:
                                    json_object = json_object+'}'
                                
                                print(json_object)
                                try:
                                    # Convertir la cadena a un objeto JSON para asegurarse de que es válido
                                    json_data = json.loads(json_object)
                                    # Escribir el objeto JSON en el archivo .jsonl
                                    jsonl_file.write(json.dumps(json_data, ensure_ascii=False) + ',')
                                    print("[+] JSON added to DS")
                                except json.JSONDecodeError:
                                    print(f"[-] Error decoding JSON response") # json_object
                            
                            # Tiempo de espera para la API de GPT
                            time.sleep(10)
                            #break
                    #break
        return jsonl_filename

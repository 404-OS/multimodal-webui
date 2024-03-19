import os
import sys
import json
import csv

class JsonlToCSV():

    def __init__(self):
        pass

    def from_jsonl_to_csv(self, jsonl_path, csv_path):
        file = open(jsonl_path, encoding='utf-8')
        data = file.read()
        file.close()
        real_data = data.split('},')

        # Verificar si el archivo CSV ya existe y si está vacío
        file_exists = os.path.exists(csv_path) and os.path.getsize(csv_path) > 0
        
        for rd in real_data:
            current_rd = rd+'}'
            
            try:
                # Intentar cargar la cadena como un objeto JSON
                data = json.loads(current_rd)

                # Verificar si las claves 'prompt' y 'response' están en el JSON
                if 'prompt' in data and 'response' in data:
                    
                    # Abrir o crear el archivo CSV y añadir los datos
                    with open(csv_path, 'a', newline='', encoding='utf-8') as csv_file:
                        
                        csv_writer = csv.writer(csv_file)
                        
                        # Escribir las cabeceras si el archivo es nuevo o está vacío
                        if not file_exists:
                            csv_writer.writerow(['prompt', 'response'])
                            file_exists = True  # Asegurarse de no volver a escribir la cabecera
                        
                        # Añadir los valores de 'prompt' y 'response' al CSV
                        csv_writer.writerow([data['prompt'], data['response']])

                    print("Datos añadidos al archivo CSV correctamente.")
                else:
                    print("La cadena JSON no contiene las claves 'prompt' y 'response'.")

            except json.JSONDecodeError:
                print("La cadena no es un JSON válido.")

        print("Archivo CSV creado exitosamente.")

# USAGE
"""
jsonl_path = 'D:/IA/TEXTO/AIP-WEBUI/ds_generator/finetune/output/aip_data_clean.jsonl'
csv_path = 'D:/IA/TEXTO/AIP-WEBUI/ds_generator/finetune/output/aip_data_clean.csv'
from_jsonl_to_csv(jsonl_path, csv_path)
"""
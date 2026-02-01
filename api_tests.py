import requests
import json

# URL base da sua API local
BASE_URL = "http://127.0.0.1:8000"

def criar_medico():
    print("\n--- TENTANDO CRIAR UM MÉDICO ---")
    
    url = f"{BASE_URL}/medicos/"
    
    # Dados que vamos enviar (JSON Payload)
    payload = {
        "name": "Dr. House",
        "last_name": "Gregory",
        "email": "house.greg@princeton.org" # Se rodar 2x vai dar erro pq o email é unique
    }
    

    try:
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            print("✅ Sucesso! Médico criado:")
            print(json.dumps(response.json(), indent=4))
        else:
            print(f"❌ Erro {response.status_code}:")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("☠️ Erro: O servidor parece estar desligado.")

def listar_medicos():
    print("\n--- LISTANDO MÉDICOS DO BANCO ---")
    
    url = f"{BASE_URL}/medicos/"
    
    # Fazendo o GET request
    response = requests.get(url)
    
    if response.status_code == 200:
        medicos = response.json()
        print(f"📋 Total encontrado: {len(medicos)}")
        for medico in medicos:
            print(f"- ID: {medico['id']} | Nome: {medico['name']} {medico['last_name']}")
    else:
        print("Erro ao listar médicos")



#  ⋙──────────────────────────────────────────────────────────────────────➤




if __name__ == "__main__":
    # 1. Cria
    criar_medico()
    
    # 2. Lista

    
    
    
    

    
    
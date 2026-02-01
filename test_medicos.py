import requests
import json

BASE_URL = "http://127.0.0.1:8000"


def criar_medico(payload):
    print(f"\n--- TENTANDO CRIAR O MÉDICO: {payload.get('name')} ---")
    url = f"{BASE_URL}/medicos/"
    
    # O payload agora vem de fora
    response = requests.post(url, json=payload)
    
    # Se a API retornar 400/500, estoura o erro aqui
    response.raise_for_status()
    
    print("✅ Sucesso! JSON Retornado:")
    print(json.dumps(response.json(), indent=4))




def listar_medicos():
    print("\n--- LISTANDO MÉDICOS ---")
    url = f"{BASE_URL}/medicos/"
    
    response = requests.get(url)
    
    # Vai estourar se não for 200 OK
    response.raise_for_status()
    
    print("✅ Lista Recebida:")
    print(json.dumps(response.json(), indent=4))


#  ⋙─────────────────────────────────────────────────────────────➤




dados_novo = {
    "name": "",
    "last_name": "",
    "email": "wsson@princeton.org"  # <--- Mudei o email
}

criar_medico(dados_novo)

    
listar_medicos()



















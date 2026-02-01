import requests
import json

BASE_URL = "http://127.0.0.1:8000"

# O SEGREDO: Usamos uma 'Session' para persistir o Cookie entre as requisições
# É como se fosse um navegador aberto
client = requests.Session()




#  (✪) register ⋙⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫸
def register(username, email, password):
    print(f"\n--- 1. TENTANDO REGISTRAR: {email} ---")
    url = f"{BASE_URL}/auth/register"
    
    payload = {
        "username": username,
        "email": email,
        "password": password
    }
    
    response = client.post(url, json=payload)
    
    if response.status_code == 400:
        print(f"⚠️ Aviso: {response.json().get('detail')}")
    else:
        response.raise_for_status()
        print("✅ Usuário criado com sucesso!")
        print(json.dumps(response.json(), indent=4))





#  (✪) login ⋙⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫸
def login(email, password):
    print(f"\n--- 2. TENTANDO FAZER LOGIN: {email} ---")
    url = f"{BASE_URL}/auth/login"
    
    payload = {
        "email": email,
        "password": password
    }
    
    # O cookie HttpOnly será salvo automaticamente dentro do objeto 'client'
    response = client.post(url, json=payload)
    response.raise_for_status()
    
    print("✅ Login realizado! Cookie recebido e guardado na sessão.")
    print("Cookies na sessão:", client.cookies.get_dict())






def logout(): #  ⋙⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫸
    print("\n--- 4. TENTANDO FAZER LOGOUT ---")
    url = f"{BASE_URL}/auth/logout"
    
    # O endpoint vai mandar limpar o cookie na sessão do client
    response = client.post(url)
    response.raise_for_status()
    
    print("✅ Logout realizado! O servidor mandou limpar o cookie.")
    # Verifica se o cookie sumiu da sessão do requests
    print("Cookies restantes na sessão:", client.cookies.get_dict())
    
    





#  (✪) testar_rota_protegida_medico ⋙⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫸
def testar_rota_protegida_medico():
    print("\n--- 3. TENTANDO CRIAR MÉDICO (Rota Protegida) ---")
    url = f"{BASE_URL}/medicos/"
    
    payload = {
        "name": "Dr. Chase",
        "last_name": "Robert",
        "email": "chaseassa@princeton.org"
    }

    # Como estamos usando o 'client' (Session) que já tem o cookie, deve passar
    response = client.post(url, json=payload)
    
    # Se der erro (ex: 401), vai mostrar o motivo
    if response.status_code != 200 and response.status_code != 201:
        print(f"❌ Falha (Status {response.status_code}):")
        print(response.text)
    
    response.raise_for_status()
    print("✅ Médico criado com sucesso (Autenticação funcionou)!")
    print(json.dumps(response.json(), indent=4))
# # ── ⋙─────────────────────────────────────────────────────────────────➤




# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
#  ø●○● ○○○○ ●●●● ○○○○ ●●●● ○○○○ ●●●● ○○○○ ●●●● ○○○○ ●●●● ○○○○ ●●●● ○○○○ ●●●● ○○○○ ●●●● ○○○○ ●●●● ○○○○ ●●●● ○○○ø ║                                                                                 ║
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════╝


# ┌────────────┐
# │ MyUSerTest │
# └────────────┘

USER = "admin_master"
EMAIL = "addfsmin@hospital.com"
PASS = "senha123"


# 1. Registra
register(USER, EMAIL, PASS)

# 2. Loga (Aqui pegamos o cookie)
login(EMAIL, PASS)

# 3. Tenta acessar a rota que você bloqueou
testar_rota_protegida_medico()


logout()






print(f"\n--- 2. TENTANDO FAZER LOGIN: {EMAIL} ---")

url = f"{BASE_URL}/auth/login"


payload = {
    "email": EMAIL,
    "password": PASS
}


# O cookie HttpOnly será salvo automaticamente dentro do objeto 'client'
response = client.post(url, json=payload)


response.cookies


response.raise_for_status()

print("✅ Login realizado! Cookie recebido e guardado na sessão.")
print("Cookies na sessão:", client.cookies.get_dict())














































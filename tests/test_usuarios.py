import requests
import json

BASE_URL = "http://127.0.0.1:8000"

# O SEGREDO: Usamos uma 'Session' para persistir o Cookie entre as requisições
# É como se fosse um navegador aberto
client = requests.Session()



# (●) print_step
def print_step(step_name):
    print(f"\n{'┌' + '─' * len(step_name + 'øø') + '┐'}")
    print(f"│ {step_name} │")
    print(f"{'└' + '─' * len(step_name + 'øø') + '┘'}")



# (●) check_response
def check_response(response, label=""):
    x = str(response.status_code)
    if x[0] == '2':
        print(f"✔ [SUCESSO] {label} - Status: {response.status_code}")
        try:
            return response.json()
        except:
            return response.text
    else:
        print(f"✖ [ERRO] {label} - Status: {response.status_code}")
        print(f"Detalhe: {response.text}")
        return None
    




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



#  (✪) logout ⋙⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫸
def logout(): 
    print("\n--- 4. TENTANDO FAZER LOGOUT ---")
    url = f"{BASE_URL}/auth/logout"
    
    # O endpoint vai mandar limpar o cookie na sessão do client
    response = client.post(url)
    response.raise_for_status()
    
    print("✅ Logout realizado! O servidor mandou limpar o cookie.")
    # Verifica se o cookie sumiu da sessão do requests
    print("Cookies restantes na sessão:", client.cookies.get_dict())
    
    



#  (✪) refresh ⋙⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫸
def refresh():
    print("\n--- 4. TENTANDO RENOVAR O TOKEN (REFRESH) ---")
    url = f"{BASE_URL}/auth/refresh"
    
    # O client já tem o cookie 'refresh_token' guardado do login
    # Como definimos path="/auth/refresh" no cookie, o navegador (ou Session)
    # só envia o cookie se a URL bater.
    
    response = client.post(url)
    
    if response.status_code == 200:
        print("✅ Token renovado! Novos cookies recebidos.")
        print("Novos Cookies:", client.cookies.get_dict())
    else:
        print(f"❌ Falha no Refresh: {response.text}")
        response.raise_for_status()



# (●) ╔═══════════════════════════════════════════════════════════════════════════════════════════════════════════════╗ ┌──────┐
# (●) ║ ø●○● ○○○○ ●●●● ○○○○ ●●●● ○○○○ ●●●● ○○○○ ●●●● ○○○○ ●●●● ○○○○ ●●●● ○○○○ ●●●● ○○○○ ●●●● ○○○○ ●●●● ○○○○ ●●●● ○○○ø ║ │ MAIN │  ⋙────────➤
# (●) ╚═══════════════════════════════════════════════════════════════════════════════════════════════════════════════╝ └──────┘


# ● ┌───────────────────┐
# ● │ TESTE DE SANIDADE │
# ● └───────────────────┘

USER = "admin_master"
EMAIL = "adminho@hospital.com"
PASS = "senha123"

register(USER, EMAIL, PASS)
login(EMAIL, PASS)
refresh()
logout()











































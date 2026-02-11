# -*- coding: utf-8 -*-

import requests
import json
from datetime import date

# CONFIGURAÇÃO
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/financeiro" # Ajuste conforme seu prefixo real
AUTH_URL = f"{BASE_URL}/auth/login/" # Ajuste conforme sua rota de auth

# Credenciais de um usuário admin já existente no seu banco
USER_EMAIL = "adminho@hospital.com" 
USER_PASSWORD = "senha123"

# Sessão mantém os cookies (HttpOnly) entre requisições
session = requests.Session()


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
    


# (●) ╔═══════════════════════════════════════════════════════════════════════════════════════════════════════════════╗ ┌──────┐
# (●) ║ ø●○● ○○○○ ●●●● ○○○○ ●●●● ○○○○ ●●●● ○○○○ ●●●● ○○○○ ●●●● ○○○○ ●●●● ○○○○ ●●●● ○○○○ ●●●● ○○○○ ●●●● ○○○○ ●●●● ○○○ø ║ │ MAIN │  ⋙────────➤
# (●) ╚═══════════════════════════════════════════════════════════════════════════════════════════════════════════════╝ └──────┘


# ╔════════════════╗ ┌───┐
# ║  AUTENTICAÇÃO  ║ │ ø │ ⪼————–⪫
# ╚════════════════╝ └───┘

print_step("Autenticação")
payload_login = {"email": USER_EMAIL, "password": USER_PASSWORD}
resp = session.post(AUTH_URL, json=payload_login)
check_response(resp)



# ╔════════════════╗ 
# ║  DEPENDÊNCIAS  ║ 
# ╚════════════════╝ 


#  (●) profissionais  ⪼——————————————————————————————————————————————–⪫
print_step("Dependências")
resp_prof = session.post(f"{API_URL}/profissionais", json={
    "nome": "Dr. House",
    "ativo": True
})
prof_data = check_response(resp_prof)
prof_id = prof_data['id']


# (●) serviço consulta ⪼——————————————————————————————————————————————–⪫
resp_serv_cons = session.post(f"{API_URL}/servicos", json={
    "nome": "Consulta Cardiológica",
    "categoria": "CONSULTA",

})

serv_cons_data = check_response(resp_serv_cons, "Criar Serviço (Consulta)")
serv_cons_id = serv_cons_data['id']



# (●) serviço terapia ⪼——————————————————————————————————————————————–⪫
resp_serv_ter = session.post(f"{API_URL}/servicos", json={
    "nome": "Sessão de RPG",
    "categoria": "TERAPIA",

})

serv_ter_data = check_response(resp_serv_ter, "Criar Serviço (Terapia)")
serv_ter_id = serv_ter_data['id']



# ╔═══════════════╗ 
# ║  LANÇAMENTOS  ║ 
# ╚═══════════════╝ 



# ✪ CENÁRIO 1: Lançamento COM Paciente NOVO (On-the-fly)  ⪼——————————————————————————————————————————————–⪫
print_step("Cenário 1: Paciente On-the-fly")

payload_lancamento_novo = {
    "data_pagamento": str(date.today()),
    "data_competencia": str(date.today()),
    "valor": 350.00,
    "metodo_pagamento": "PIX",
    "observacao": "Teste script on-the-fly",
    
    # Dados Relacionais
    "servico_id": serv_cons_id,
    "profissional_id": prof_id, # Obrigatório pois é CONSULTA
    
    # O Pulo do Gato: Não envio ID, envio NOME
    "paciente_nome": "Paciente Teste Script da Silva" 
}


resp_lanc = session.post(f"{API_URL}/lancamentos", json=payload_lancamento_novo)
data_lanc = check_response(resp_lanc, "Criar Lançamento + Paciente")


if data_lanc:
    print(f"   -> ID do Paciente Criado Automaticamente: {data_lanc['paciente']['id']}")
    print(f"   -> Nome retornado: {data_lanc['paciente']['nome']}")





# ✪ CENÁRIO 2: Teste de Validação (Consulta sem Médico) ⪼——————————————————————————————————————————————–⪫
print_step("Cenário 2: Validação (Deve Falhar)")

payload_erro = {
    "data_pagamento": str(date.today()),
    "data_competencia": str(date.today()),
    "valor": 350.00,
    "metodo_pagamento": "DINHEIRO",
    "servico_id": serv_cons_id, # É CONSULTA!
    "paciente_nome": "Outro Paciente",
    "profissional_id": None # <--- ERRO: Deveria ser obrigatório
}

resp_erro = session.post(f"{API_URL}/lancamentos", json=payload_erro)
check_response(resp_erro, "Tentar Consulta sem Profissional")





# ✪ CENÁRIO 3: Terapia sem Médico (Deve Passar) ⪼——————————————————————————————————————————————–⪫
print_step("Cenário 3: Terapia sem Profissional (Deve Passar)")

payload_terapia = {
    "data_pagamento": str(date.today()),
    "data_competencia": str(date.today()),
    "valor": 150.00,
    "metodo_pagamento": "CARTAO_CREDITO",
    "servico_id": serv_ter_id, # É TERAPIA!
    "paciente_nome": "Paciente da Terapia",
    "profissional_id": None # <--- OK: Terapia permite null
}

resp_ter = session.post(f"{API_URL}/lancamentos", json=payload_terapia)
check_response(resp_ter, "Criar Terapia sem Profissional")

































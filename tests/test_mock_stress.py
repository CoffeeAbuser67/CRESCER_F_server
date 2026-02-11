# -*- coding: utf-8 -*-
"""
@author: Henry 🦀
"""

import requests
import json
import random
import time
from datetime import date, timedelta


# ╔══════════════╗ 
# ║ CONFIGURAÇÃO ║⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫸
# ╚══════════════╝ 

 
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/financeiro"
AUTH_URL = f"{BASE_URL}/auth/login/"

# Credenciais Admin
USER_EMAIL = "adminho@hospital.com"
USER_PASSWORD = "senha123"

session = requests.Session()

# ╔═════════════╗ 
# ║ UTILITÁRIOS ║◡◠◡◠-➤
# ╚═════════════╝ 


# (●) print_step
def print_step(step_name):
    print(f"\n{'┌' + '─' * len(step_name + 'øø') + '┐'}")
    print(f"│ {step_name} │")
    print(f"{'└' + '─' * len(step_name + 'øø') + '┘'}")

# (●) print_header
def print_header(header_name):
    print(f"{'╔' + '═' * len(header_name + 'øø') + '╗'}")
    print(f"║ {header_name} ║")
    print(f"{'╚' + '═' * len(header_name + 'øø') + '╝'}")


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

# (●) get_random_date
def get_random_date():
    """Gera uma data aleatória nos últimos 30 dias"""
    days_offset = random.randint(0, 30)
    return str(date.today() - timedelta(days=days_offset))

# (●) get_random_paciente
def get_random_paciente():
    """Gera nomes diferentes para testar a criação on-the-fly"""
    sobrenomes = ["Silva", "Santos", "Oliveira", "Souza", "Pereira", "Lima", "Ferreira"]
    nomes = ["Stress", "Carga", "Teste", "Bug", "Caos", "Jmeter", "Locust"]
    return f"{random.choice(nomes)} {random.choice(sobrenomes)}"

# (●) get_random_payment
def get_random_payment():
    return random.choice(["PIX", "DINHEIRO", "CARTAO_CREDITO", "CARTAO_DEBITO"])


 # ╔═══════╗ 
 # ║ SETUP ║◡◠◡◠-➤
 # ╚═══════╝ 
 
print_header('SETUP')

print_step("Iniciando Login")
payload_login = {"email": USER_EMAIL, "password": USER_PASSWORD}
resp = session.post(AUTH_URL, json=payload_login)
check_response(resp)



print_step("Criando Médicos")
medicos = ["Dr. Malvado", "Dr. Loucasso", "Dr. da Putaria"]
medicos_ids = []
for med in medicos: 
    prof_resp = session.post(f"{API_URL}/profissionais", json={"nome": med, "ativo": True})
    result = check_response(prof_resp)
    medicos_ids.append(result['id'])

    

print_step("Criando Serviço Consulta")
serv_c_resp = session.post(f"{API_URL}/servicos", json={"nome": "Consulta", "categoria": "CONSULTA"})
result = check_response(serv_c_resp)
serv_c_id = result['id']



print_step("Criando Serviços de Terapia")
terapias = ["Terapia pra doido", "Terapia pra dodoi", "Terapia pra doente"]
terapias_ids =[] 
for terapia in terapias:
    serv_t_resp = session.post(f"{API_URL}/servicos", json={"nome": terapia, "categoria": "TERAPIA"})
    result = check_response(serv_t_resp)
    terapias_ids.append(result['id'])




# ╔═════════════════════════╗ 
# ║ BOMBARDEIRO JACAREZEIRO ║⇌⇌⇌⇌⇌⇌⇌⫸
# ╚═════════════════════════╝ 
print_header('BOMBARDEIRO JACAREZEIRO')


TOTAL_REQUISICOES = 100 
sucessos = 0
erros = 0
start_time = time.time()



for i in range(1, TOTAL_REQUISICOES + 1):
    
    # Decide o cenário aleatoriamente
    cenario = random.choice(['CONSULTA', 'TERAPIA', 'MISTO'])
    
    payload = {
        "data_pagamento": get_random_date(),
        "data_competencia": get_random_date(),
        "metodo_pagamento": get_random_payment(),
        "paciente_nome": get_random_paciente(),
        "observacao": f"Load Test #{1}"
        }

    if cenario == 'CONSULTA':
        payload['servico_id'] = serv_c_id
        payload['profissional_id'] = random.choice(medicos_ids)
        payload['valor'] = random.randint(300, 500)
    
    elif cenario == 'TERAPIA':
        payload['servico_id'] = random.choice(terapias_ids)
        payload['profissional_id'] = None # Testando nulo
        payload['valor'] = random.randint(80, 150)
        
    else: # MISTO (Consulta com valor quebrado)
        payload['servico_id'] = random.choice([serv_c_id] + terapias_ids)
        payload['profissional_id'] = random.choice(medicos_ids)
        payload['valor'] = round(random.uniform(100.0, 400.0), 2)


    # DISPARO
    try:
        r = session.post(f"{API_URL}/lancamentos", json=payload)
        
        if r.status_code == 201:
            sucessos += 1
            print(f"\r[{i}/{TOTAL_REQUISICOES}] ✅ Criado ({cenario}) - Paciente: {payload['paciente_nome']}", end="")
        else:
            erros += 1
            print(f"\n[{i}/{TOTAL_REQUISICOES}] ❌ Erro {r.status_code}: {r.text}")
            
    except Exception as e:
        erros += 1
        print(f"\n[{i}/{TOTAL_REQUISICOES}] ☠️ Exception: {e}")



# ╔═══════════╗ 
# ║ RELATÓRIO ║─────────────➤
# ╚═══════════╝ 

print_header('RELATÓRIO JACAREZEIRO')
end_time = time.time()
duration = end_time - start_time

print(f"\n\n{'='*40}")
print("RESUMO DO ESTRESSE")
print(f"{'='*40}")
print(f"Tempo Total:     {duration:.2f} segundos")
print(f"Média:           {TOTAL_REQUISICOES / duration:.2f} req/s")
print(f"✔️ Sucessos:      {sucessos}")
print(f"✖️ Falhas:        {erros}")
print(f"{'='*40}")

if erros == 0:
    print("🏆 BACKEND BLINDADO! Nenhum erro detectado.")
else:
    print("⚠️  ATENÇÃO: Ocorreram falhas durante o teste.")








import csv
import os
import random

first_names = ["Ana", "Bruno", "Carlos", "Daniela", "Eduardo", "Fernanda", "Gabriel", "Helena", "Igor", "Juliana"]
last_names = ["Silva", "Santos", "Oliveira", "Pereira", "Costa", "Almeida", "Ribeiro", "Martins", "Barbosa", "Rocha"]
departments = ["Recursos Humanos", "Finanças", "Engenharia", "Marketing", "Vendas"]
supervisors = ["Supervisor A", "Supervisor B", "Supervisor C", "Supervisor D", "Supervisor E"]

current_code = 0

def generate_unique_code():
    global current_code
    code = f"{current_code:04d}"
    current_code += 1
    return code

def generate_person():
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    code = generate_unique_code()
    department = random.choice(departments)
    supervisor = random.choice(supervisors)
    return f"{first_name} {last_name}, Code: {code}, Department: {department}, Supervisor: {supervisor}"

if __name__ == "__main__":
    # Ensure the data directory exists
    os.makedirs('/home/br4b0/Desktop/novo_lar/bergamoto/data', exist_ok=True)
    
    with open('/home/br4b0/Desktop/novo_lar/bergamoto/data/people.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["name", "pin", "setor", "supervisor"])
        for _ in range(200):
            person = generate_person().split(", ")
            name = person[0]
            code = person[1].split(": ")[1]
            department = person[2].split(": ")[1]
            supervisor = person[3].split(": ")[1]
            writer.writerow([name, code, department, supervisor])

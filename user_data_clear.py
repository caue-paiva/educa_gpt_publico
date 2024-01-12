import json , os


with open("MainIntegration/json_userData.json", "r") as fp:
    dados = json.load(fp)

    for key, value in dados.items():
        if isinstance(value, int):  # If the value is a number
            dados[key] = 0
        elif isinstance(value, list):  # If the value is a list
            for i in range(len(value)):
                value[i] = 0
        

    with open('MainIntegration/json_userData.json', 'w') as fp:
        json.dump(dados, fp)
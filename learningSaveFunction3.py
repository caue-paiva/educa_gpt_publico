import openai
import json
import os
from dotenv import load_dotenv

load_dotenv(os.path.join("keys.env"))

openai.api_key = os.getenv("OPENAI_API_KEY")
#GPT_MODEL_FUNC_CALLING = os.getenv("GPT_MODEL_FUNC_CALLING")
GPT_MODEL_FUNC_CALLING = "gpt-3.5-turbo-0613"

# no json, na lista de cada disciplina, o primeiro numero é o total de questões e o segundo o número de acertos;

GLOBAL_SUB_TOPICS = ["Historia_Brasil","Historia geral","Idade_media" , "Geografia_Fisica", "Geografia_Politi/social"]

def save_studen_progress(Subtopico, resposta_correta, Resposta_aluno:str)->str:
  Resposta_aluno = Resposta_aluno.lower()
  with open(os.path.join("json_userData.json"), 'r') as fp:
    dados = json.load(fp)
    "Identifica o subTopico da questão e se o aluno acertou a questão ou não"
    dados[Subtopico][0] += 1
    dados["total_questoes"] += 1
    if (resposta_correta == Resposta_aluno):
     dados[Subtopico][1] += 1
     dados["total_acertos"] += 1
     print("acertou")
    
  with open(os.path.join("json_userData.json"), 'w') as fp:
        json.dump(dados, fp) 
  return f"progresso salvo no subtopico {Subtopico}"

def general_user_stats()->str:
  TotalQuest = 0
  TotalAcertos = 0 
  with open(os.path.join("json_userData.json"), 'r') as fp:
   dados = json.load(fp)
   TotalQuest = dados["total_questoes"]
   TotalAcertos = dados["total_acertos"]
  
  porce_acertos = ((TotalAcertos/TotalQuest)*100)
  resposta:str = f"No Total,  você fez {TotalQuest} questões e teve {porce_acertos:.2f}% de acertos "
  return resposta 

#Pense passo a passo e decida se a resposta do aluno corresponde ou não à resposta verdadeira da questão, caso a resposta verdadeira não esteja disponível 
  
def handle_user_answer(Userinput:str)->str:

 print("entrando na funcao de salvar progresso "+ Userinput+ "\n\n")
 function_llm_response = openai.ChatCompletion.create(
  model = GPT_MODEL_FUNC_CALLING,
  messages = [{"role":"assistant", "content": """pense passo a passo, leia o que é pedido non enunciado e responda a alternativa correta questão, essa resposta será parte da sua resposta final  """ },
    {"role":"user", "content": Userinput }],
  
  functions =[ 
     {
        "name": "save_studen_progress",
        "description": "Analiza o tópico de uma questão  e diz qual o tópico da questão e se o aluno escolheu a alternativa correta da questão, lembre se que não importa se a resposta for uma letra maiuscula ou minuscula:  a = A, b= B, c=C, d=D, e= E",
        "parameters": {
            "type": "object",
            "properties": {
                "Subtopico": {
                    "type": "string",
                    "enum": ["Historia_Brasil","Historia geral","Idade_media","Geografia_Politi/social","Geografia_Fisica"],
                    "description": "identifique qual o subtopico/tema da questão entre as opções , descreva EXATAMENTE umas das opções"
                },
                "resposta_correta": {
                    "type": "string",
                    "enum": ["a", "b", "c", "d", "e"],
                    "description": "Pense passo-a-passo, se atente na pergunta sendo feita, resolva a questão e ache a alternativa correta e retorne qual a letra correta dessa alternativa",
                },
                "Resposta_aluno":{
                    "type": "string",
                    "enum": ["a", "b", "c", "d", "e"],
                    "description": "Abaixo da questão atual o aluno vai dar a resposta dele sobre a questão, diga qual a alternativa que ele trouxe, não deixe a resposta do aluno interferir em achar a resposta certa",
            },
            },
            "required":["Subtopico", "resposta_correta","Resposta_aluno" ],
        },
    }, 
   ],
 function_call = "auto"
 )

 required_action_dict:dict = function_llm_response["choices"][0]["message"]
 
 if required_action_dict.get("function_call"): #ver se o LLM mandou chamar alguma funcao baseado no input
    function_name = required_action_dict["function_call"]["name"]
    arguments = json.loads(required_action_dict["function_call"]["arguments"])
    Subtopico = arguments["Subtopico"]
    Resposta_aluno = arguments["Resposta_aluno"]
    resposta_correta = arguments["resposta_correta"]
    
    #print(type(Subtopico))
    #print("teste sub" + str(Subtopico))
    function_response:str = save_studen_progress(
        Subtopico=str(Subtopico),
        resposta_correta=str(resposta_correta),
        Resposta_aluno=str(Resposta_aluno)
    )
    print(function_response)
    chat_bot_response = openai.ChatCompletion.create(
      model = GPT_MODEL_FUNC_CALLING, #ver se esse precisa realmente ser um modelo function caller ou nao
      messages = [ {"role":"assistant", "content": "Fale se o aluno acertou ou não a questão, se ele errar mostre a resposta certa e sua lógica. Apenas fale sobre assuntos pertinentes ao constexto da questao e da resposta do usuario" },
        
        {"role":"user", "content": Userinput },
                  required_action_dict, {   
                     "role": "function",
                     "name": function_name,
                     "content": function_response
                    },
                  
              ],
      )
    Parsed_response:str = chat_bot_response["choices"][0]["message"]["content"]
    user_stats = general_user_stats()  #retorna o progresso geral do user 
    return (user_stats + " \n "+ Parsed_response) 

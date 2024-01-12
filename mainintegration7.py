from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
import os
from googleapiclient.discovery import build 
from langchain.prompts import PromptTemplate
import qdran_query as QD
import intent_identi as inten_iden
import learningSaveFunction3 as save_progress #precisa do from . import para rodar o codigo no webserver do heroku
from dotenv import load_dotenv



load_dotenv(os.path.join('keys.env'))

#GPT_MODEL_NORMAL_CHAT = os.getenv("GPT_MODEL_NORMAL_CHAT")
#GPT_MODEL_FUNC_CALLING = os.getenv("GPT_MODEL_FUNC_CALLING")
GPT_MODEL_FUNC_CALLING = "gpt-3.5-turbo-0613"
GPT_MODEL_NORMAL_CHAT =  "gpt-3.5-turbo-1106"

class GoogleSearch():
    def __init__(self):
        self.service = build(
            "customsearch", "v1", developerKey=os.environ.get("GOOGLE_API_KEY")
        )

    def search(self, query,num_results=4):
        response = (
            self.service.cse()
            .list(
                q=query,
                cx=os.environ.get("GOOGLE_CSE_ID"),
                num=num_results
            )
            .execute()
        )
        return response['items']
    def filter(self, response):
        response_with_links = ''

        for result in response:
            response_with_links += f"Link: {result['link']}\n"

            response_with_links += f"titulo: {result['title']}\n"
            response_with_links += f"Conteúdo: {result['snippet']}\n\n"
        return response_with_links


import unicodedata
def remove_non_en_chars(input_str:str)->str:
    normalized_text = unicodedata.normalize('NFKD', input_str)
    return normalized_text.encode('ascii', 'ignore').decode('ascii')

class ChatBot():
    
    chat_memory: list[dict[str,str]]  #array responsavel pela memoria do chat, composto por dicionarios cada um com 2 keys e 2 values  {"user": input, "assistant": text}
    current_action:str
    chat_subject: str
    subjectPrompt:str #string com a matéria que o chat vai ser sobre

    #abaixo é o corpo da prompt utilizada por todas as classes
    prompt_body:str = """ de forma precisa e profunda para os alunos. Pense passo-a-passo no melhor jeito de responder uma pergunta ou resolver algo e apenas traga resposta corretas que o aluno aprecie

    {chat_history}
    aluno: {human_input}
    tutor: """   #prompt do chat principal
    

    def __init__(self, chat_hist:list, chat_meta_data: dict[str,str]):
        #carrega o historico de chat e matéria nas listas e variaveis do objeto
        self.chat_memory:list[dict[str,str]] = []
        for dic in chat_hist:
            self.chat_memory.append(dic)  #adiciona na memoria as mensagens antigas
       
        incoming_chat_subject =  chat_meta_data.get('subject') #.get(key) não da erro se não existir essa key
        if  incoming_chat_subject ==  None:
            self.chat_subject: str = "Assuntos gerais" #caso o json não tenha essa key, uma mensagem de assuntos gerais será o assunto
        else:
            self.chat_subject: str =  incoming_chat_subject  #dict de metadados como qual o assunto/matéria do chat
        
        self.subjectPrompt = f"você é um tutor que explica de forma didática as matérias {self.chat_subject}  "  #seta a promp da matéria do chatbot
        

    def __classify_input__(self, UserInput: str)-> str:
        input_parsed = UserInput.lower()
        next_action = inten_iden.intent_identi(input_parsed) #problemas no NLU com o modelo não reconhecendo web e internet como keywords de pesquisa_web, aparentemente ele ve as 2 palavras como parte de pesquisa_web mas ele ainda sim vai para chat_padrão 
        print("resultado da ferramenta: " + next_action) #problemas no NLU com o modelo sendo meio bugado em pesquisa_web, as vezes fala que é web quando não é 
        
        possible_actions:set[str] = set(["pesquisa_web","busca_questoes", "verifica_resposta"])  #na prod atual o verifica resposta não esta habilitado

        if next_action in possible_actions:
            return next_action
        else:
            return "chat_padrao"
    
    def run_chat(self, input:str)->dict:
        parsed_input = remove_non_en_chars(input) 
        self.current_action: str = self.__classify_input__(parsed_input)
        print("acao atual sendo executada " + self.current_action)
        print(f"memoria do chat antes de rodar prox chain \n {self.chat_memory}  \n\n" )
        if self.current_action == "pesquisa_web": #chain de pesquisa na web e para trazer links
             
             search_engine = GoogleSearch()
             web_prompt_templa = """Você é um tutor conversando com um Aluno.

              Dadas as seguintes partes extraídas de uma pesquisa e uma pergunta do aluno.
              Analise todas as informações da pesquisa, pense passo a passo para dar a resposta mais correta e atualizada possível. De preferencia para informações mais recentes relevantes para o ano de 2023
              SEMPRE  Traga pelo menos 1 link relevante à pergunta/conversa para o aluno, escreva os links para o usuário apenas se ele for diretamente relacionado com o assunto da conversa.
             {context}

             {chat_history}
             aluno: {human_input}
             tutor:""" 

             prompt = PromptTemplate(
                 input_variables=["chat_history", "human_input", "context"], 
                 template=web_prompt_templa
             )
             
             web_search_chain = LLMChain(
                         llm=ChatOpenAI(model = GPT_MODEL_NORMAL_CHAT, temperature=0), 
                         prompt=prompt, 
                         verbose=False,                         
             )

             web_search_result = search_engine.search(input) #no caso da pesquisa do google, caracteres não ascii podem nos ajudar
             parsed_web_search: str = remove_non_en_chars(search_engine.filter(web_search_result)) #remove chars nao em ingles do resultado da busca
             
             messages = ["user: {} \n assistant: {}\n".format(dic['user'], dic['assistant']) for dic in self.chat_memory]  #junta as strings geradas pela lista de memoria no chat em uma unica string
             chat_history_str:str = "".join(messages)
             #print(f"memoria no chat da web é: {output} \n")
             web_search_reponse:dict = web_search_chain({"human_input" : parsed_input, "context": parsed_web_search, "chat_history": chat_history_str }, return_only_outputs=True)           
            
             #print("input_string", chain)
             #print(chain['text'])
             text_response: str = remove_non_en_chars(web_search_reponse['text'])
             return_dict:dict = {"user": parsed_input, "assistant": text_response}         
             self.chat_memory.append({"user": parsed_input, "assistant": text_response})

             return return_dict
             
        elif self.current_action == "busca_questoes":  # chain de pesquisa de questões em docs
            
            answer_to_memory, answer_to_user =  QD.vectorDB_search_questions(parsed_input)
            #print(type(answer_to_memory))
            #print(answer_to_memory)
            answer_to_memory[-1]["context"] = remove_non_en_chars(answer_to_memory[-1]["context"])
            self.chat_memory.append({"user": parsed_input, "assistant": answer_to_memory[-1]["context"]})
            
            return_dict = {"user": parsed_input, "assistant": answer_to_user + "\n\n"}

            return return_dict

        elif self.current_action == "verifica_resposta":  #chain de salvar progresso
            if len(self.chat_memory) == 0: #se nao tiver questao anterior apenas a pergunta do usuario é considerada
                user_answer:str =  f"\n \n aluno: {parsed_input}"
            else:  user_answer:str = self.chat_memory[-1]["assistant"] + f"\n \n aluno: {parsed_input}"  # pega a ultima conversa entre usuario e chatbot, talvez fazer ser as ultimas duas?
            
            save_progress_answer: str = save_progress.handle_user_answer(user_answer)
            save_progress_answer = remove_non_en_chars(save_progress_answer)
            self.chat_memory.append({"user": parsed_input, "assistant": save_progress_answer })
            return_dict = {"user": parsed_input, "assistant": save_progress_answer }

            #print("retornando dict")
           
            return  return_dict
        
        else:  #caso de chat normal com o chatbot
             template:str = self.subjectPrompt +  self.prompt_body 
             prompt = PromptTemplate(
                      input_variables=["chat_history", "human_input"], 
                      template=template
             )
               
             std_llm_chain = LLMChain(
                      llm=ChatOpenAI(model = GPT_MODEL_NORMAL_CHAT, temperature=0), 
                      prompt=prompt, 
                      verbose=False,          
             )

             messages:list = ["user: {} \n assistant: {}\n".format(dic['user'], dic['assistant']) for dic in self.chat_memory]
             chat_history_str:str = "".join(messages) #junta as strings geradas pela lista de memoria no chat em uma unica string
            
             #print(chat_history_str) 
             
             llm_response:dict = std_llm_chain({"human_input" : parsed_input, "chat_history": chat_history_str })
             
             #print(type(llm_response)) # dictionary
            
             text:str = remove_non_en_chars(llm_response['text'])
             self.chat_memory.append({"user": parsed_input, "assistant": text})
             return_dict =  {"user": parsed_input, "assistant": text}
             #print(return_dict)
             
             return return_dict
    
    def current_chat_state(self)->str:
        return self.current_action
    
"""def chat_bot(User_input: str)-> dict:
    Bot_answer = chatInstance.chatModel()
    current_chat_state: str = chatInstance.current_chat_state()
    Bot_Answer["chat_state"] = current_chat_state
    return Bot_Answer  #returns a dictionary"""

"""def load_chat_state(chat_hist:list, chat_meta_data: dict): 
    global subjectPrompt, Memoria
    if len(Memoria) != 0: #limpa a memoria ao carregar um novo chat
     Memoria.clear()
     print("memoria limpa")

    print("\n\n") 
    #print(dict_list)   
    for d in chat_hist:
        Memoria.append(d)  #adiciona na memoria as mensagens antigas
    print(Memoria)
    current_subject = chat_meta_data['subject']
    subjectPrompt= f"você é um tutor que explica de forma didática as matérias {current_subject}  "
    print(subjectPrompt)"""
             
inputUser:str = ""
import gradio as gr
import time

theme = gr.themes.Default(primary_hue="zinc", secondary_hue="amber").set(  
    input_background_fill="#FFFFFF",
    background_fill_primary ="#abdbe3",
    button_primary_background_fill ="#e28743",
    button_primary_border_color_hover="#e28743",
)

block =gr.Blocks(theme=theme)

with block:   #gera block do gradio para o front end 

    chatbot = gr.Chatbot([], elem_id="chatbot").style(height=650)
    msg = gr.Textbox()
    #clear = gr.ClearButton([msg, chatbot])
    submit= gr.Button("Submit")
    initial_chat_hist:list [dict] = []
    chat_bot1 = ChatBot(chat_hist = initial_chat_hist, chat_meta_data={"subject": "Geografia"})

    def user(user_message, history)->tuple[str,str]:
        return "", history + [[user_message, None]]

    def bot(history):
        User_input:str = history[-1][0]
     
        bot_answer_dict:dict = chat_bot1.run_chat(User_input)  #resposta bot é o dictionary com a perguntar do 'user' e a resposta do 'assisten'
        #print(bot_answer_dict)
        bot_answer_str: str = bot_answer_dict['assistant']
        print(bot_answer_str)
        # mem_dict =  self.chat_memory[len(self.chat_memory)-1]
        #print(mem_dict.keys())
        history[-1][1]=  "" #coloca as respostas do chatbot no historico de chat

        for character in bot_answer_str:
            history[-1][1] += character
            time.sleep(0.001)
            yield history  #da uma resposta gradual ao user

    submit.click(user, [msg, chatbot], [msg, chatbot], queue=False).then(
        bot, chatbot, chatbot
    )
     
block.queue()
block.launch(inline=True, height=1000)



   

import os
from langchain.vectorstores import Qdrant
import qdrant_client
from langchain.embeddings.openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv(os.path.join('keys.env'))

#codigo com função de query em um banco de dados de vetores  para ser utilizada pelo código principal para busca questoes do ENEM

QDRANT_COLLECTION:str = "enem2"
CORRECT_ANSWER_SUBSTR: str = "(RESPOSTA)" if QDRANT_COLLECTION == "enem1" else "(RESPOSTA " # a substr da resposta correta mudou de uma coleção para a outra, devido ao codigo de extrair os pdfs do enem mudar
openai_api_key = os.getenv('OPENAI_API_KEY')
model_name = 'text-embedding-ada-002'

embed = OpenAIEmbeddings(  #setando o modelo de embeddings
    model=model_name,
    openai_api_key=openai_api_key
)

client = qdrant_client.QdrantClient(
     url=os.getenv("QDRANT_HOST"),
     api_key=os.getenv('QDRANT_API'), # setando o client qdrant com minha API de host URL
 )

doc_store = Qdrant(  #inicializando objeto de documento_store
    client=client, 
    collection_name = "enem2",
    #collection_name=os.getenv("QD_COLLECTION_NAME"), 
    embeddings=embed,
)

def vectorDB_search_questions(user_input:str)-> tuple[list,str]:  #função a ser chamada para recuperar a questão mais similar
     
     chat_memory_return:list[dict] = [] #lista que guarda a memória do chat, dictionary de 2 keys: contexto do do e input do user 
     raw_docs = doc_store.similarity_search(query=user_input, k=1)  #gera 1 pagina de resultado na busca por documentos
     #print(raw_docs)
     inputs = [{"context": doc.page_content, "user_input": user_input} for doc in raw_docs] #extrai um dictionary dos resultados da busca nos docs
     returned_question:str = inputs[0]['context']   #extrai o texto em si do resultado
     #print(f"returned_question:{returned_question}")   
     if not("(Enem/") in returned_question:
      returned_question  =  " \n (Enem/" + returned_question  #adicionar (Enem/ caso o input não tenha isso  
     
      #vamos pegar a primeira occorencia da substring (RESPOSTA) e criar uma str com a resposta certa para o chatbot e uma sem, para o user

     #talvez tenha que mudar esse buffer
     CORRECT_ANSWER_BUFFER = 45 #buffer para saber o tamanho da string  (RESPOSTA) sempre correta: , precisa ser 45 em certos casos
     correct_answer_substr_index: int = returned_question.find(CORRECT_ANSWER_SUBSTR) #acha o index onde a substr (RESPOSTA) aparece pela primeira vez
     
     question_with_answer:str = returned_question[:(correct_answer_substr_index + CORRECT_ANSWER_BUFFER)] #string com a resposta sempre certa, para memoria do chat
     question_without_answer:str = question_with_answer[:correct_answer_substr_index] #string sem resposta, para o user
           
     chat_memory_return.append({"context": question_with_answer, "UserInput": user_input})     #adiciona o resultado na lista de memória
     #print(f" \n questao mantendo resposta  \n {question_with_answer} \n")
     
     user_return:str = "\n Questão do ENEM: "+ question_without_answer
     #print(user_return)

     return chat_memory_return, user_return  #chat_memory_return é o output para o contexto da IA,user_return é para o usuário


if __name__ == "__main__":
  print("teste")
  memo_chat, user_return =  vectorDB_search_questions("""me de uma questao sobre No poema de Robert Frost, as palavras “fault” e “blame”"""
  )
  print(user_return)
 
# memo_chat, user_return =  vectorDB_search_questions("me de uma questão do enem sobre a historia do brasil")
# print(type(memo_chat[0]))
# print(memo_chat[0]['context'])

import os
from langchain.vectorstores import Qdrant
import qdrant_client
from langchain.document_loaders import TextLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv


#código feito para carregar novos documentos na qdrant cloud

load_dotenv(os.path.join("educa_gpt_publico_cv",'keys.env'))

openai_api_key = os.getenv('OPENAI_API_KEY') or 'OPENAI_API_KEY'
model_name = 'text-embedding-ada-002'



client = qdrant_client.QdrantClient(
     url=os.getenv("QDRANT_HOST"),
     api_key=os.getenv('QDRANT_API'), 
 )


embed = OpenAIEmbeddings(  #setando o modelo de embeddings
    model=model_name,
    openai_api_key=openai_api_key
)

vectors_config = qdrant_client.http.models.VectorParams(size=1536,distance = qdrant_client.http.models.Distance.COSINE)
#configuração dos vetores, método de pesquisa (COSENO) e tamanho dos vetores (1536 é o tam usada pela openAI)


#retur = client.recreate_collection(collection_name=os.getenv("QD_COLLECTION_NAME"), vectors_config=vectors_config)
# essa linha de código serve para criar coleções do zero ou deletar existentes, cuidado ao mecher com ele

doc_store = Qdrant(
    client=client, 
    collection_name=os.getenv("QD_COLLECTION_NAME"), 
    embeddings=embed,
)




#adicionar docs para a vectorstore

def text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(  #objeto de cortar textos do langchain
    chunk_size = 2200, #cada chunk de texto tem no máximo 2200 caracteres, melhor numero que eu testei ate agora
    #mudar entre linux e windows parece resultar em problemas no textspitter, no windows o melhor parece ser 1600 caracteres, e no linux 1800 caracteres
    chunk_overlap  = 0,
    separators=["(Enem/"]  #divide partes do texto ao encontrar essa string, agrupa pedaços de texto entre a occorrencia dessa string
    )

    chunks = text_splitter.split_documents(text)

    return chunks

loader = TextLoader("vector_DB_test/questoes_ling_redu.txt")  #carrega o arquivo txt à ser adicionado
documents = loader.load()

parsed_text = text_chunks(documents)  #extrai pedaços do texto e coloca num array
for i in range(len(parsed_text)):
    parsed_text[i] = parsed_text[i].page_content #extrai o texto em si, antes o texto estavo num obj langchain
    print("\n\n nova questão "+parsed_text[i]+ "\n\n")


#print(type(parsed_text[0]))
#print(parsed_text[0])

#print(doc_store.add_texts(parsed_text)) #adiciona os novos pedaços de texto na doc_store, printar os vetores de return para verificar se deu certo


#print(client.get_collection(collection_name=os.getenv("QD_COLLECTION_NAME")))
#ver a coleção atual e ver se os novos vetores foram realmente adicionados

#ultima vez deu que tinha 38 vectors





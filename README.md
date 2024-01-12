## EducaGPT 


:us:

# Educational Chatbot tailored for Brazilian High School students

## About the project

This project is part of a [research grant program](http://lattes.cnpq.br/2223448141926231) with the  **Brazilian National Council for Scientific and Technological Development (CNPq)** for the **R&D of Artificial Intelligence tech for educational purposes** within the reality of Brazilian High school students.

This projects builds upon the educational capabilities of Large Language Models (ex: GPT-3.5 and GPT-4) for education , while also seeking to **mitigate weaknesses** such as hallucination and lack of knowledge about certain subjects and tests within the **brazilian university admittance standardized test (ENEM)**.

To achieve these results an **LLM application**, using openAI models (gpt-3.5 turbo or gpt-4), along with aditional modules for extra functionality was developed.

The modules in question are:

* **Document retrieval** for ENEM questions,trough a vectorDB (Qdrant) , allowing for students to dissert them with the LLM and train for that test.

* **Internet search** for sources trough Google Search API, so that students can see the sources behind statements made by the LLM.

* **User performance tracker** for use in combination with the questions retriever, so that users can see and track their % of correctly answered questions for each subject.

For identifing which module to use in a certain context a **simpler NLP model for text classification** was created using the **Spacy NLP** library


# Using the project

A currently  functional (but without the user performance tracker) version of the application is available at this [link](https://intellectia.vercel.app/) the back-end of this web aplication is run with the **Heroku PaaS service**, using **containers and web-workers** for deployment of the Python code.

This repo contains a local version of the project, using the Gradio UI library for a simple chat view and functionality

# Running the local version:

# 1) Clone the repository:
```bash
git clone https://github.com/caue-paiva/educa_gpt_publico
```
# 2) Install the dependencies
```bash
pip install -r requirements.txt
```

# 3) Run the main file:
``` bash
python3 mainintegration7.py
```

# 4) Click on the local gradio URL for the chat
ex, on the terminal:
```bash
Running on local URL:  http://127.0.0.1:7860
```

# 5) Start chatting with the LLM 



:brazil:



# Chatbot Educacional personalizado para estudantes do Ensino Médio Brasileiro

## Sobre o projeto

Este projeto faz parte de um [programa de bolsas de pesquisa](http://lattes.cnpq.br/2223448141926231) com o Conselho Nacional de Desenvolvimento Científico e Tecnológico **(CNPq)** do Brasil para a **P&D de tecnologia de Inteligência Artificial para fins educacionais**  dentro da realidade dos estudantes do Ensino Médio Brasileiro.

Este projeto se baseia nas capacidades educacionais de LLMs (ex: GPT-3.5 e GPT-4) para educação, enquanto também procura mitigar fraquezas como alucinação e falta de conhecimento sobre certos assuntos e testes dentro do exame nacional do ensino médio (ENEM).

Para alcançar esses resultados, uma **aplicação com LLM**, usando modelos da openAI (gpt-3.5 turbo ou gpt-4), juntamente com **módulos adicionais para funcionalidade extra foi desenvolvida.**

Os módulos em questão são:

* **Recuperação de documentos para questões do ENEM**, através de um vectorDB (Qdrant), permitindo que os estudantes dissertem com o LLM e treinem para esse teste.

* **Pesquisa na internet** para fontes através da API de Pesquisa do Google, para que os estudantes possam ver as fontes por trás das declarações feitas pelo LLM.

* **Rastreador de desempenho do usuário** para uso em combinação com o recuperador de perguntas, para que os usuários possam ver e acompanhar sua porcentagem de perguntas respondidas corretamente para cada matéria.

Para identificar qual módulo usar em um determinado contexto, um **modelo de NLP/PLN** mais simples para **classificação de texto** foi criado usando a **biblioteca Spacy NLP.**

## Usando o projeto

Uma versão atualmente funcional (mas sem o rastreador de desempenho do usuário) da aplicação está disponível neste [link](https://intellectia.vercel.app/),  o back-end desta aplicação web é executado com a **no serviço de PaaS Heroku**, usando **containers e web-workers** para implantação do código Python.

Este repositório contém uma **versão local do projeto**, utilizando a biblioteca Gradio UI para uma simples visualização de chat e funcionalidade

Executando a versão local:
# 1) Clone o repositório:
```bash
git clone https://github.com/caue-paiva/educa_gpt_publico
```
# 2) Instale as dependências
```bash
pip install -r requirements.txt
```
# 3) Execute o arquivo principal:
```bash 
python3 mainintegration7.py
```
# 4) Clique na URL gradio local para o chat
ex, no terminal:
```bash 
Rodando na URL local:  http://127.0.0.1:7860
```
# 5) Comece a conversar com o LLM







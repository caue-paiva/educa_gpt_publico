import spacy , os

nlp = spacy.load(os.path.join("pt_textcat_demo8-0.0.0/pt_textcat_demo8/pt_textcat_demo8-0.0.0"))


def intent_identi(text:str)->str:
    doc = nlp(text)
    predicted_category = max(doc.cats, key=doc.cats.get)
    arrayProb= []   
    for key in doc.cats:
        arrayProb.append(doc.cats[key])  
    
    proba= float(max(arrayProb))
    print("proba: " + str(proba))
    print(predicted_category)
    if predicted_category == "pesquisa_web":
        if proba < 0.80:
            return "chat_padrao"
        else:
            return predicted_category
        
    elif proba < 0.95:
        return "chat_padrao"
    else: 
        return predicted_category
    



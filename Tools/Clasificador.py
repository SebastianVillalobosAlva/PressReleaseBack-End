from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn import svm
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn import metrics
import pandas as pd
import json
import pickle


# class LemmaTokenizer(object):
#     def __init__(self,nlp):
#         self.spacynlp = nlp

#     def __call__(self, doc):
#         nlpdoc = self.spacynlp(doc)
#         nlpdoc = [token.lemma_ for token in nlpdoc if (len(token.lemma_) > 1) or (token.lemma_.isalnum()) and not token.is_stop ]
#         return nlpdoc

# se importan las bases ya descargadas y se des da el formato correcto


# nlp = spacy.load('es_core_news_md')

print('\n\nLeyendo bases')

ejemplos=pd.read_csv('../Data/Notas_Ejemplos.csv')
c_ejemplos=pd.read_csv('../Data/Notas_Contra_Ejemplos.csv')

ejemplos['etiqueta']=1
c_ejemplos['etiqueta']=0


db=pd.concat([ejemplos,c_ejemplos],ignore_index=True)
db['TitluloTexto']=db.Titulo+". "+db.Texto


db.drop(db[db.Texto.isnull()].index,inplace=True)


print('\n\nCreando Modelo')

# Se divide la base Train Test
X_train, X_test, y_train, y_test = train_test_split(db.Texto, db.etiqueta, test_size=0.33, random_state=42)


# cargar stop words
with open('Stop_Words.json',encoding='utf-8') as json_file:
    stop_words = json.load(json_file)


# Crea pipeline

# Modelo=Pipeline([('tfidf',TfidfVectorizer(tokenizer=LemmaTokenizer(nlp))),('svm',svm.LinearSVC())])
Modelo=Pipeline([('tfidf',TfidfVectorizer(stop_words=stop_words)),('svm',svm.SVC(probability=True))])

print('\n\nEntrenando Modelo')

Modelo.fit(X_train, y_train)

predictions=Modelo.predict(X_test)

print(metrics.confusion_matrix(y_test,predictions))
print(metrics.classification_report(y_test,predictions))

# guardar modelo
salir=False
while(not salir):
    print('\n\nGuardar modelo? (y/n): ')
    respuesta=input()
    if respuesta=='y' or respuesta=='Y':
        print('\n\nNombre de modelo:')
        nombre=input()
        with open(f'../Models/{nombre}.pkl','wb') as file:
            pickle.dump(Modelo,file)
        with open(f'../Models/{nombre}_metrics.txt','w') as file:
            file.write(metrics.classification_report(y_test,predictions))
        salir=True
    elif respuesta=='n' or respuesta=='N':
        salir=True
    else:
        print('\n\n solo se acepta \'s\' o \'n\'')
    



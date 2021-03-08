from flask import Flask, render_template, session, url_for, redirect, jsonify, request
import numpy as np
from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField, TextField 
import joblib
import json
from flask_cors import CORS, cross_origin
##########################
from Tools import Jornada
from Tools import Reforma
import pickle
import datetime
import pandas as pd
import sklearn
import sklearn.pipeline
import sklearn.feature_extraction
import sklearn.utils._cython_blas
import sklearn.neighbors
import sklearn.neighbors._typedefs
import sklearn.tree
import sklearn.tree._utils
import re
    
def Obtener_Prediccion(nota):
    '''
    Returns the classification and probability of a press release as new columns in a pd.DataFrame.

    Parameter
    --------------------------------
    nota: pd.DataFrame 
            Press Release

    Returns
    --------------------------------
    nota: pd:DataFrame 
            Press Release with their classification and probability

    '''
    # Open model
    modelo = None
    with open('Models/Modelo_3.pkl','rb') as f:
        modelo = pickle.load(f)

    # Obtain classification of press release
    if modelo is not None:
        prediccion=modelo.predict(nota.Texto) # Classify as '1' or '0'
        modelo.probability = True
        proba=modelo.predict_proba(nota.Texto) # Obtain probability of their classification

        nota['Prediccion'] = prediccion
        nota['PrediccionEtiqueta'] = 'No'
        nota.loc[nota.Prediccion == 1,'PrediccionEtiqueta']='Si'

        nota['Probabilidad_Si'],nota['Probabilidad_No'] = proba[:,1],proba[:,0] # Append the probabilities as new columns

        # Return press release based on probability
        if proba[0,1]>=.60:
            return nota
        else:
            return None
    
app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'
CORS(app,support_credentials=True)

@app.route("/notas",methods=['POST'])
@cross_origin(support_credentials=True)
def Notes(): 
    # Read json
    data = request.get_json()
    print(data) 
    # Compute the dates for which to download and classify press releases. Increment of one day per date
    fechas = pd.date_range(start=data['fecha_i'],end=data['fecha_f'])
    print(fechas)
    # Create pd.DataFrame where to store all press releases that have >= 60% probability of being useful
    notas = pd.DataFrame(data = None, columns= ['Titulo','Autor','Referencia','Texto','link','Prediccion','PrediccionEtiqueta','Probabilidad_Si','Probabilidad_No'])
    notas_lista = []

    for idx,date in enumerate(fechas):
        i = 0
        # Obtain year, month and day for which to download press releases
        year = int(fechas[idx].year)
        month = int(fechas[idx].month)
        day = int(fechas[idx].day)

        if(data['Jornada'] & data['Reforma']):
            print('Jornada y Reforma')
        elif(data['Jornada'] & ~data['Reforma']):
            
            print('Jornada')
            links = Jornada.ObtenLinks(day,month,year) # Obtain all the links from La Jornada
            print('Bajando links')
            
            for link in links:
                # Download press release individually and classify them
                print("Descargando nota:",i)
                notaJ = Jornada.DescargaNotas(link,True) 
                notaJ = Obtener_Prediccion(notaJ)
                
                if notaJ is not None:
                    notas_lista.append(notaJ)
                i += 1
               
                if i > 15:
                    break
                
        elif(~data['Jornada'] & data['Reforma']):
            
            print('Reforma')
            folios = Reforma.getFoliosDia(day,month,year) # Obtain all the links from Reforma
            print('Bajando links')

            for folio in folios:
                # Download press release individually and classify them
                print("Descargando nota:",i)
                notaR = Reforma.NotasReforma(folio,True)
                notaR = Obtener_Prediccion(notaR)

                if notaR is not None:
                    notas_lista.append(notaR)
                i += 1
               
                if i > 15:
                    break
              
    if not notas_lista:
        return "No hay notas que cumplan con la mínima probabilidad"

    notas = pd.concat(notas_lista)
    notas.drop(notas[notas.Texto.isnull()].index,inplace=True)
    notas_json = notas[['Titulo','Autor','link','Probabilidad_Si','Probabilidad_No']].to_json(orient='split')

    return notas_json

if __name__ == '__main__':
    app.run()
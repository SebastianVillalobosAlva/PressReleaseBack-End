# Se importan librerias de manera explicita para poder generar un ejecutable
from Tools import Jornada
from Tools import Reforma
import pickle
import datetime
import pandas as pd
import sklearn
import sklearn.pipeline
import sklearn.feature_extraction
import sklearn.utils._cython_blas
import sklearn.neighbors._typedefs
import sklearn.tree
import sklearn.tree._utils
 
from os import system, name 
import re

# define our clear function 
def clear(): 
  
    # for windows 
    if name == 'nt': 
        _ = system('cls') 
  
    # for mac and linux(here, os.name is 'posix') 
    else: 
        _ = system('clear') 

# Valida el format de la fecha y que sea una fecha valida
def validaFecha(str_fecha):
    try:
        date = datetime.datetime.strptime(str_fecha, '%Y-%m-%d')
        return date
    except ValueError:
        return False
    

hoy = datetime.datetime.now()

fecha = hoy.strftime('%Y-%m-%d')

Header = f'''
###############################################################
#                                                             #
#                                                             #
#          Bienvenido al Seleccionador de Notas               #     
#                                                             #
#                                                             #
###############################################################

Para descagar las notas de hoy ({fecha}) presiona ENTER,

para descargar otra fecha ingrésala en el formato AAAA-MM-DD.

Ingresa la fecha: '''

clear()

print(Header)


while True:
    respuesta = input()

    respuesta = respuesta.strip()

    if respuesta == '':
        break
    else:
        aux_fecha = validaFecha(respuesta)
        if aux_fecha is not False and aux_fecha <= hoy:
            fecha = aux_fecha.strftime('%Y-%m-%d')
            break
        else:
            print('\nERROR: Ingresa una fecha valida en el formato AAAA-MM-DD. \n\nIngresa la fecha:')

print(f'\nDescargando noticias del día: {fecha} ...\n\n')



datos_fecha=fecha.split('-')

year = int(datos_fecha[0])
month = int(datos_fecha[1])
day = int(datos_fecha[2])



print('Descargando notas Jornada...')
print('\nObteniendo Links de Jornada...')
links = Jornada.ObtenLinks(day,month,year)
notas = Jornada.DescargaNotas(links,True)




print('\n\nDescargando notas Reforma...')
print('\nObteniendo Folios Reforma...')
folios = Reforma.getFoliosDia(day,month,year)
notasReforma = Reforma.NotasReforma(folios,True)



notas = notas.append(notasReforma, ignore_index=True)

# notas.to_excel(f'Notas_{fecha}.xlsx')
# notas= pd.read_excel('Notas_2020_10_20.xlsx')

notas.drop(notas[notas.Texto.isnull()].index,inplace=True)



print('\n\nCargando Modelo...')

modelo = None
with open('Models/Modelo_3.pkl','rb') as f:
    modelo = pickle.load(f)


if modelo is not None:
    print('\n\nHaciendo Prediccion...')
    prediccion=modelo.predict(notas.Texto)
    modelo.probability = True
    proba=modelo.predict_proba(notas.Texto)

    # print(proba)
    notas['Prediccion'] = prediccion
    notas['PrediccionEtiqueta'] = 'No'
    notas.loc[notas.Prediccion == 1,'PrediccionEtiqueta']='Si'

    notas['Probabilidad_Si'],notas['Probabilidad_No'] = proba[:,1],proba[:,0]

    notas = notas.sort_values(by=['Prediccion','Probabilidad_Si'],ascending=False)
    


    print('\n\nGuardando Resultados...')

    notas[['Titulo','Autor','Referencia','Texto','link','Prediccion','PrediccionEtiqueta','Probabilidad_Si','Probabilidad_No']].to_excel(f'Predicciones_{fecha.replace("-","_")}.xlsx',index=False)


else:
    print('Error: No se pudo cargar modelo.')


print('\n\nPresiona enter para terminar.')
input()
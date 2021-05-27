import pickle
from Tools import Jornada, Reforma
import pandas as pd

def Obtener_Prediccion(nota, periodico):
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

        if(periodico == 0):
            nota['Periodico'] = "Reforma"
        else:
            nota['Periodico'] = "La Jornada"

        nota['P_Si'],nota['P_No'] = proba[:,1],proba[:,0] # Append the probabilities as new columns

        # Return press release based on probability
        if proba[0,1]>=.15:
            return nota
        else:
            return None
        # return nota

def GuardarEnBase(nota,Nota,db):
    nota_existe = Nota.query.filter_by(Link = nota.link.str.encode("utf-8")).first() 
    if not nota_existe: 
        # try: 
            # print("Creando la nota")
            # # creating Users object 
            # user = Nota( 
            #     Titulo = nota.Titulo.str.encode("utf-8"),
            #     Autor = nota.Autor.str.encode("utf-8"),
            #     Texto = nota.Texto.str.encode("utf-8"),
            #     Link = nota.link.str.encode("utf-8"),
            #     P_Si = float(nota.Probabilidad_Si),
            #     P_No = float(nota.Probabilidad_No)
            #     ) 
            # print("\n Se creo la nota")
            # print(user)
            # # adding the fields to users table 
            # db.session.add(user) 
            # print("\n Se agregó la nota")
            # db.session.commit() 
            # # db.session.flush()
            # print("\n Se guardó en la base de datos")
        return True

        # except:
    else:
            # db.session.rollback() 
            # print("\n No se guardó en la base de datos")
        return False

def Bajar_Notas(data,Nota,db,engine):
     # Compute the dates for which to download and classify press releases. Increment of one day per date
    fechas = pd.date_range(start=data['fecha_i'],end=data['fecha_f'])
    print(fechas)
    # Create pd.DataFrame where to store all press releases that have >= 60% probability of being useful
    notas = pd.DataFrame(data = None, columns= ['Titulo','Autor','Referencia','Texto','link','Prediccion','PrediccionEtiqueta','P_Si','P_No','Periodico'])
    notas_lista = []

    for idx,date in enumerate(fechas):
        i = 0
        # Obtain year, month and day for which to download press releases
        year = int(fechas[idx].year)
        month = int(fechas[idx].month)
        day = int(fechas[idx].day)

        if(data['Jornada'] & data['Reforma']):

            print('Jornada y Reforma')
            links = Jornada.ObtenLinks(day,month,year)
            folios = Reforma.getFoliosDia(day,month,year)
            print("Obteniendo link de Jornada y Reforma")

            f = 0
            l = 0
            while((f < len(folios)) and (l < len(links))):
                print('Descargando nota {} de Jornada'.format(l))
                notaJ = Jornada.DescargaNotas(links[l],True) 
                notaJ = Obtener_Prediccion(notaJ, 1)
                if notaJ is not None:
                    existJ = GuardarEnBase(notaJ,Nota,db)
                    if existJ:
                        notas_lista.append(notaJ)

                print('Descargando nota {} de Reforma'.format(f))
                notaR = Reforma.NotasReforma(folios[f],True)
                notaR = Obtener_Prediccion(notaR, 0)
                if notaR is not None:
                    existR = GuardarEnBase(notaR,Nota,db)
                    if existR:
                        notas_lista.append(notaR)
                
                if (l < len(links)):
                    l += 1

                if (f < len(folios)):
                    f += 1
                
                # if f > 15 or l > 15:
                #     break

        elif(data['Jornada'] & ~data['Reforma']):
            
            print('Jornada')
            links = Jornada.ObtenLinks(day,month,year) # Obtain all the links from La Jornada
            print('Bajando links')
            
            for link in links:
                # Download press release individually and classify them
                print("Descargando nota:",i)
                notaJ = Jornada.DescargaNotas(link,True) 
                notaJ = Obtener_Prediccion(notaJ, 1)
                
                if notaJ is not None:
                    exist = GuardarEnBase(notaJ,Nota,db)
                    if exist:
                        notas_lista.append(notaJ)

                i += 1
               
                # if i > 30:
                #     break
                
        elif(~data['Jornada'] & data['Reforma']):
            
            print('Reforma')
            folios = Reforma.getFoliosDia(day,month,year) # Obtain all the links from Reforma
            print('Bajando links')

            for folio in folios:
                # Download press release individually and classify them
                print("Descargando nota:",i)
                notaR = Reforma.NotasReforma(folio,True)
                notaR = Obtener_Prediccion(notaR, 0)

                if notaR is not None:
                    # notaR.to_sql(name='notasguardadasV2')
                    exist = GuardarEnBase(notaR,Nota,db)
                    if exist:
                        notas_lista.append(notaR)
                i += 1
               
                # if i > 15:
                #     break
              
    if not notas_lista:
        return "No hay notas que cumplan con la mínima probabilidad"

    notas = pd.concat(notas_lista)
    notas.drop(notas[notas.Texto.isnull()].index,inplace=True)
    # notas[['Titulo', 'Autor', 'Texto','link','P_Si', 'P_No']].to_sql(name="notasguardadasV2", if_exists='append', con=engine, index=False)
    notas = notas.drop_duplicates()
    notas_json = notas[['Titulo','Autor','link','P_Si','P_No']].to_json(orient='split')
    print(len(notas))
    notas[['Titulo', 'Autor', 'Texto','link','P_Si', 'P_No']].to_sql(name="notasguardadasv2", if_exists='append', con=engine, index=False)

    return notas_json   

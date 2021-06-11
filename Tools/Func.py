import pickle
from Tools import Jornada, Reforma
import pandas as pd
from fpdf import FPDF

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

def Bajar_Notas(data):
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
    notas_p=notas[['Titulo','Autor','Referencia','link','Prediccion','PrediccionEtiqueta','P_Si','P_No','Texto']]
    renglones=notas_p.shape[0]
    columnas=notas_p.shape[1]
    c_n_l=list(notas_p.columns)
    i=0
    p=0
    enunciado=""
    for renglon in range(0,renglones):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('arial', 'B', 14)
        pdf.cell(0, 8, 'Notas',0,2,align='C')
        pdf.set_font('arial', 'B', 8)
        for column in c_n_l:
            if not column=='Texto':
                pdf.cell(0,10,column+': '+str(notas_p[column].iloc[i]),0,2,align='C')
            if column=='Texto':
                pdf.add_page()
                pdf.cell(0,11,'Texto',0,2,align='C')
                pdf.set_font('arial', 'B', 9)
                articulo=str(notas_p['Texto'].iloc[i])
                pdf.multi_cell(0,10,articulo,0,0)
            #     pdf.image("C://Users/Dell/Downloads/PressReleaseBack-End-Isra/PressReleaseBack-End-Isra/screenshot.png",type='PNG')
                    
        name="report_"+str(notas_p['Titulo'].iloc[i])+".pdf"
        pdf.output(name, 'F')
        i=i+1
    notas_json = notas[['Titulo','Autor','link','P_Si','P_No']].to_json(orient='split')
    print(len(notas))
    notas[['Titulo', 'Autor', 'Texto','link','P_Si', 'P_No']].to_sql(name="notasguardadasv2", if_exists='append', con=engine, index=False)

    return notas_json   

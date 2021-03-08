import pandas as pd
import Jornada

baseLinks=pd.read_excel('Catálogo_Notas.xlsx').fillna('')

notasJornada=baseLinks[baseLinks['Link de la nota'].str.contains('jornada')]
linksNotas=notasJornada['Link de la nota'].tolist()


print('\nDescargando Notas...')
notasDescargadas=Jornada.DescargaNotas(linksNotas)

print('\nGuardando Notas')
notasDescargadas.to_csv('Notas_Ejempos.csv')
# print(notasDescargadas)

notasJornada['Fecha']=notasJornada.Dia.astype(str)+'_'+notasJornada.Mes.astype(str)+'_'+notasJornada.Año.astype(str)

fechas=notasJornada.Fecha.unique()

print('\nDescargando Notas contra ejemplo...')
links_ejemplos=set(linksNotas)
contraEjemplos=None
for f in fechas:
    dia,mes,año=f.split('_')
    try:    
        dia=f'{float(dia):02.0f}'
        mes=f'{float(mes):02.0f}'
        año=f'{float(año):04.0f}'
    except:
        continue
    # print(dia)
    links=Jornada.ObtenLinks(dia,mes,año)
    links_contra=list(set(links)-links_ejemplos)

    if not len(links)==len(links_contra):
        Notas_contra=Jornada.DescargaNotas(links_contra)
        if contraEjemplos is None:
            contraEjemplos=Notas_contra
        else:
            contraEjemplos=contraEjemplos.append(Notas_contra,ignore_index=True)
        # print(contraEjemplos)


contraEjemplos.to_csv('Notas_contra_ejemplos.csv')
import pandas as pd
from datetime import date
import Reforma
 
folio='1879279'
folio='1879488'

folioInt=int(folio)

data = pd.read_csv('Titulos_Completo.csv',encoding= 'unicode_escape') 
listaTitulos= pd.DataFrame(data)
total_rows = listaTitulos.count()
#print (total_rows +1)

contadorNulos=0;
flagFinal=0;
i=1;
folioTemp=folioInt;
contadorEncontrados=0;
flagEncontrado=0;
articulos={'Titulo':[],'Autor':[],'Referencia':[],'Texto':[],'link':[]}
print("Ejecutando...")
while flagFinal == 0:
	folioUrl=folioInt+i
	i=i+1
	url=Reforma.CrearUrl(str(folioUrl))
	nota=Reforma.DescargarNota(url)
	if nota["titulo"]=="None":
		contadorNulos=contadorNulos+1
	else:
		if nota["titulo"]!="Error de conexión":
			contadorNulos=0
			folioTemp=folioUrl
			for index, row in listaTitulos.iterrows():
				busquedaTitulo=row['Titulos']
				if nota["titulo"]==busquedaTitulo:
					flagEncontrado=1;
			if flagEncontrado!=1:
				contadorEncontrados=contadorEncontrados+1;
				print("Encontrado")
				#print (total_rows)
				articulos['Titulo'].append(nota["titulo"])
				articulos['Autor'].append(nota["autor"])
				articulos['Referencia'].append(nota["resumen"])
				articulos['Texto'].append(nota["contenido"])
				articulos['link'].append(url)
				print(nota["titulo"]+" -> "+nota["fechaSubida"]+" -> "+str(folioUrl))
				print(folioTemp)
				print("-------------------------------------------------------------------------------------------------")
			flagEncontrado=0

	if contadorNulos>=50:
		flagFinal=1
	if nota["titulo"]=="Error de conexión":
		flagFinal=1;
		folioTemp=folioUrl-1
	if contadorEncontrados>=2000:
		flagFinal=1;

df=pd.DataFrame(articulos)
df.to_csv('Notas__Contra_Ejemplos_Reforma.csv', encoding='latin1')
print(df)
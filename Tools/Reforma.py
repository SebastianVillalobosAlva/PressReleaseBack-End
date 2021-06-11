#Web-Scrapping Reforma

def getFoliosHoy():
	# se obtiene la fecha actual y se llama get folios dia
	import datetime

	ahora = str(datetime.datetime.now())
	datosahora = ahora.split()
	fecha = datosahora[0].split('-')
	dia = int(fecha[2])
	mes = int(fecha[1])
	year = int(fecha[0])

	return getFoliosDia(dia,mes,year)

def getFoliosDia(dia,mes,year):
	# Obtiene el xml del reforma para obtener el folio de todas las notas del dia
	import datetime
	import xml.etree.ElementTree as ET
	import requests

	secciones = ['primera','avisos','nacional','editoriales','internacional','ciudad','cancha','gente','cultura','automotriz','moda','thenewyorktimes','buenamesa','primerafila','club','spot','vida','revistar','deviaje','bienesraices','murosocialdomingo','redcarpet','campanas','gadgets','grandprixdeeifel','cheforopeza','porunavisionsana','impulsosestadodemexico','chinahoy','centralmunicipal','tendencias','probonoenmexico','universitarios','covid19prevencionycuidado','bienesinmuebles','grandprixrusia','opcionesacademicas','audicion','gadgetslarevista','entremuros','inversiones','edomex','nfl2020','grandprixtoscana','verdeideassustentables','podium']
	urlBase = 'https://www.reforma.com/libre/online07/paginas/'

	diaActual = datetime.date.today()
	diaRecibido = datetime.date(year,mes,dia)

	if diaRecibido > diaActual:
		return []

	delta = diaActual - diaRecibido
	if delta.days > 6:
		urlBase = 'https://hemerotecalibre.reforma.com/'

	folios = []

	for seccion in secciones:
		url = f'{urlBase}{year}{mes:02}{dia:02}/secciones/{seccion.upper()}.XML'
		r = requests.get(url)
		inicio = r.text.index('<?xml version="1.0"')
		try:
			xml = ET.fromstring(r.text[inicio:])
			if xml.tag == 'Error':
				continue

			for pagina in xml.iter('pag'):
				pag = pagina.attrib['num']
				for nota in pagina.iter('nota'):
					folio = nota.attrib['folio']
					if folio !='0':
						folios.append((folio,pag))
		except:
			pass
	
	return folios

	
def NotasReformaHoy(verbose=False):
	if verbose:
		print('Obteniendo Folios.')
	folios = getFoliosHoy()
	NotasReforma(folios,verbose)

def NotasReforma(folio,verbose=False):
	import pandas as pd
	import datetime 

	articulos={'Titulo':[],'Autor':[],'Referencia':[],'Texto':[],'link':[]}
	
	hoy = datetime.datetime.now()
	fecha = hoy.strftime('%Y %m %d')
	folio_, pagina = folio
	url=CrearUrl(folio_)

	nota=DescargarNota(url)

	if nota["titulo"]!="None" or nota["titulo"]!="Error de conexión":
		articulos['Titulo'].append(nota["titulo"])
		articulos['Autor'].append(nota["autor"])
		articulos['Referencia'].append(f'Periódico Reforma {fecha}, p.{pagina}')
		articulos['Texto'].append(nota["contenido"])
		articulos['link'].append(url)
			
	df=pd.DataFrame(articulos)
	return df

def CrearUrl(folio):
	url='https://www.reforma.com/libre/online07/aplicacionEI/webview/iWebView.aspx?Coleccion=1066&folio='+folio+'&TipoTrans=8'
	return url

def DescargarNota(link):
	from bs4 import BeautifulSoup
	import requests
	import re

	try:
		source = requests.get(link).text
	except:
		nota = {
					"titulo": "Error de conexión",		
					"fechaSubida": "None",
					"resumen": "None",
					"autor": "None",
					"seccion": "None",
					"contenido": "None"
				}
		return nota

	soup = BeautifulSoup(source, 'html.parser')

	titlulo = soup.title.text if soup.title is not None else ''

	if soup.title == None or titlulo == 'Grupo Reforma - PÃ¡gina No Encontrada':
		nota = {
					"titulo": "None",		
					"fechaSubida": "None",
					"resumen": "None",
					"autor": "None",
					"seccion": "None",
					"contenido": "None"
				}
		return nota
	
	patronFecha= re.compile(r'\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d')   
	patronSeccion= re.compile(r'var NombreSeccion = (.*);')     
	scripts = soup.find_all("script")
	try:
		fechaSubida=patronFecha.findall(source)[0]
	except:
		# print(link)
		fechaSubida="0000-00-00 00:00:00"
	try:
		NombreSeccion=patronSeccion.search(source)
		x = re.split("\s", NombreSeccion.group())
		tempSeccion=x[3].replace('\'','')
		NombreSeccion=tempSeccion.replace(';','')
		#print(NombreSeccion)
	except:
		NombreSeccion="None"
		#print("No Encontrada")
	
	
	match = soup.find('div', id = 'divTituloNota')
	titulo =  match.text
	#print(titulo)

	match = soup.find('div', style = 'font-style:italic')
	resumen =  match.text
	#print(resumen)

	match = soup.find('div', class_ = 'autor')
	autor =  match.text
	#print(autor)

	contenido=""
	for match in soup.find_all('p'):
		contenido =  contenido+match.text+"\n"
	#print(contenido)
	
	nota = {
		"titulo": titulo,		
		"fechaSubida": fechaSubida,
		"resumen": resumen,
		"autor": autor,
		"seccion": NombreSeccion,
		"contenido": contenido
	}
	return nota

import datetime
import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import requests
import pandas as pd
import time



def ObtenLinksDiarios():
	#Esta funcion va a regresar una lista de los links de las notas del dia actual
	#variable fecha
	ahora = str(datetime.datetime.now())
	datosahora = ahora.split()
	fecha = datosahora[0].split('-')
	dia = int(fecha[2])
	mes = int(fecha[1])
	year = int(fecha[0])
	return ObtenLinks(dia,mes,year)

def ObtenLinks(dia,mes,year):
	#Esta funcion va a regresar una lista de los links de las notas del dia deseado
	secciones=['edito','opinion','correo','politica','economia','mundo','estados','capital','ciencias','cultura','espectaculos','deportes']
	links =list()
	#request por seccion del dia
	for i in range(len(secciones)) :
	    urldia = F'https://www.jornada.com.mx/{year}/{mes:02}/{dia:02}'
	    url = urldia+'/'+secciones[i]
	    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})

	    web_byte = urlopen(req).read()
	    webpage = web_byte.decode('utf-8')

	    soup = BeautifulSoup(webpage, 'html.parser')

	    # Retrieve all of the anchor tags
	    tags = soup('a')
	    for tag in tags:
	        tagstring = str(tag.get('href', None))
	        if not tagstring.startswith(secciones[i]): continue
	        link = urldia+'/'+tagstring
	        links.append(link)
			
	return list(dict.fromkeys(links))

def DescargaNotasDiarias(imprime=False):
	links = ObtenLinksDiarios()
	return DescargaNotas(links,imprime=imprime)

def DescargaNotas(link,imprime=True):
	#esta regresa una tabla de panadas con todos los articulos que se pasen en un arreglo
	#Titulo,autor,fecha,Articulo
	articulos={'Titulo':[],'Autor':[],'Referencia':[],'Texto':[],'link':[]}
	n=0
	r=requests.get(link)
	soup=BeautifulSoup(r.content,'html.parser')
		
	bloque_titulo=soup.find('div',{'class':'cabeza'})
	titulo=bloque_titulo.text if bloque_titulo is not None else ''

	bloque_autor=soup.find('div',{'class':'credito-articulo'})

	autor=bloque_autor.span.text if bloque_autor is not None else ''

	bloque_articulo=soup.find('div',{'id':'article-text'})
		
	if bloque_articulo is not None:
		bloque_ref=bloque_articulo.find('div',{'class':'hemero'})
			
		ref=bloque_ref.text if bloque_ref is not None else ''

		texto_articulo=''
			
		inicial=bloque_articulo.find('div',{'class':'inicial'})
		texto_articulo+=inicial.text if inicial is not None else ''
			

		for parrafo in bloque_articulo.find_all('p'):
			texto_articulo+=parrafo.text+'\n'

		articulos['Titulo'].append(titulo)
		articulos['Autor'].append(autor)
		articulos['Referencia'].append(ref)
		articulos['Texto'].append(texto_articulo)
		articulos['link'].append(link)
	
	
	return pd.DataFrame(articulos) 


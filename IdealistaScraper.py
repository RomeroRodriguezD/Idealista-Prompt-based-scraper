import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
import random
import time
import xlwt
import re

def scrapear():

    # Lista para reemplazar acentos.
    replacement_chars = {'à':'a', 'á':'a', 'è':'e', 'é':'e', 'í':'i', 'ì':'i', 'ó':'o', 'ò':'o', 'ú':'u', 'ù':'u'}
    # Semáforos
    naves_flag = False
    locales_flag = False
    # Parámetros de búsqueda
    ciudad = str(input('¿De qué ciudad quieres scrapear?')).lower()
    ciudad = ciudad.replace(" ", "-")
    provincia = str(input('¿De qué provincia es? ')).lower()
    inmueble = int(input('¿Qué tipo de inmueble quieres buscar?\nIntroduce el número asociado.\n(0) Viviendas\n(1) Habitaciones\n(2) Naves\n(3) Locales\n(4) Trasteros\n(5) Garajes\n(6) Terrenos.\n'))
    # Asigna el parámetro inmueble a la URL.
    if inmueble == 0:
      inmueble = 'viviendas'
    elif inmueble == 1:
      inmueble == 'habitaciones'
    elif inmueble == 2:
      inmueble == 'locales'
      naves_flag = True
    elif inmueble == 3:
      inmueble = 'locales'
      locales_flag = True
    elif inmueble == 4:
      inmueble = 'trasteros'
    elif inmueble == 5:
      inmueble = 'garajes'
    elif inmueble == 6:
      inmueble = 'terrenos'

    regimen = int(input('¿De alquiler (0) o venta (1)? Introduce el número correcto.'))
    # Asigna el parámetro régimen a la URL.
    if regimen == 1:
      regimen = 'venta'
    else:
      regimen = 'alquiler'
      # Quita los acentos. En IDE se puede usar el módulo unicodedata, en Google Colab no.
    for letra, reemplazo in replacement_chars.items():
      ciudad = ciudad.replace(letra, reemplazo)
      provincia = provincia.replace(letra, reemplazo)

    headers = {
        'Host':'www.idealista.com',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
        'Connection': 'keep-alive',
        'DNT': '1',
        'Host': 'www.idealista.com',
        'Sec-Fetch-Dest': 'document',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/101.0'}


    headers = {k: str(v).encode("utf-8") for k, v in headers.items()}  # Encode en UTF-8

    # Data that will be on the output dataframe

    precios = []
    calles = []
    enlaces = []
    descripciones = []
    media = []
    moda = []
    metros_finales = []
    # media_m2 = [] De momento descartada
    siguiente = True
    pagina = 1
    letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']


    while siguiente:
        time.sleep(random.randint(3,7))
        base_url = f"https://www.idealista.com/{regimen.lower()}-{inmueble}/{ciudad.lower()}-{provincia.lower()}/pagina-{pagina}.htm?ordenado-por=precios-asc"
        if naves_flag:
          base_url = f"https://www.idealista.com/{regimen.lower()}-{inmueble}/{ciudad.lower()}-{provincia.lower()}/con-naves/pagina-{pagina}.htm?ordenado-por=precios-asc"
        if locales_flag:
          base_url = f"https://www.idealista.com/{regimen.lower()}-{inmueble}/{ciudad.lower()}-{provincia.lower()}/con-locales/pagina-{pagina}.htm?ordenado-por=precios-asc"
        print(base_url)
        web = requests.get(base_url, headers=headers)
        time.sleep(0.2)
        soup = bs(web.content, 'html.parser')
        precio = soup.findAll("span", attrs={"class", "item-price h2-simulated"})
        calle = soup.findAll("a", attrs={"class", "item-link"})
        enlace = soup.findAll("a", attrs={"class", "item-link", "href", "/inmueble*"})  # Enlace del inmueble
        descrip = soup.findAll("div", attrs={"class", "item-description description"})
        metros = soup.findAll("span", attrs={"class", "item-detail"})
        seguir = soup.findAll("li", attrs={"class", "next"}) #a, icon-arrow-right-after


        if len(seguir) == 0:  # If there's no next page, it stops the loop.

            siguiente=False

        #print(seguir)
        print(f"Vuelta {pagina}") # Page check

        for i in precio:  # First converts the price into string, removes dots, then it converts it into a float.
            new_precio = str(i.contents[0])
            new_precio2 = new_precio.replace(".", "")
            new_precio2 = float(new_precio2)
            precios.append(new_precio2)

        for j in calle:
            new_calle = str(j.contents)
            calles.append(new_calle)

        for p in enlace:
            new_enlace = "https://www.idealista.com"
            new_enlace += str(p['href'])
            enlaces.append(new_enlace)

        for result in descrip:  # If it does not find any description, adds a default row to make the data rows match.

            try:
                meaning = result.find(class_="ellipsis")
                descripciones.append(meaning.text)

            except:
                descripciones.append("Sin descripción")

        # Cleans useless symbols from descriptions.

        signo1 = "["
        signo2 = "]"
        calles = [s.replace(signo1, "") for s in calles]
        calles = [s.replace(signo2, "") for s in calles]

        try:   #Makes corrections on description content, if there's no description, it just pass.

            for i in descripciones:
                descripciones = [s.replace(signo1, "") for s in descripciones]
                descripciones = [s.replace(signo2, "") for s in descripciones]
                descripciones = [s.replace('\\n', "") for s in descripciones]

        except:
            pass

        # Loop to get m2 tag. Double loop since it needs to be separated from useless data inside "metros".


        meses = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic']

        '''for item in metros:
            for i in item:
                if "," in i:
                    metros.remove(item)'''

        for item in metros:
            print(item)
            new_item = str(item)
            if '€' in new_item:
                metros.remove(item)

        for item in metros:  # Eliminar items con fechas que tienen también 6 carácteres:
            for i in item:
                if "jun" in i:
                    metros.remove(item)
                elif "may" in i:
                    metros.remove(item)
                elif "jul" in i:
                    metros.remove(item)
                elif "ago" in i:
                    metros.remove(item)
                elif "sep" in i:
                    metros.remove(item)
                elif "abr" in i:
                    metros.remove(item)

        for item in metros:
            cuenta=1
            for i in item:

                item2 = str(i).strip(' ') #Strip spaces from each "item-detail"
                item2 = str(item2.strip('.'))
                item2 = str(item2.strip(','))
                if len(item2) <=10: # If it has 3 numbers its a valid m2 value.
                    metros_finales.append(item2)
                elif len(item2)==2:
                   # if int(item2)>25:
                    metros_finales.append(item2)
                break
        pagina += 1

    #Mean and mode for prices. Then, converted to dataframe.

   # mediahecha = round(statistics.mean(precios), 2)
    #modahecha = statistics.mode(precios)
    # Append to lists
    #media.append(mediahecha)
    #moda.append(modahecha)

    #metros_media = round(statistics.mean(metros_finales))
    #media_m2.append(metros_media)
    #media_m2frame = pd.DataFrame({'Media m2':media_2})
    # Makes them a DataFrame
    modaframe = pd.DataFrame({'Moda': moda})
    mediaframe = pd.DataFrame({'Media': media})
    # Resets index.
    modaframe = modaframe.reset_index()
    mediaframe = mediaframe.reset_index()
    # Turns m2 into a DataFrame
    metros_frame = pd.DataFrame({'m2':metros_finales})
    metros_frame.reset_index()
    #Crafts the main dataframe
    viviendas = pd.DataFrame({'Precio': precios, 'Calle': calles, 'Enlace': enlaces, 'Descripciones':descripciones})
    viviendas.reset_index()
    # Crafts the final DataFrame with all the previous ones merged, turns it into a .xls
    viviendas_finales = [viviendas, metros_frame]
    archivo_viviendas = pd.concat(viviendas_finales, axis=1)
    #del archivo_viviendas['index'] #Deletes index column
    archivo_viviendas.to_excel(f'{str(ciudad)}{str(inmueble)}{str(regimen)}Totales.xls')

if __name__ == '__main__':

  scrapear()

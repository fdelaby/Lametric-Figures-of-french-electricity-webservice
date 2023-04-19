from fastapi import FastAPI
import requests
from datetime import timedelta, timezone;
import datetime
from bs4 import BeautifulSoup
import pytz
import urllib.parse
import json


app = FastAPI()
url = "https://eco2mix.rte-france.com/curves/eco2mixWeb?"
urlproductionmix = "https://www.rte-france.com/themes/swi/xml/power-production-fr.xml"

app.last_refresh = datetime.datetime(2022, 10, 2, 00, 00, 00)

app.co2 = "0"
app.nuke = "0"
app.coal = "0"
app.gaz = "0"
app.fuel = "0"
app.hydro = "0"
app.wind = "0"

app.liste_comsumption = []



@app.on_event('startup')
async def init_data():
    print("init call")
    app.liste_comsumption.append(0)




@app.get("/all")
def hello():
    calledXml = False
    tz_fr= pytz.timezone('Europe/Paris')

    date_trigger = tz_fr.localize(app.last_refresh + timedelta(minutes=15))
    # date_trigger = date_trigger.replace(tzinfo=timezone.utc).astimezone(tz=None)

    current_date = datetime.datetime.now(tz_fr)
    datejour = current_date.strftime("%d/%m/%Y")

    if ( current_date > date_trigger):
        calledXml = True
        paramsUrl = {'type': 'conso', 'dateDeb': datejour, 'dateFin': datejour, 'mode':'NORM'}
        document = requests.get(url + urllib.parse.urlencode(paramsUrl),verify=False)

        soup= BeautifulSoup(document.content,"lxml-xml")

        refresh_date = soup.find('date_actuelle').text
        print (str(refresh_date))
        print (str(date_trigger))
        # params["last_refresh"] = datetime.datetime.strptime(str(refresh_date), '%Y-%m-%d %H:%M:%S')
        app.last_refresh = datetime.datetime.strptime(str(refresh_date), '%Y-%m-%d %H:%M:%S')
        types = soup.findAll('type')

                        
        for tipe in types:
            if str(tipe['v']) == 'Consommation':
                valeurs = tipe('valeur')
                size_tab = len(valeurs)
                if (size_tab != 0):
                    if (size_tab > 10):
                        size_tab = 10
                    app.liste_comsumption = []
                    for i in range(1,size_tab+1):
                        indice = i * -1
                        print(str(valeurs[indice].text))
                        app.liste_comsumption.append(int(str(valeurs[indice].text)))
        
        app.liste_comsumption.reverse()

        paramsUrl = {'type': 'co2', 'dateDeb': datejour, 'dateFin': datejour, 'mode':'NORM'}
        document = requests.get(url + urllib.parse.urlencode(paramsUrl),verify=False)
        soup= BeautifulSoup(document.content,"lxml-xml")
        types = soup.findAll('type')

        for tipe in types:
            if str(tipe['v']) == 'Taux de Co2':
                valeurs = tipe('valeur')                
                size_tab = len(valeurs)
                if (size_tab != 0):
                    print(str(valeurs[-1].text))
                    app.co2 = str(valeurs[-1].text)
        
        document = requests.get(urlproductionmix,verify=False)
        soup= BeautifulSoup(document.content,"lxml-xml")
        types = soup.findAll('type')

        for tipe in types:
            if str(tipe['v']) == 'Nucléaire':
                valeurs = tipe('valeur')
                size_tab = len(valeurs)
                if (size_tab != 0):
                    print(str(valeurs[-1].text))
                    app.nuke = str(valeurs[-1].text)
            
            if str(tipe['v']) == 'Charbon':
                valeurs = tipe('valeur')
                size_tab = len(valeurs)
                if (size_tab != 0):
                    print(str(valeurs[-1].text))
                    app.coal = str(valeurs[-1].text)

            if str(tipe['v']) == 'Gaz':
                valeurs = tipe('valeur')
                size_tab = len(valeurs)
                if (size_tab != 0):
                    print(str(valeurs[-1].text))
                    app.gaz = str(valeurs[-1].text)

            if str(tipe['v']) == 'Fioul':
                valeurs = tipe('valeur')
                size_tab = len(valeurs)
                if (size_tab != 0):
                    print(str(valeurs[-1].text))
                    app.fuel = str(valeurs[-1].text)
            
            if str(tipe['v']) == 'Hydraulique':
                valeurs = tipe('valeur')
                size_tab = len(valeurs)
                if (size_tab != 0):
                    print(str(valeurs[-1].text))
                    app.hydro = str(valeurs[-1].text)

            if str(tipe['v']) == 'Eolien':
                valeurs = tipe('valeur')
                size_tab = len(valeurs)
                if (size_tab != 0):
                    print(str(valeurs[-1].text))
                    app.wind = str(valeurs[-1].text)


        
    print (app.last_refresh)
    minconsumption = min(app.liste_comsumption)
    minconsumption = minconsumption - 1
    liste_display = []

    for c in app.liste_comsumption:
        liste_display.append(c-minconsumption)


    json_data = {
            "frames": [
                {
                "text": "French electrical power consumed",
                "icon": "49411"
                },
                {
             "text": str(app.liste_comsumption[-1]) + " MW",
             "icon": "49411"
                },
                {
             "text": app.co2 + "g CO2 eq/kWh",
             "icon": "8522"
                },
             {
             "text": app.wind + " MW (wind)",
             "icon": "1153"
                },
                {
                    "index":0,
             "chartData": 
            #   app.liste_comsumption
            liste_display
            
                }
             ],
             "info":{"last_update": app.last_refresh, "date_trigger": date_trigger, "current_date": current_date, "call" : calledXml}
            }

    return json_data
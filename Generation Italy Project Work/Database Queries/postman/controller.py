from flask import Flask, request
from service import *

#istanzazione applicazione web di tipo flask
app = Flask(__name__)

# istanzzazione dei componenti service
model_service = ModelService()

#*********END POINT model********
#END POINT 1: Elenco dati per settore
#localhost:5000/model/elenco/sector/<sector>
@app.get("/model/elenco/sector/<string:sector>")
def elenco_dati_per_sector(sector):
    return model_service.elenco_dati_per_sector(sector)

#END POINT 2: Elenco dati per data
#localhost:5000/model/elenco/data/<data>
@app.get("/model/elenco/data/<string:data>")
def elenco_per_data(data):
    return model_service.elenco_per_data(data)

#END POINT 3: Elenco returns positivi
#localhost:5000/model/elenco/returns_positivi
@app.get("/model/elenco/returns_positivi")
def elenco_returns_positivi():
    return model_service.elenco_returns_positivi()

#eseguibilità della nostra applicazione
app.run(debug=True, port=5050)
from model import *
from repository import * 

class ModelService:

    #metodo di inizializzazione
    def __init__(self):
        self.repository = Repository()

    #metodo per l'elenco dei dati per settore
    def elenco_dati_per_sector(self, sector):
        sql = "SELECT m.date, asset, vol_d,vol_1w,vol_1m,vol_1y,returns FROM market_calcoli m WHERE m.sector = %s"
        ottenuto_db = self.repository.recupero_multiplio(sql,(sector,))
        if isinstance(ottenuto_db, str):
            return {"codice":500, "messaggio":ottenuto_db}, 500
        modelli = []
        for record in ottenuto_db:
            modello = Model(date=record[0], vol_d=record[1], vol_1w=record[2], vol_1m=record[3], vol_1y=record[4], returns=record[5])
            modelli.append(modello)
        return [m.serializzazione_per_sector() for m in modelli] if modelli else []

    #motodo per l'elenco dei dati per data
    def elenco_per_data(self, data):
        sql = "SELECT asset, sector, vol_d, vol_1w, vol_1m, vol_1y, returns FROM market_calcoli m WHERE m.date = %s"
        ottenuto_db = self.repository.recupero_multiplio(sql,(data,))
        if isinstance(ottenuto_db, str):
            return {"codice":500, "messaggio":ottenuto_db}, 500
        modelli = []
        for record in ottenuto_db:
            modello = Model(asset=record[0], sector=record[1], vol_d=record[2], vol_1w=record[3], vol_1m=record[4], vol_1y=record[5], returns=record[6])
            modelli.append(modello)
        return [m.serializzazione_per_data() for m in modelli] if modelli else []
    
    #metodo per l'elenco dei returns positivi
    def elenco_returns_positivi(self):
        sql = "SELECT m.date, asset, sector, returns FROM market_calcoli m WHERE m.returns > 0"
        ottenuto_db = self.repository.recupero_multiplio(sql)
        if isinstance(ottenuto_db, str):
            return {"codice":500, "messaggio":ottenuto_db}, 500
        modelli = []
        for record in ottenuto_db:
            modello = Model(date=record[0], asset=record[1], sector=record[2], returns=record[3])
            modelli.append(modello)
        return [m.serializzazione_per_returns_positivi() for m in modelli] if modelli else []
    

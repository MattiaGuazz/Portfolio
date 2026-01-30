from abc import ABC
import pandas as pd
import os


#definizione classe astratta per centralizzazione delle operazioni comuni
class Modello_base(ABC):

    #metodo inizializzazione
    def __init__(self, percorso_dataset, righe_da_saltare=0):
        self.dataframe = pd.read_csv(filepath_or_buffer=os.path.join(os.path.dirname(__file__), percorso_dataset), skiprows= righe_da_saltare)

    #fumeotodo per ottenere informazioni generali
    @staticmethod
    def analisi_generali(df):
        print("***********Analisi generali dataframe***********")
        print("Prime cinque osservazioni", df.head().to_string(), sep="\n")
        print("Ultime cinque osservazioni", df.tail().to_string(), sep="\n")
        print("informazioni generali")
        df.info()

    #metodo che controlla i valori univoci
    @staticmethod
    def analisi_valori_univoci(df, variabili_da_trovare=None):  #valori_da_trovare è una lista
        print("***********Valori univoci dataframe***********")
        if variabili_da_trovare:
            df = df.drop(variabili_da_trovare, axis=1) #axis = 1 colonne, axis = 0 righe
        for colonne in df.columns:
            print(f"In colonna {colonne} abbiamo {df[colonne].nunique()} valori univoci" ) #numero valori univoci
            for valore in df[colonne].unique(): #di quella colonna ritorna una series con solo numeri univoci(non duplicati)
                print(valore)

    #metodo per analisi dei principali indici statistici
    @staticmethod
    def analisi_indici_statistici(df):
        print("***********Indici statistici dataframe***********")
        indici_generali = df.describe()
        print("Indici statitisci principali delle variabili quantitative:", indici_generali.to_string(), sep="\n")
        for colonna in df.columns:
            print(f"Moda colonna {colonna}: ",df[colonna].mode().iloc[0])

    #metodo per identificazione degli outliners
    @staticmethod
    def identificazione_outliner(df, variabili_da_droppare = None):
        print("***********Individuazione Outliers dataframe***********")
        if variabili_da_droppare:
            df = df.drop(variabili_da_droppare, axis=1)
        for colonna in df.columns:
            #calcolo differenza interquartile
            q1 = df[colonna].quantile(0.25)
            q3 = df[colonna].quantile(0.75)
            iqr = q3 - q1
            #calcolo limiti supueriore/inferiore
            limite_inferiore = q1 -1.5*iqr
            limite_superiero = q3 +1.5*iqr
            #individuazione outliers
            outliers = df[(df[colonna] < limite_inferiore) | (df[colonna] > limite_superiero)]
            print(f"Nella colonna {colonna} sono presenti n° {len(outliers)} outliers ({(len(outliers)/len(df))*100}%)")
        
from modello_base import Modello_base
import pandas as pd
from scipy.stats import chi2_contingency, contingency, spearmanr, pearsonr
import matplotlib.pyplot as plt
import numpy as np

class Analisi_Progetto_Work(Modello_base):
    # metodo di inizializzazione
    def __init__(self, percorso_dataset, righe_da_saltare=0):
        super().__init__(percorso_dataset, righe_da_saltare)
        self.dataframe_sistemato = self.sistema_dataframe()

    def tabelle_contingenza(self, colonna, target):
        #generazione e stampa tabella di contingenza
        tabella_contingenza = pd.crosstab(self.dataframe_sistemato[colonna],self.dataframe_sistemato[target])
        #test del chi-quadro e stampa esito
        chi2, p, dof, excepted = chi2_contingency(tabella_contingenza)
        print(f"Il p-value risultate dal chi-quadro su tabella di contingenza {colonna}-{target} è: {p}" )
        print(f"Notazione non scientifica del p-value: {format(p, ".53f")}") #53 limite massimo di decimali
        #calcolo indice cramer e stampa esito
        cramer = contingency.association(tabella_contingenza, method="cramer")
        print(f"L'indice di cramer sulla tabella contingenza {colonna}-{target} è: {cramer}")
        return tabella_contingenza

    def correlazione_regressione(self, colonna, target):
        #analisi correlazione
        correlazione, p = pearsonr(self.dataframe_sistemato[colonna], self.dataframe_sistemato[target])
        print(f"La correlazione: {correlazione}")
        print(f"La p: {p}")
    
    # funzione per mettere a posto il dataframe
    def sistema_dataframe(self):
        # definizione colonne non utilizzate per l'analisi
        valori_da_droppare = ["us_rates_%","CPI","GDP","sp500 high","sp500 low","sp500 open", "nasdaq high","nasdaq low","nasdaq open", "silver high","silver low","silver open", "oil high","oil low","oil open", "platinum high","platinum low","platinum open", "palladium high","palladium low","palladium open", "gold low","gold open"]
        
        # modifica della colonna "gold high" in "gold high-low" ovvero la volatilità intraday
        self.dataframe["gold high"] = self.dataframe["gold high"].fillna(0) - self.dataframe["gold low"].fillna(0)
        self.dataframe = self.dataframe.rename(columns={"gold high": "gold high-low"})

        # resa della colonna "date" in datetime per poterla usare come indice temporale del dataframe
        self.dataframe["date"] = pd.to_datetime(self.dataframe["date"])
        self.dataframe = self.dataframe.set_index("date")

        # calcoli per ricavare ricavi%
        assets = ["sp500", "nasdaq", "silver", "oil", "platinum", "palladium", "gold"]
        FX = ["usd_chf", "eur_usd"]
        totalAssets = assets + FX
        
        for currency in FX:
            # aggiunta delle varie colonne "returns" con il calcolo dei rendimenti giornalieri per i cambi valuta e modifica del primo valore per ogni colonna "returns" da NaN a 0 per non impattare i calcoli statistici
            self.dataframe[f"{currency} returns"] = self.dataframe[currency].pct_change().fillna(0)
        
        for asset in assets:
            
            ret = f"{asset} returns"

            # aggiunta delle varie colonne "returns" con il calcolo dei rendimenti giornalieri per le varie azioni
            self.dataframe[ret] = self.dataframe[f"{asset} close"].pct_change()

            # modifica del primo valore per ogni colonna "returns" da NaN al valore dato da (close - open)/open per impattare i calcoli statistici il meno possibile
            self.dataframe[f"{asset} returns"].iloc[0] = (self.dataframe[f"{asset} close"].iloc[0] - self.dataframe[f"{asset} open"].iloc[0]) / self.dataframe[f"{asset} open"].iloc[0]

        for asset in totalAssets:

            ret = f"{asset} returns"

            # creazione della colonna volatilità giornaliera "vol_d"
            daily = self.dataframe[ret].abs() * np.sqrt(252)
            self.dataframe[f"{asset} vol_d"] = daily.reindex(self.dataframe.index, method="ffill")

            # creazione della colonna volatilità settimanale "vol_1w"
            weekly = self.dataframe[ret].resample("W").std() * np.sqrt(252)
            self.dataframe[f"{asset} vol_1w"] = weekly.reindex(self.dataframe.index, method="ffill")

            # creazione della colonna volatilità mensile "vol_1m"
            monthly = self.dataframe[ret].resample("M").std() * np.sqrt(252)
            self.dataframe[f"{asset} vol_1m"] = monthly.reindex(self.dataframe.index, method="ffill")

            # creazione della colonna volatilità annua "vol_1y"
            yearly = self.dataframe[ret].resample("Y").std() * np.sqrt(252)
            self.dataframe[f"{asset} vol_1y"] = yearly.reindex(self.dataframe.index, method="ffill")

            # modifica dei valori NaN nel primo valore di volatilità successivo, questo viene fatto perchè è la tecnica più utilizzata in finanza
            for period in ["d", "1w", "1m", "1y"]:

                col = f"{asset} vol_{period}" 
                self.dataframe[col] = self.dataframe[col].fillna(method="bfill")

        
        # drop dei valori non analizzati e delle righe vuote selezionate controllando se il campo "sp500 close" è vuoto
        df_sistemato = self.dataframe.drop(valori_da_droppare, axis = 1)
        df_sistemato = df_sistemato.dropna(subset=["sp500 close"])
        
        # modifica valori nulli per il cambio valute copiando il primo valore antecedente questo viene fatto perchè è la tecnica più utilizzata in finanza
        df_sistemato["usd_chf"] = df_sistemato["usd_chf"].fillna(method="ffill")
        df_sistemato["eur_usd"] = df_sistemato["eur_usd"].fillna(method="ffill")

        


        return df_sistemato


# analisi = Analisi_Progetto_Work("financial_regression.csv")
# analisi.analisi_generali(analisi.dataframe_sistemato)

#analisi.dataframe_sistemato.to_csv("dataframe_sistemato_clean.csv", index=True)
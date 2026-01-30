from analisiProjectWork import Analisi_Progetto_Work
import pandas as pd
from scipy.stats import pearsonr, f_oneway
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import warnings

# per evitare warning di future deprecation nel terminale 
warnings.filterwarnings("ignore", category=FutureWarning)

# definizione dizionario settori per ogni asset
asset_sector = {
    "sp500": "Equity", # Equity = mercato azionario
    "nasdaq": "Equity",
    "gold": "Metals", # Metals = metalli preziosi
    "silver": "Metals", 
    "platinum": "Metals", 
    "palladium": "Metals", 
    "oil": "Energy", # Energy = mercato dell'energia
    "usd_chf": "FX", # FX = cambio valuta
    "eur_usd": "FX",
}

# creazione dataset da csv e creazione alias
analisi = Analisi_Progetto_Work("financial_regression.csv")
data = analisi.dataframe_sistemato

# analisi outlier nelle volatilità del petrolio per vedere se sono dovuti a variazioni di prezzo reali o se sono errori di importazione dei dati

# date_outlier = data["oil vol_1m"].idxmax()
# data.loc[date_outlier]
# print(date_outlier)
# print(data.loc[date_outlier - pd.Timedelta(days=3) : date_outlier + pd.Timedelta(days=3), ["oil close"]])

# siccome gli outlier sono dovuti ad un avvenimento storico effettuiamo una Winsorization per ammortizzarne l'effetto nei calcoli statistici pur mantenendo l'accuratezza dei dati
for asset, sector in asset_sector.items():

    upper = data[f"{asset} vol_d"].quantile(0.99)
    data[f"{asset} vol_d"] = np.where(data[f"{asset} vol_d"] > upper, upper, data[f"{asset} vol_d"])

    upper = data[f"{asset} vol_1w"].quantile(0.99)
    data[f"{asset} vol_1w"] = np.where(data[f"{asset} vol_1w"] > upper, upper, data[f"{asset} vol_1w"])

    upper = data[f"{asset} vol_1m"].quantile(0.99)
    data[f"{asset} vol_1m"] = np.where(data[f"{asset} vol_1m"] > upper, upper, data[f"{asset} vol_1m"])

    upper = data[f"{asset} vol_1y"].quantile(0.99)
    data[f"{asset} vol_1y"] = np.where(data[f"{asset} vol_1y"] > upper, upper, data[f"{asset} vol_1y"])

# creazione dataframe "df_long" per facilitare i calcoli statistici per i vari settori
rows = []

data["usd_chf volume"] = 999999999
data["eur_usd volume"] = 999999999

for asset, sector in asset_sector.items():
    
    row = pd.DataFrame({
        
        "asset": asset,
        "sector": sector,
        "vol_d": data[f"{asset} vol_d"],
        "vol_1w": data[f"{asset} vol_1w"],
        "vol_1m": data[f"{asset} vol_1m"],
        "vol_1y": data[f"{asset} vol_1y"],
        "returns":data[f"{asset} returns"],
        "volume":data[f"{asset} volume"],
    
    })
    
    rows.append(row)

df_long = pd.concat(rows)
# analisi.analisi_generali(df_long)
# df_long.to_csv("dataframe_calcoli.csv", index=True)

# print(df_long)

# calcolo media, deviazione standard e mediana per le varie volatilità e i returns e print sotto forma di tabella dove le righe sono i settori degli asset
group_stats = df_long.groupby("sector")[["vol_d", "vol_1w", "vol_1m", "vol_1y", "returns"]].agg(["mean", "std", "median"])
print(group_stats)

# boxplot delle varie volatilità
plt.figure(figsize=(8, 5))
sns.boxplot(data=df_long, x="sector", y="vol_d")
plt.title("Distribuzione della volatilità giornaliera per settore")
plt.show()

plt.figure(figsize=(8, 5))
sns.boxplot(data=df_long, x="sector", y="vol_1w")
plt.title("Distribuzione della volatilità settimanale per settore")
plt.show()

plt.figure(figsize=(8, 5))
sns.boxplot(data=df_long, x="sector", y="vol_1m")
plt.title("Distribuzione della volatilità mensile per settore")
plt.show()

plt.figure(figsize=(8, 5))
sns.boxplot(data=df_long, x="sector", y="vol_1y")
plt.title("Distribuzione della volatilità annuale per settore")
plt.show()

# definizione codici numerici per ogni settore in modo tale da poter fare le correlazioni statistiche e aggiunta di essi al df_long
sector_codes, uniques = pd.factorize(df_long["sector"])
df_long["sector_code"] = sector_codes
print(df_long)

print()
categories = ["vol_d", "vol_1w", "vol_1m", "vol_1y", "returns"]
for category in categories:
    
    # creazione di gruppi di azioni usando i settori come discriminante
    groups = []
    for sector in df_long["sector"].unique():
        vals = df_long.loc[df_long["sector"] == sector, category].dropna()
        groups.append(vals)

    #  confronto della distribuzione della categoria nei vari settori per indicare se le medie di essa sono significativamente diverse tra i vari settori
    F_stat, p_value = f_oneway(*groups)

    print()
    print("----------------------------")
    print(f"{category} F-statistic:", F_stat) #  più questo valore è elevato più le categorie sono indipendenti tra loro

    print(f"{category} p-value:", p_value) #  più questo valore è elevato meno le categorie sono indipendenti tra loro
    print("----------------------------")

    # controllo relazione lineare tra la categoria e i settori, se è 0 non c'è correlazione
    # se è positiva vuole dire che andando verso settori con codice più alto i valori della categoria tendono ad aumentare
    # se è negativa vuole dire che andando verso settori con codice più alto i valori della categoria tendono a diminuire
    correlazioneSettore = df_long[category].corr(df_long["sector_code"]) 
    print(f"Correlazione tra {category} e i settori):", correlazioneSettore)
    print("----------------------------")

print()
print("----------------------------")

# creazione dataframe basato su "df_long" raggruppando i dati per settore e popolandolo con le medie di "vol_d", "vol_1w", "vol_1m", "vol_1y", "returns"
sector_means = df_long.groupby("sector")[["vol_d", "vol_1w", "vol_1m", "vol_1y", "returns"]].mean()


volatilita = ["vol_d", "vol_1w", "vol_1m", "vol_1y"]
ricorrenze = ["giornaliera", "settimanale", "mensile", "annuale"]

for vol, ricorrenza in zip(volatilita, ricorrenze):
    
    # calcolo della correlazione tra la media della volatilità con la media dei rendimenti
    corrVolRet, pVolRet = pearsonr(sector_means[vol], sector_means["returns"]) 
    print(f"Correlazione tra {vol} e returns):", corrVolRet)
    print(f"quanto è significativa la correlazione tra {vol} e returns):", pVolRet)
    print("----------------------------")
    print()
    print("----------------------------")

    # creazione tabella di pivot per ogni tipo di volatilità con i settori come colonne e le date come indice
    pivot_vol = df_long.pivot_table(index=df_long.index, columns="sector", values=vol)

    # plot grafico dell'andamento temporale delle volatilità per ogni settore
    for sector in pivot_vol.columns:
    
        plt.figure(figsize=(12,6))
        plt.plot(pivot_vol.index, pivot_vol[sector], label=sector)
        plt.title(f"Volatilità {ricorrenza} per settore nel tempo")
        plt.xlabel("Data")
        plt.ylabel(f"Volatilità {ricorrenza}")
        plt.legend()
        plt.show()

# creazione tabella di pivot per i rendimenti con i settori come colonne e le date come indice
pivot_ret = df_long.pivot_table(index=df_long.index, columns="sector", values="returns")

# plot grafico dell'andamento temporale dei rendimenti per ogni settore
for sector in pivot_ret.columns:
    
    plt.figure(figsize=(12,6))
    plt.plot(pivot_ret.index, pivot_ret[sector], label=sector)
    plt.title("Rendimenti percentuali per settore nel tempo")
    plt.xlabel("Data")
    plt.ylabel("Rendimenti percentuali")
    plt.legend()
    plt.show()

# media mobile a 30gg dei rendimenti per poter analizzare al meglio l'andamento del mercato
rolling_ret = pivot_ret.rolling(30).mean()

# plot grafico dell'andamento temporale della media mobile dei rendimenti per ogni settore
for sector in rolling_ret.columns:
    
    plt.figure(figsize=(12,6))
    plt.plot(rolling_ret.index, rolling_ret[sector], label=sector)
    plt.title("Rendimenti medi (rolling 30 giorni) per settore")
    plt.xlabel("Data")
    plt.ylabel("Rendimento medio")
    plt.legend()
    plt.show()


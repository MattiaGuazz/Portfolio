from repository import MercatoRepository

#
# Service applicativo che fa da "ponte" tra il controller Flask
# e la tabella SQL market_calcoli.
#

class MercatoService:

  # Insieme delle colonne che permettiamo di interrogare tramite l'endpoint generico
  # /api/data/<nome_colonna>. Le colonne corrispondono alle stesse usate
  # nello script di analisi: volatilità a varie frequenze e rendimenti percentuali.
  COLONNE_CONSENTITE = {"vol_d", "vol_1w", "vol_1m", "vol_1y", "returns"}

  # Dizionario che raggruppa gli asset nei 4 settori principali
  # usati anche nell'analisi: Equity, Metals, Energy, FX.
  # L'endpoint /api/volatility/1m/<categoria> sfrutta questa mappa
  # per restituire più serie in un colpo solo.
  CATEGORIE_ASSET = {
    "equity": ["sp500", "nasdaq"],
    "metals": ["gold", "silver", "platinum", "palladium"],
    "energy": ["oil"],
    "fx": ["usd_chf", "eur_usd"]
  }

  def __init__(self):
    # Istanza del repository che gestisce la connessione MySQL e le query grezze
    self.repository = MercatoRepository()

  def dati_categoria(self, categoria, limite=100):
    """Restituisce la serie vol_1m per tutti gli asset della categoria scelta.

    Questo metodo serve per l'endpoint:
      /api/volatility/1m/<categoria>

    Esempio: categoria="equity" → torna SP500 e Nasdaq con la loro volatilità mensile.
    """

    # Recuperiamo la lista di asset associati alla categoria richiesta
    asset_categoria = self.CATEGORIE_ASSET.get(categoria)
    if not asset_categoria:
      # Se la categoria non esiste restituiamo un messaggio di errore descrittivo
      return {"errore": "Categoria non trovata"}

    serie_categoria = []  # conterrà una voce per ogni asset del gruppo

    for asset in asset_categoria:
      # Query parametrica: estraiamo data e vol_1m per l'asset indicato
      sql = (
        "SELECT date, vol_1m FROM market_calcoli "
        "WHERE asset=%s AND vol_1m IS NOT NULL "
        "ORDER BY date DESC LIMIT %s"
      )
      valori_query = (asset, limite)
      dati_db = self.repository.recupero_multiplo(sql, valori_query)
      if not dati_db:
        # Se per quell'asset non troviamo righe, passiamo al successivo
        continue

      # Normalizziamo i record del DB in una lista di dict JSON-friendly
      # con chiavi "data" e "valore", in modo coerente con lo script di analisi.
      serie_pulita = []
      for record in dati_db:
        serie_pulita.append({
          "data": str(record[0]),   # convertiamo la data in stringa
          "valore": float(record[1])  # e il valore numerico in float
        })

      # Aggiungiamo la serie di questo asset al gruppo complessivo
      serie_categoria.append({
        "asset": asset,
        "colonna": "vol_1m",
        "dati": serie_pulita
      })

    # Risposta aggregata per la categoria: usata direttamente dal controller
    return {
      "categoria": categoria,
      "serie": serie_categoria
    }

  def dati_singoli(self, colonna, asset="sp500", limite=50):
    """Ritorna una serie temporale per la colonna richiesta e l'asset dato.

    Questo è il service usato dall'endpoint generico:
      /api/data/<nome_colonna>?asset=...&limit=...

    Esempio:
      /api/data/returns?asset=gold&limit=50
    restituisce gli ultimi 50 valori di rendimento percentuale per l'oro.
    """

    # Blocchiamo subito richieste su colonne non previste
    if colonna not in self.COLONNE_CONSENTITE:
      return []

    # Costruiamo la query usando la colonna richiesta e l'asset scelto
    sql = (
      "SELECT date, " + colonna + " FROM market_calcoli "
      "WHERE asset=%s AND " + colonna + " IS NOT NULL "
      "ORDER BY date DESC LIMIT %s"
    )
    valori_query = (asset, limite)
    dati_db = self.repository.recupero_multiplo(sql, valori_query)

    # Anche qui normalizziamo in una lista di dict con data + valore
    risultato = []
    for record in dati_db:
      risultato.append({
        "data": str(record[0]),
        "valore": float(record[1])
      })
    return risultato


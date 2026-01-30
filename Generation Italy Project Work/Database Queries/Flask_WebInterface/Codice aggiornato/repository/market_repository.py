import pymysql


"""Modulo di accesso al database MySQL per il project work.
.
"""


class MercatoRepository:
  """Incapsula la connessione a MySQL e le query di sola lettura.

  Questa classe è l'equivalente "lato DB" di ciò che nello script di analisi
  è la lettura del CSV: fornisce i dati grezzi che poi il service trasforma
  in strutture Python/JSON più comode.
  """

  def _ottieni_connessione(self):
    """Crea e restituisce una nuova connessione al database MySQL.

    """
    return pymysql.connect(
      host="localhost",
      port=8889,
      user="root",
      password="root",
      database="ProjectWork_market_data"
    )

  def recupero_multiplo(self, sql, valori=None):
    """Esegue una SELECT che può restituire più righe.

    Ritorna:
      - una lista di tuple (come restituita da ``cursor.fetchall()``)
      - oppure una lista vuota in caso di errore o nessun risultato.
    """

    try:
      # "with" garantisce la chiusura automatica della connessione e del cursore
      with self._ottieni_connessione() as connessione:
        with connessione.cursor() as cursore:
          if valori:
            cursore.execute(sql, valori)
          else:
            cursore.execute(sql)
          return cursore.fetchall()
    except Exception as e:
      # In caso di problemi logghiamo l'errore in console e ritorniamo lista vuota
      print("Errore DB recupero multiplo:", e)
      return []

  def recupero_singolo(self, sql, valori):
    """Esegue una SELECT che deve restituire al massimo un record.
    Ritorna:
      - una singola tupla (``cursor.fetchone()``)
      - oppure ``None`` se non viene trovato nulla o se c'è un errore.
    """

    try:
      with self._ottieni_connessione() as connessione:
        with connessione.cursor() as cursore:
          cursore.execute(sql, valori)
          return cursore.fetchone()
    except Exception as e:
      print("Errore DB recupero singolo:", e)
      return None


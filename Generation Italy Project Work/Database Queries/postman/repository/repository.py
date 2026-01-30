import pymysql

class Repository:
    # metodo ausiliario per ottenere connessione al db quando serve
    def _get_connection(self):
        return pymysql.connect(
        host="localhost",
        port=8889,
        user="root",
        passwd="root",
        database="ProjectWork_market_data"
        )
    
    #metodo generico standard di manipolazione dei dati
    def manipolazione_dati(self, sql, valori):
        try:
            with self._get_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(sql, valori)
                    connection.commit()
                    return cursor.rowcount
        except Exception as e:
            print(e)
            return "errore database"
        
    #metodo generico standard per recupero di dati multipli
    def recupero_multiplio(self, sql, valori=None):
        try:
            with self._get_connection() as connection:
                with connection.cursor() as cursor:
                    if valori:
                        cursor.execute(sql, valori)
                    else:
                        cursor.execute(sql)
                    return cursor.fetchall()
        except Exception as e:
            print(e)
            return "errore database"
        
    #metodo generico standard per recupero di dati singolo
    def recupero_singolo(self, sql, valori):
        try:
            with self._get_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(sql, valori)
                    return cursor.fetchone()
        except Exception as e:
            print(e)
            return "errore database"

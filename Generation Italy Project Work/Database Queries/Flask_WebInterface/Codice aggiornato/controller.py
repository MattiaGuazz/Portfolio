from flask import Flask, render_template, request, jsonify
from service import *

# App Flask che espone sia l'HTML sia le API JSON
app = Flask(__name__)

# Service centralizzato per interrogare il DB
market_service = MercatoService()

@app.route("/")
def home():
  # Pagina principale con i link alle API
  return render_template("index.html")

@app.get("/api/volatility/1m/<categoria>")
def api_volatilita_categoria(categoria):
  # Estrae serie vol_1m per tutti gli asset della categoria
  limite = request.args.get('limit', default=100, type=int)
  risultato = market_service.dati_categoria(categoria, limite)
  return jsonify(risultato)

@app.get("/api/data/<nome_colonna>")
def api_dati_singoli(nome_colonna):
  # Endpoint generico per qualunque colonna consentita (returns, vol_d, ...)
  limite = request.args.get('limit', default=50, type=int)
  asset = request.args.get('asset', default='sp500')
  dati = market_service.dati_singoli(nome_colonna, asset=asset, limite=limite)
  if not dati:
    return jsonify({"error": "Colonna non valida o asset senza dati"}), 404
  return jsonify({"column": nome_colonna, "asset": asset, "data": dati})

if __name__ == "__main__":
  # Avvio locale in debug
  app.run(debug=True, port=5050)

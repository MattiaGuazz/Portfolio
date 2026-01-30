class Model:

    def __init__(self,id=None, date=None, asset=None, sector=None, vol_d=None, vol_1w=None, vol_1m=None, vol_1y=None, returns=None):
        self.id = id
        self.date = date
        self.asset = asset
        self.sector = sector
        self.vol_d = vol_d
        self.vol_1w = vol_1w
        self.vol_1m = vol_1m
        self.vol_1y = vol_1y
        self.returns = returns

    def serializzazione_per_sector(self):
        return {
            "date": self.date,
            "asset": self.asset,
            "vol_d": self.vol_d,
            "vol_1w": self.vol_1w,
            "vol_1m": self.vol_1m,
            "vol_1y": self.vol_1y,
            "returns": self.returns
        }
    
    def serializzazione_per_data(self):
        return {
            "asset": self.asset,
            "sector": self.sector,
            "vol_d": self.vol_d,
            "vol_1w": self.vol_1w,
            "vol_1m": self.vol_1m,
            "vol_1y": self.vol_1y,
            "returns": self.returns
        }
    
    def serializzazione_per_returns_positivi(self):
        return {
            "date": self.date,
            "asset": self.asset,
            "sector": self.sector,
            "returns": self.returns
        }
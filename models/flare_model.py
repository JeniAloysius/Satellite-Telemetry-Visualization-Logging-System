import pandas as pd
import numpy as np

class SolarFlareModel:
    def __init__(self):
        self.threshold = None

    def train(self, df):
        # Simple model: rolling mean + 2σ
        df['flux'] = df['flux'].astype(float)
        mean = df['flux'].rolling(50).mean().iloc[-1]
        std = df['flux'].rolling(50).std().iloc[-1]
        self.threshold = mean + 2 * std

    def predict(self, current_flux):
        return current_flux > self.threshold

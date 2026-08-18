
import pandas as pd

def extract(path):
    dataframe = pd.read_csv(path)
    return dataframe.to_string(), 1
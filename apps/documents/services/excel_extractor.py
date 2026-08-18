
import pandas as pd

def extract(path):
    workbook = pd.read_excel(path, sheet_name=None)
    output = []

    for sheet, dataframe in workbook.items():
        output.append(f"Sheet: {sheet}")
        output.append(dataframe.to_string())
    return "\n".join(output), len(workbook)
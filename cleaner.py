import pandas as pd
import os

folder = 'output/ne'
new_folder = 'output/ne/cleaned'
os.makedirs(new_folder, exist_ok=True)

for doc in os.listdir(folder):
    if doc.endswith('.xlsx'):
        print(doc)
        df = pd.read_excel(os.path.join(folder, doc))
        # print(df)
        df['phrase'] = df['phrase'].str.replace('\n', '')
        df.to_excel(os.path.join(new_folder, f'{doc}.xlsx'), index=False)

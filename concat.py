import pandas as pd
import os

input_path = 'output/charles_without_sentences.xlsx'
output_path = 'output'


def concat_string(row):
    """consider the empty string"""


df = pd.read_excel(input_path)
df.fillna('', inplace=True)

cols = ['contexte_avant', 'pivot', 'contexte_apres']

df['phrase'] = df[cols].apply(lambda row: " ".join(row.values.astype(str)), axis=1).str.strip()
# print(df['phrase'])

# print(df.head())
df.to_excel(os.path.join(output_path, 'charles.xlsx'), index=False)

import pandas as pd
import re  #Regular expressions

chunksize = 1000
chunks = []

pattern = r'\bNLP\b'

for chunk in pd.read_json("2023.jsonl", lines=True, chunksize=chunksize):
    filtered_chunk = chunk[chunk['description'].apply(lambda d: bool(re.search(pattern, d['text'], re.IGNORECASE)) if pd.notna(d) and 'text' in d else False)]
    chunks.append(filtered_chunk)

df_nlp = pd.concat(chunks, ignore_index=True)

common_titles = df_nlp['headline'].value_counts()

print("Most common job titles for jobs mentioning NLP:")
print(common_titles.head(10))

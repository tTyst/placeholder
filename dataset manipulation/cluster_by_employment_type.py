import pandas as pd
import json
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.cluster import AgglomerativeClustering

# Definiera nyckelord för filtrering
keywords = ['restaurang', 'kock', 'servitör', 'servitris', 'bartender', 'diskare', "hotell"]

# Funktion för att extrahera säkert från JSON-struktur med listor
def extract_label_from_list(data):
    if isinstance(data, list) and len(data) > 0:
        return data[0].get('label', None)
    return None

# Funktion för att extrahera säkert från direkt JSON-struktur
def extract_label_from_dict(data):
    if isinstance(data, dict):
        return data.get('label', None)
    return None

def extract_conditions_from_dict(data):
    if isinstance(data, dict):
        return data.get('conditions', None)
    return None

# Funktion för att bearbeta en datachunk
def process_chunk(chunk):
    chunk_filtered = chunk[chunk['headline'].str.contains('|'.join(keywords), case=False, regex=True, na=False)].copy()
    
    chunk_filtered['description_conditions'] = chunk_filtered['description'].apply(extract_conditions_from_dict)
    chunk_filtered['working_hours_type_label'] = chunk_filtered['working_hours_type'].apply(extract_label_from_dict)
    chunk_filtered['duration_label'] = chunk_filtered['duration'].apply(extract_label_from_dict)
    chunk_filtered['employment_type_label'] = chunk_filtered['employment_type'].apply(extract_label_from_list)
    
    return chunk_filtered

# Initiera en tom lista för att lagra bearbetade chunks
processed_data = []

chunk_size = 5000
with open('2023.jsonl', 'r', encoding='utf-8') as file:
    chunk = []
    for line in file:
        chunk.append(json.loads(line))
        if len(chunk) == chunk_size:
            df_chunk = pd.DataFrame(chunk)
            processed_data.append(process_chunk(df_chunk))
            chunk = []
    if chunk:
        df_chunk = pd.DataFrame(chunk)
        processed_data.append(process_chunk(df_chunk))

filtered_df = pd.concat(processed_data, ignore_index=True)

# One-Hot Encoding av data
encoder = OneHotEncoder(sparse=False)
encoded_data = encoder.fit_transform(filtered_df[['description_conditions','working_hours_type_label', 'duration_label', 'employment_type_label']])
encoded_df = pd.DataFrame(encoded_data, columns=encoder.get_feature_names_out())

# Standardisera data
scaler = StandardScaler()
scaled_features = scaler.fit_transform(encoded_df)

# Agglomerative Clustering
agg_cluster = AgglomerativeClustering(n_clusters=4)
clusters = agg_cluster.fit_predict(scaled_features)
filtered_df['cluster'] = clusters

# Spara resultatet
output_file = 'filter_by_employ_23_restaurang.csv'
filtered_df.to_csv(output_file, index=False)

# Skriv ut ett framgångsmeddelande
print(f"Databearbetning klar. Resultaten sparades till {output_file}")

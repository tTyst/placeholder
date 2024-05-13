import pandas as pd
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.cluster import AgglomerativeClustering

# Definiera nyckelord för filtrering
keywords = ['restaurang', 'kock', 'servitör', 'servitris', 'bartender', 'diskare', "hotell"]

# Funktion för att bearbeta en datachunk
def process_chunk(chunk):
    chunk_filtered = chunk[chunk['headline'].str.contains('|'.join(keywords), case=False, regex=True, na=False)].copy()
    return chunk_filtered

# Läs in data från CSV-fil
data = pd.read_csv('2023.csv', encoding='utf-8', low_memory=False)

# Filtrera och bearbeta data
filtered_data = process_chunk(data)

# One-Hot Encoding av data
encoder = OneHotEncoder(sparse=False)
encoded_data = encoder.fit_transform(filtered_data[['description_conditions','working_hours_type_label', 'duration_label', 'employment_type_0_label']])
encoded_df = pd.DataFrame(encoded_data, columns=encoder.get_feature_names_out())

# Standardisera data
scaler = StandardScaler()
scaled_features = scaler.fit_transform(encoded_df)

# Agglomerative Clustering
agg_cluster = AgglomerativeClustering(n_clusters=4)
clusters = agg_cluster.fit_predict(scaled_features)
filtered_data['cluster'] = clusters

# Spara resultatet
output_file = 'filter_by_employ_23_restaurang.csv'
filtered_data.to_csv(output_file, index=False)

# Skriv ut ett framgångsmeddelande
print(f"Databearbetning klar. Resultaten sparades till {output_file}")

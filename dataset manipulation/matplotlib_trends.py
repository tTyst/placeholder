import pandas as pd
import matplotlib.pyplot as plt

# Läs in DataFrame från CSV OBS! se till att inputfilen är korrekt
df = pd.read_csv('filter_by_employ_23_2.csv')

# Konvertera publication_date till datetime
df['publication_date'] = pd.to_datetime(df['publication_date'], errors='coerce')

# Filtrera för att bara inkludera data från 2023-01-01 och framåt
df = df[df['publication_date'] >= '2023-01-01']

# Extrahera månad och år för gruppering
df['year_month'] = df['publication_date'].dt.to_period('M')

# Gruppera data efter kluster och månad
clustered_trends = df.groupby(['cluster', 'year_month']).size().reset_index(name='count')

# Byt namn på klusternumren till etiketter
cluster_labels = {
    0: "Deltid",
    1: "Heltid",
    2: "Sommarjobb",
    3: "Behovsanställning"
}
clustered_trends['cluster'] = clustered_trends['cluster'].map(cluster_labels)

# Pivotera data för att få klustren som separata kolumner
trend_pivot = clustered_trends.pivot(index='year_month', columns='cluster', values='count').fillna(0)

# Plot
plt.figure(figsize=(10, 6))
for cluster in trend_pivot.columns:
    plt.plot(trend_pivot.index.astype(str), trend_pivot[cluster], label=cluster)

plt.xlabel('Month')
plt.ylabel('Number of Job Postings')
plt.title('Trends in Job Postings per Cluster Over Time')
plt.xticks(rotation=45)
plt.legend(title='Cluster')
plt.tight_layout()
plt.show()

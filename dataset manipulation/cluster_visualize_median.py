import pandas as pd

# Load the CSV file into a DataFrame
df = pd.read_csv('filter_by_employ_23_restaurang.csv', low_memory=False)

# Ensure the 'cluster' column exists
if 'cluster' not in df.columns:
    raise KeyError("The DataFrame must contain a 'cluster' column.")

# Specified columns to display from each cluster
display_columns = ['description_text', 'description_conditions', 'working_hours_type_label', 'duration_label', 'employment_type_label', 'cluster']

# Initialize a counter for the total number of job postings
total_postings = 0

# Analyze each cluster
for k in range(df['cluster'].nunique()):
    # Get data for the current cluster
    cluster_data = df[df['cluster'] == k]
    
    # Get the number of job postings in the current cluster
    cluster_postings = len(cluster_data)
    total_postings += cluster_postings
    
    print(f"\nCluster {k} Profile:")
    print(f"Number of job postings in cluster {k}: {cluster_postings}")
    
    # Print the mode (most frequent value) for selected columns
    for col in display_columns:
        if col in cluster_data.columns:
            mode_value = cluster_data[col].mode()
            most_common = mode_value[0] if not mode_value.empty else "N/A"
            print(f"{col} (Most Common): {most_common}")

# Print the total number of job postings across all clusters
print(f"\nTotal number of job postings across all clusters: {total_postings}")

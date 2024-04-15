import pandas as pd

# Adjust the chunksize as needed. Smaller chunksize may be necessary for very large files or limited memory.
chunksize = 1
chunks = []

# The loop will now collect a specified number of chunks instead of breaking after the first one.
for chunk in pd.read_json("2023.jsonl", lines=True, chunksize=chunksize):
    chunks.append(chunk)
    # Comment out or remove the break statement to load more or the entire file
    break

# Concatenate the chunks into a single DataFrame
df = pd.concat(chunks, ignore_index=True)

# Adjust display options to view more of the DataFrame in your output (optional)
pd.set_option('display.max_columns', None)  # Show all columns
pd.set_option('display.max_rows', None)  # Display all rows
pd.set_option('display.max_colwidth', None)  # Show full content of each cell

# Print the DataFrame in a more readable format
for index, row in df.iterrows():
    print(f"Record {index+1}:\n")  # Add a newline after each record title for better separation
    for col in df.columns:
        value = row[col]
        if isinstance(value, dict):
            print(f"    {col}:")  # Print the parameter name
            for k, v in value.items():
                print(f"        {k}: {v}")  # Print key-value pairs in the dictionary
        else:
            print(f"    {col}: {value}")  # Print the parameter name and value on the same line
        print()  # Adds a newline after the value for better separation
    print()  # Adds another newline for clear separation between records

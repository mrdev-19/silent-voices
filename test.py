import pandas as pd

# Create an empty DataFrame with specified column names and fill them with '--'
data = [['--', '--', '--']]
columns = ['', 'Column2', 'Column3']
df = pd.DataFrame(data, columns=columns)

# Convert non-byte-like data types to bytes
df = df.applymap(lambda x: x.encode() if isinstance(x, str) else x)

# Display the DataFrame
print(df)

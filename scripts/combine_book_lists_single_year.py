import os
import pandas as pd
import glob
import config

YEAR = 2023

csv_files = glob.glob(os.path.join(config.RAW_DATA_DIR, f"book_lists_{YEAR}/*.csv"))  

# Read all CSV files into a single dataframe
df_list = [pd.read_csv(file) for file in csv_files]

# Concatenate all dataframes
combined_df = pd.concat(df_list, ignore_index=True)

# Remove duplicates based on all columns
combined_df = combined_df.drop_duplicates()

# Save the cleaned dataframe to a new CSV file
combined_df.to_csv(os.path.join(config.RAW_DATA_DIR, f"combined_books_list_{YEAR}.csv"), index=False)

print("All CSV files combined and duplicates removed.")

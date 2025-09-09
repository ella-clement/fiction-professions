import os
import pandas as pd
import config

FILE_PATH = os.path.join(config.RAW_DATA_DIR, "book_list.csv")

df = pd.read_csv(FILE_PATH, dtype=str)
df_cleaned = df.drop_duplicates(subset=["Title", "Author"], keep="first")
df_cleaned.to_csv(FILE_PATH, index=False)

print(f"Cleaned file saved. {len(df_cleaned)} unique books remain.")

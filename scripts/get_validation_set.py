import pandas as pd
from sklearn.model_selection import train_test_split
import config

df = pd.read_csv(os.path.join(config.DATA_DIR, 'book_list_with_metadata.csv'))

# Randomly select 10% of the rows (without replacement)
df_sampled = df.sample(frac=0.1, random_state=42)

# Split the sampled rows into test and validation sets (50% for each)
test_set, validation_set = train_test_split(df_sampled, test_size=0.5, random_state=42)

test_set = test_set.reset_index(drop=True)
validation_set = validation_set.reset_index(drop=True)

test_set.to_csv(os.path.join(config.DATA_DIR, 'test_set.csv',index=False))
validation_set.to_csv(os.path.join(config.DATA_DIR, 'validation_set.csv',index=False))

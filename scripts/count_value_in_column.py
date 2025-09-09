import pandas as pd

def count_value_in_column(csv_file, column_name, value):
    df = pd.read_csv(csv_file,on_bad_lines='skip', quotechar='"')
    
    if column_name not in df.columns:
        print(f"Error: Column '{column_name}' not found in the CSV file.")
        return
    
    column_length = len(df[column_name])    
    value_count = df[column_name].value_counts().get(value, 0)
    value_fraction = value_count / column_length
    
    print(f"Value '{value}' appears {value_count} times in column '{column_name}'.")
    print(f"Length of column '{column_name}': {column_length}")
    print(f"Fraction prevalence of value '{value}': {value_fraction:.4f}")


def count_unique_values_in_column(csv_file, column_name):
    df = pd.read_csv(csv_file,on_bad_lines='skip', quotechar='"')
    
    if column_name not in df.columns:
        print(f"Error: Column '{column_name}' not found in the CSV file.")
        return
    
    unique_values_count = df[column_name].nunique()
    print(f"Number of unique values in column '{column_name}': {unique_values_count}")

CSV_FILE = os.path.join(config.DATA_DIR, 'book_list_with_metadata.csv')  
COLUMN_NAME = 'Summary'  
VALUE = 0  

count_value_in_column(CSV_FILE, COLUMN_NAME, VALUE)


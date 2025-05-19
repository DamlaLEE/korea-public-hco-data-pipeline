import os
import pandas as pd
import warnings
import re

def load_and_merge_files(
    folder_path,
    file_type="xlsx",
    max_files=None,
    sort_by_time=False
):
    """
    Load and merge multiple xlsx or csv files from a folder.

    Parameters:
    - folder_path (str): directory path containing the files
    - file_type (str): 'xlsx' or 'csv'
    - max_files (int or None): number of recent files to load, or all if None
    - sort_by_time (bool): if True, load recent files based on modified time

    Returns:
    - pd.DataFrame or None
    """

    if file_type not in ("xlsx", "csv"):
        raise ValueError("Only 'xlsx' and 'csv' file types are supported.")

    # 1. List matching files
    all_files = [
        os.path.join(folder_path, f)
        for f in os.listdir(folder_path)
        if f.endswith(f".{file_type}")
    ]

    if sort_by_time:
        all_files = sorted(all_files, key=os.path.getmtime, reverse=True)

    if max_files is not None:
        all_files = all_files[:max_files]

    print(f"📁 Found {len(all_files)} {file_type.upper()} file(s) to load:")

    for f in all_files:
        print(" -", os.path.basename(f))

    # 2. Read files
    df_list = []
    for file in all_files:
        try:
            if file_type == "xlsx":
                df = pd.read_excel(file)
            else:
                df = pd.read_csv(file)

            df["source_file"] = os.path.basename(file)
            df_list.append(df)
        except Exception as e:
            print(f"❌ Failed to read {file}: {e}")

    # 3. Merge
    if df_list:
        merged_df = pd.concat(df_list, ignore_index=True)
        print(f"✅ Merged shape: {merged_df.shape}")
        return merged_df
    else:
        print("❌ No files were merged.")
        return None

def extract_doctor_counts(text):
    try:
        doctor = int(re.search(r"의사\s*:\s*(\d+)", text).group(1))
    except:
        doctor = None
    try:
        dentist = int(re.search(r"치과의사\s*:\s*(\d+)", text).group(1))
    except:
        dentist = None
    try:
        korean_med = int(re.search(r"한의사\s*:\s*(\d+)", text).group(1))
    except:
        korean_med = None
    return pd.Series([doctor, dentist, korean_med])

def seperate_data(dataframe, column_name_new, column_name_raw, num):
    dataframe[column_name_new] = dataframe[column_name_raw].apply(
            lambda x: x.split("_")[num-1] if len(x.split("_")) >= num else None)
    
def extract_region_info(address):
    try:
        parts = address.split()
        province = parts[0] if len(parts) > 0 else None
        city = parts[1] if len(parts) > 1 else None
    except:
        province, city = None, None
    return pd.Series([province, city])

def get_top_hospitals_by_staff(df, category, top_n):
    filtered_df = df[df['category'] == category]
    filtered_df = filtered_df.sort_values(by='total_medical_staff', ascending=False)
    return filtered_df.head(top_n)
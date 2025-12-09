import pandas as pd
from fuzzywuzzy import fuzz
import os

def extract_address_components(address):
    """
    Extract the street number, street name, and city from an address string.

    :param address: The full address as a string in the format "number street, city".
    :return: A tuple (street_number, street_name, city).
    """

    if not isinstance(address, str):
        return '', '', ''
    try:
        parts = address.split(',')
        street_parts = parts[0].strip().split()
        street_number = street_parts[0] if street_parts[0].isdigit() else ''
        street_name = ' '.join(street_parts[1:]) if street_parts[0].isdigit() else parts[0].strip()
        city = parts[1].strip() if len(parts) > 1 else ''
        return street_number, street_name, city
    except:
        return '', '', ''

def remove_apartment_info(address):
    """
    Remove apartment or unit information from an address string.

    :param address: Address string that may contain apartment/unit info.
    :return: Address string containing only street and city.
    """

    if not isinstance(address, str):
        return address
    parts = address.split(',')
    if len(parts) > 1:
        return ','.join(parts[:2])  # Return only the street address and city
    return address

def calculate_weighted_score(source_address, target_address, street_name_weight):
    """
    Compute a weighted similarity score between two addresses.

    :param source_address: Address from source dataset.
    :param target_address: Address from target dataset.
    :param street_name_weight: Weight assigned to street name similarity.
    :return: Weighted similarity score as a float.

    """
    source_street_number, source_street_name,source_city = extract_address_components(source_address)
    target_street_number, target_street_name, target_city = extract_address_components(target_address)

    street_name_score = fuzz.token_set_ratio(source_street_name, target_street_name)
    city_score = fuzz.token_set_ratio(source_city, target_city)
    street_number_score = fuzz.token_set_ratio(source_street_number, target_street_number)

    weighted_score = (street_name_weight * street_name_score +
                      0.32 * street_number_score + 0.08 * city_score)
    return weighted_score

source_df = pd.read_excel("artifacts/source_with_new_address.xlsx")
target_df = pd.read_excel("artifacts/target_with_new_address.xlsx")

if 'Address' not in source_df.columns or 'Address' not in target_df.columns:
    raise ValueError("The 'Address' column does not exist in one of the dataframes.")

source_df['Modified Address'] = source_df['Address'].apply(remove_apartment_info)
target_df['Modified Address'] = target_df['Address'].apply(remove_apartment_info)

source_df['Address'] = source_df['Modified Address']
target_df['Address'] = target_df['Modified Address']

target_addresses = target_df['Modified Address'].dropna().tolist()
source_addresses = source_df['Modified Address'].dropna().tolist()

threshold = 85.5  

street_name_weight = 0.60  #

matching_results = []

# find closest match for each address in Source from Target addresses using weighted similarity scores
for source_address in source_addresses:
    best_match = None
    highest_score = 0
    
    for target_address in target_addresses:
        weighted_score = calculate_weighted_score(source_address, target_address, street_name_weight)
        
        if weighted_score > highest_score:
            best_match = target_address
            highest_score = weighted_score
    
    if best_match and highest_score >= threshold:
        matching_results.append((source_address, best_match, highest_score))

matches_df = pd.DataFrame(matching_results, columns=['Source Address', 'Closest Target Address', 'Similarity Score'])

column_mapping = {
    'pH Before Acidification 1': 'pH_before_acidification1',
    'pH After Acidification 1': 'pH_after_acidification1',
    'Conductivity 1 (µS/cm) ': 'conductivity1_uscm',  
    'Turbidity 1 (NTU)': 'turbidity1_NTU',
    'Pb of AAS 1 (ppb) ': 'Pb_of_AAS1_ppb', 
    'Cu of AAS 1 (ppm)': 'Cu_of_AAS1_ppm',
    'Pb of E-Tongue 1 (ppb)': 'Pb_of_E_Tongue1_ppb',
    'Cu of E-Tongue 1 (ppm)': 'Cu_of_E_Tongue1_ppm',
    'pH Before Acidification 5': 'pH_before_acidification5',
    'pH After Acidification 5': 'pH_after_acidification5',
    'Conductivity 5 (µS/cm) ': 'conductivity5_uscm',  
    'Turbidity 5 (NTU)': 'turbidity5_NTU',
    'Pb of AAS 5 (ppb)': 'Pb_of_AAS5_ppb',
    'Cu of AAS 5 (ppm)': 'Cu_of_AAS5_ppm',
    'Pb of E-Tongue 5 (ppb)': 'Pb_of_E_Tongue5_ppb',
    'Cu of E-Tongue 5 (ppm)': 'Cu_of_E_Tongue5_ppm'
}

# process the first match for data transfer
if not matches_df.empty:
    for _, match_row in matches_df.iterrows():
        source_address = match_row['Source Address']
        target_address = match_row['Closest Target Address']
        
        # find Source row and Target row by address
        source_row = source_df[source_df['Address'] == source_address]
        target_row = target_df[target_df['Address'] == target_address]

        if not source_row.empty and not target_row.empty:
            print(f"Performing data transfer for:\nSource Address: {source_address}\nTarget Address: {target_address}")

            for source_col, target_col in column_mapping.items():
                if source_col in source_row.columns and target_col in target_row.columns:
                    target_df.at[target_row.index[0], target_col] = source_row.iloc[0][source_col]
        else:
            print(f"No valid rows found in either Source or Target for the match:\nSource Address: {source_address}\nTargetAddress: {target_address}")

os.makedirs("artifacts", exist_ok=True)

source_df.to_excel("artifacts/source_with_new_address.xlsx", index=False)
target_df.to_excel("artifacts/target_with_new_address.xlsx", index=False)

print("Modified address columns saved back to their respective files with apartment number removed from address.")

target_df.drop(columns=['Address', 'Modified Address'], inplace=True)

os.makedirs("output", exist_ok=True)

target_df.to_excel("output/target_with_updated_info.xlsx", index=False)
print("Data transfer completed. Updated Target data saved to 'target_with_updated_info.xlsx'")


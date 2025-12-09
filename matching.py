import pandas as pd
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from data_transfer import extract_address_components, remove_apartment_info, calculate_weighted_score
import os

os.makedirs("artifacts", exist_ok=True)

source_df = pd.read_excel("artifacts/source_with_new_address.xlsx")
target_df = pd.read_excel("artifacts/target_with_new_address.xlsx")

if 'Address' not in source_df.columns or 'Address' not in target_df.columns:
    raise ValueError("The 'Address' column does not exist in one of the dataframes.")

source_df['Address'] = source_df['Address'].apply(remove_apartment_info)
target_df['Address'] = target_df['Address'].apply(remove_apartment_info)

target_addresses = target_df['Address'].dropna().tolist()
source_addresses = source_df['Address'].dropna().tolist()

threshold = 85.5  

street_name_weight = 0.60 

matching_results = []
matched_target_set = set()

for source_address in source_addresses:
    best_match = None
    highest_score = 0
    
    for target_address in target_addresses:
        weighted_score = calculate_weighted_score(source_address, target_address, street_name_weight)
        
        if weighted_score > highest_score:
            best_match = target_address
            highest_score = weighted_score
    
    if best_match and highest_score >= threshold and best_match not in matched_target_set:
        matching_results.append((source_address, best_match, highest_score))
        matched_target_set.add(best_match)
    else:
        closest_match = best_match if best_match else None
        similarity_score = highest_score if best_match else 0
        matching_results.append((source_address, closest_match, similarity_score))

matches_df = pd.DataFrame(matching_results, columns=['Source Address', 'Closest Target Address', 'Similarity Score'])

matches_df.to_excel("artifacts/address_matching_results_85.5.xlsx", index=False)
print("Matching completed and results saved to 'address_matching_results_85.5.xlsx'")

matched_count = matches_df[matches_df['Similarity Score'] >= threshold].shape[0]
not_matched_count = len(source_addresses) - matched_count

print(f"Number of addresses matched (Yes): {matched_count}")
print(f"Number of addresses not matched (No): {not_matched_count}")

total_addresses = len(source_addresses)
match_percentage = (matched_count / total_addresses) * 100

print(f"Percentage of addresses matched: {match_percentage:.2f}%")

matched_addresses = matches_df[matches_df['Similarity Score'] >= threshold]
not_matched_addresses = matches_df[matches_df['Similarity Score'] < threshold]

matched_addresses = matched_addresses.sort_values(by='Similarity Score')
not_matched_addresses = not_matched_addresses.sort_values(by='Similarity Score')

matched_addresses.to_excel("artifacts/address_matched_85.5.xlsx", index=False)
not_matched_addresses.to_excel("artifacts/address_not_matched_85.5.xlsx", index=False)

print("Matched addresses saved to 'address_matched_85.5.xlsx'")
print("Not matched addresses saved to 'address_not_matched_85.5.xlsx'")

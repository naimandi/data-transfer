# Drinking Water Quality Data Transfer

This project automates the process of transferring drinking water quality data from a source dataset to a target dataset. 

## Data 
Both the source and target datasets contains drinking water quality measurements collected from Massachusetts and New Hampshire. 

**Source Data:** (Excel): contains updated data

**Filename:** `source_data.xlsx`

**Columns include:** `Batch`, `Sample`, `Street Number`, `Street Name`, `Apt`, `City`, `State`, `Zip Code`,  along with various pH, conductivity, turbidity, Pb/Cu measurements, etc.


**Target Data** (CSV): where the data will be transferred and consolidated.

**Filename:** `target_data.csv`

**Columns include:** `apt`, `batch`, `city`, `sample`, `state`, `street_name`,`street_num`, `zip`, along with corresponding pH, conductivity, turbidity, and Pb/Cu measurement fields.

## Workflow

1. **Clean and Standardize Columns:**  
    Normalize columns relevant for matching rows from both datasets ( street name, number, ZIP, state, city).  

2. **Concatenate Address Components:**  
   Combine street number, street name, apartment (optional), city, state, and ZIP into a single `Address` column for both datasets. 

3. **Match Addresses:**  
   Use a **weighted fuzzy similarity score** to match addresses. Weights are applied as follows:  
   - Street Name: 60%  
   - Street Number: 32%  
   - City: 8%  

    A match is considered valid if the weighted similarity score meets or exceeds a threshold of **85.5**.  

4. **Transfer Data:**  
For each matched address, transfer water quality measurements from the source dataset to the target dataset. Addresses that do not meet the threshold are not automatically transferred and may require manual review.

5. **Optional:** Optional Matching Reports  
   This step uses a weighted fuzzy matching algorithm to identify the closest matches between the source dataset and the target dataset based on cleaned addresses. It produces files wiht a list of **matched** and **non-matched** addresses, allowing you to review which rows were successfully matched and which may need to be transferred manually because they did not meet the address matching threshold.


## Scripts

`clean.py`: Cleans and standardizes address-related fields in the source and target, concatenates them into a unified `Address` column, and saves the cleaned datasets for downstream processing.
output files:
- `artifacts/source_with_new_address.xlsx`  
- `artifacts/target_with_new_address.xlsx`  

`data_transfer.py`: Matches addresses between the cleaned source data and target data using a weighted fuzzy similarity score, transfers measurement data from the source to the target for matched addresses, and saves the updated dataset for further use.
output files:
- `output/target_with_updated_info.xlsx`
- `artifacts/source_with_new_address.xlsx`(updated with `Modified Address`, which is the address with apartment/unit information removed for matching)
- `artifacts/target_with_new_address.xlsx` (updated with `Modified Address`)

`matching.py`:  Performs fuzzy matching between source and target `Address` columns using a weighted similarity score, identifies matched and unmatched addresses based on a threshold, and saves the results for further analysis.
output files:
- `artifacts/address_matching_results_85.5.xlsx` – addresses above the threshold. 
- `artifacts/address_matched_85.5.xlsx` –  addresses above the threshold sorted by similarity score
- `artifacts/address_not_matched_85.5.xlsx` – addresses below the threshold.  


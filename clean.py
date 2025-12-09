import pandas as pd
import re
import os

source_df = pd.read_excel("source_data.xlsx", dtype={'Zip Code': str})
target_df = pd.read_csv("target_data.csv")

def clean_street_name(name):
    """
    Standardize a street name by removing quotes, normalizing whitespace,
    expanding common abbreviations (e.g., "St" → "Street"), and applying
    title-case formatting.

    :param name: Raw street name value from the dataset.
    :return: Cleaned and standardized street name as a string.
    """
    if pd.isna(name) or str(name).strip().lower() == 'nan':
        return ''
    name = str(name).strip()  
    name = re.sub(r'^"|"$', '', name)  # remove surrounding quotes
    name = re.sub(r'\s+', ' ', name)  # remove extra whitespaces
    abbreviations = {
        r'\bSt\.?(reet)?\b': 'Street',
        r'\bRd\.?(oad)?\b': 'Road',
        r'\bAve\.?(nue)?\b': 'Avenue',
        r'\bBlvd\.?(oulevard)?\b': 'Boulevard',
        r'\bDr\.?(ive)?\b': 'Drive',
        r'\bCt\.?(ourt)?\b': 'Court',
        r'\bLn\b': 'Lane',
        r'\bCir\.?(cle)?\b': 'Circle',
        r'\bPl\b': 'Place',
        r'\bPlz\b': 'Plaza',
        r'\bPkwy\b': 'Parkway',
        r'\bHwy\b': 'Highway',
        r'\bSq\b': 'Square'
    }
    
    for abbrev, full in abbreviations.items():
        name = re.sub(abbrev, full, name, flags=re.IGNORECASE)
    
    name = re.sub(r'\.\s*$', '', name)  # remove trailing period
    name = name.title()  # capitalize
    
    return name

def clean_state(state):
    """
    Normalize a state field by removing extra characters, standardizing
    whitespace, and converting full names or variants to the two-letter
    postal code (e.g., 'Massachusetts' → 'MA').

    :param state: Raw state value.
    :return: Standardized two-letter state code.
    """
    if pd.isna(state) or state.lower() == 'nan':
        return ''
    state = str(state).strip().lower()  
    state = re.sub(r'^"|"$', '', state)  # remove surrounding quotes if present
    state = re.sub(r'\s+', ' ', state)  # remove extra whitespaces
    state = re.sub(r'\bma\b|massachusetts', 'MA', state, flags=re.IGNORECASE)
    state = re.sub(r'\bnh\b|new hampshire', 'NH', state, flags=re.IGNORECASE)

    return state.upper()  

def clean_apt_number(apt):
    """
    Clean apartment information by removing NaN and whitespace while
    preserving valid apartment identifiers.

    :param apt: Raw apartment number value.
    :return: Cleaned apartment number as a string.
    """
    if isinstance(apt, str) and apt.lower() == 'nan':
        return ''
    if pd.isna(apt):
        return ''
    cleaned_apt = str(apt).strip() 
    return cleaned_apt

def clean_city(city):
    """
    Standardize a city name by handling NaN values and trimming whitespace.

    :param city: Raw city value.
    :return: Cleaned city name.
    """
    if pd.isna(city) or city.lower() == 'nan':
        return ''
    return city.strip()

def clean_zip_code(zip_code):
    """
    Clean a ZIP code by extracting digits and
    and enforcing a five-digit zero-padded format.

    :param zip_code: Raw ZIP code value .
    :return: Five-digit ZIP code as a string.
    """
    if pd.isna(zip_code) or zip_code == '':
        return ''
    
    zip_code = str(zip_code).strip()
    zip_code_digits = re.findall(r'\d+', zip_code)  # extract all digits from the string
    
    if zip_code_digits:
        cleaned_zip = zip_code_digits[-1].zfill(5)  # ensure ZIP code has leading zeros if it's not 5 digits long
    else:
        cleaned_zip = ''

    return cleaned_zip

def clean_street_number(number):
    """
    Normalize a street number by stripping whitespace, removing non-numeric
    characters, and returning only the numeric portion.

    :param number: Raw street number value.
    :return: Cleaned street number as a numeric string.
    """
    number = str(number).strip()  
    number = re.sub(r'^"|"$', '', number)  
    number = re.sub(r'\D', '', number) 
    return number

def clean_and_concatenate_target(target_df):
    """
    Clean individual target csv file address component fields (street number,
    street name, apartment, city, state, ZIP) and concatenate them into
    a standardized full address field. Saves the new DataFrame to
    the 'artifacts' directory.

    :param target_df: Original target csv file as a pandas DataFrame.
    :return: None. Writes output to Excel.
    """
    target_df_copy = target_df.copy()

    target_df_copy['Cleaned_Street_Name'] = target_df_copy['street_name'].apply(clean_street_name)
    target_df_copy['Cleaned_Street_Num'] = target_df_copy['Street_num'].apply(clean_street_number)
    target_df_copy['Cleaned_Apt'] = target_df_copy['apt'].apply(clean_apt_number)
    target_df_copy['Cleaned_Zip'] = target_df_copy['zip'].apply(clean_zip_code)
    target_df_copy['Cleaned_State'] = target_df_copy['state'].apply(clean_state)
    target_df_copy['Cleaned_City'] = target_df_copy['city'].apply(clean_city)

    target_df_copy['Address'] = (
        target_df_copy['Cleaned_Street_Num'] + ' ' +
        target_df_copy['Cleaned_Street_Name'] + ', ' +
        target_df_copy['Cleaned_Apt'] + ', ' +
        target_df_copy['Cleaned_City'] + ', ' +
        target_df_copy['Cleaned_State'] + ' ' +
        target_df_copy['Cleaned_Zip']
    ).str.replace(', ,', ',').str.strip(', ')

    target_df_copy = target_df_copy.drop(columns=['Cleaned_Street_Name', 'Cleaned_Street_Num', 'Cleaned_Apt', 'Cleaned_Zip', 'Cleaned_State', 'Cleaned_City'])

    print("First 50 Rows from Target DataFrame with New Address Column:")
    print(target_df_copy.head(50))

    os.makedirs("artifacts", exist_ok=True)

    target_df_copy.to_excel("artifacts/target_with_new_address.xlsx", index=False)

def clean_and_concatenate_source(source_df):
    """
    Clean individual source excel file address fields (street number,
    street name, apartment, city, state, ZIP) and concatenate them into
    a standardized full address field. Saves the new DataFrame to
    the 'artifacts' directory.

    :param source_df: Original source excel file as a pandas DataFrame.
    :return: None. Writes output to Excel.
    """
    source_df_copy = source_df.copy()

    source_df_copy['Cleaned_Street_Name'] = source_df_copy['Street Name'].apply(clean_street_name)
    source_df_copy['Cleaned_Street_Num'] = source_df_copy['Street Number'].apply(clean_street_number)
    source_df_copy['Cleaned_Apt'] = source_df_copy['Apt'].apply(clean_apt_number)
    source_df_copy['Cleaned_Zip'] = source_df_copy['Zip Code'].apply(clean_zip_code)
    source_df_copy['Cleaned_State'] = source_df_copy['State'].apply(clean_state)
    source_df_copy['Cleaned_City'] = source_df_copy['City'].apply(clean_city)

    source_df_copy['Address'] = (
        source_df_copy['Cleaned_Street_Num'] + ' ' +
        source_df_copy['Cleaned_Street_Name'] + ', ' +
        source_df_copy['Cleaned_Apt'] + ', ' +
        source_df_copy['Cleaned_City'] + ', ' +
        source_df_copy['Cleaned_State'] + ' ' +
        source_df_copy['Cleaned_Zip']
    ).str.replace(', ,', ',').str.strip(', ')

    source_df_copy = source_df_copy.drop(columns=['Cleaned_Street_Name', 'Cleaned_Street_Num', 'Cleaned_Apt', 'Cleaned_Zip', 'Cleaned_State', 'Cleaned_City'])

    print("First 50 Rows from Source DataFrame with New Address Column:")
    print(source_df_copy.head(50))

    os.makedirs("artifacts", exist_ok=True)

    source_df_copy.to_excel("artifacts/source_with_new_address.xlsx", index=False)


clean_and_concatenate_source(source_df)
clean_and_concatenate_target(target_df)

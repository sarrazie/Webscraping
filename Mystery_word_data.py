#%%
import pandas as pd
import numpy as np
import os
import glob
import requests
from io import StringIO

### Install lingua-language-detector
#!pip install lingua-language-detector
from lingua import LanguageDetectorBuilder, Language, IsoCode639_1, IsoCode639_3
import re
import codecs

### Pull and download all csv data sets from the Git repository

def load_data_from_github(repo_url, directory_name):
    # Fetch each CSV file from GitHub and save as data frames
    data_frames = {}
    
    # Get the list of files using GitHub API
    api_url = f'https://api.github.com/repos/{repo_url}/contents/{directory_name}'
    response = requests.get(api_url, headers={"Accept": "application/vnd.github.v3+json"})
    
    if response.status_code == 200:
        files = [item['name'] for item in response.json() if item['type'] == 'file' and item['name'].endswith('.csv')]
        
        for file_name in files:
            url = f'https://raw.githubusercontent.com/{repo_url}/main/{directory_name}/{file_name}'
            #print(f'Downloading file from: {url}')  # Debugging statement to see which files are being downloaded
            
            response = requests.get(url)
            
            if response.status_code == 200:
                df = pd.read_csv(StringIO(response.text))
                data_frames[file_name[:-4]] = df  # Removing '.csv' extension from the key
            else:
                print(f'Error downloading file. Status code: {response.status_code}')  # Debugging statement
    else:
        print(f'Error fetching directory contents. Status code: {response.status_code}')  # Debugging statement
    
    return data_frames

### GitHub repository URL and directory name
github_repo_url = 'sarrazie/Webscraping'
directory_name = 'WebScrapingWorkshop-main'

### Load data frames directly from the GitHub repository
dfs = load_data_from_github(github_repo_url, directory_name)

### Print the resulting dictionary and any debugging statements
print(dfs)

### Transpose all data frames inside the dictionary
transposed_data_frames = {key: df.transpose() for key, df in dfs.items()}

### Assign the correct column names to each data frame
for key, df in transposed_data_frames.items():
    df.columns = df.iloc[0]
    df = df.iloc[1:].reset_index(drop=True)
     
    # Update the dictionary with the modified DataFrame
    transposed_data_frames[key] = df

### Drop rows where a guess is missing
for key, df in transposed_data_frames.items():
    df = df.dropna(subset = ['Guess'])
    transposed_data_frames[key] = df
    
### Define data frame columns in a list for the subsequent loops
df_columns = ['Table Number', 'Guess', 'Mystery Word', 'Move', 'Clues']   #'Mode', 'Speed', 'Language', 'End'
#### Transform unicode into char
def decode_unicode(text):
    return bytes(text, 'utf-8').decode('unicode-escape')

#### Apply the decode unicode function for all dataframe columns ####
for key, df in transposed_data_frames.items():
    for column in df_columns:
        if column == 'Table Number' or column == 'Move':
            pass
        elif column == 'Clues':
            df[column] = df[column].apply(decode_unicode)
            df[column] = df[column].apply(decode_unicode)
        else:
            df[column] = df[column].apply(decode_unicode)
            
    transposed_data_frames[key] = df

#### Concatenate all data sets 
big_df = pd.concat(transposed_data_frames.values(), ignore_index=True)

## Create a data frame containing duplicates 
dup = big_df[big_df.duplicated(subset=['Move', 'Table Number'], keep=False)].sort_values(by=['Table Number', 'Move'])

## Drop duplicates
big_df = big_df.drop_duplicates(subset=['Table Number', 'Move'])

### Detect languages and specify the languages to be either english, german or french (slightly increases accuracy)
languages = [Language.ENGLISH, Language.FRENCH, Language.GERMAN]
detector = LanguageDetectorBuilder.from_languages(*languages).build()

### Apply detect function to the Mystery Word column
big_df['Language'] = big_df['Mystery Word'].apply(detector.detect_language_of)

### Sort data set by Table Number to check whether the detection function worked
big_df = big_df.sort_values(by=['Table Number'])

filename = ('Game_data.csv')
big_df.to_csv(filename, index=False)


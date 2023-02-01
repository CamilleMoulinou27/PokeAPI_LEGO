# -*- coding: utf-8 -*-
"""
Created on Wed Feb 1 10:27:03 2023

@author: Camille Moulinou
"""

##### PACKAGES #####

import pandas as pd
pd.options.mode.chained_assignment = None  
import numpy as np
import requests

##### COLLECT ALL POKÉMON NAMES #####

# Initialization of a pandas DataFrame
df_pokemon_names = pd.DataFrame(columns=["PokemonName"])

# Declaration of the url and params for the request
url = "https://pokeapi.co/api/v2/pokemon/"
params = {'limit': 1008} # This limit is set because Bulbapedia indicates that we have a total of 1008 Pokemon

# Request using the previous variables
response = requests.get(url, params=params)

# Write the data in the DataFrame named df_pokemon_names
if response.status_code != 200: 
    print(response.text)
else:
    data = response.json()

    for item in data['results']:
        tmp_dict = {}
        tmp_dict["PokemonName"] = item["name"]
        df_pokemon_names = df_pokemon_names.append(tmp_dict,ignore_index = True)     
        
##### COLLECT ALL POKÉMON DETAILS #####

# List containing all Pokémon names so that we can use it in a for loop
list_all_pokemon_names = df_pokemon_names.PokemonName.tolist()

# Initialization of a pandas DataFrame
df_pokemon = pd.DataFrame(columns=["PokemonName","PokemonID","BaseExperience","Weight","Height","Order","Slot1TypeName","Slot2TypeName","FrontDefaultSpriteURL","GameNames"])

# Loop on the name of each Pokémon and writing of all details in the DataFrame named df_pokemon
for name in list_all_pokemon_names:
    # Request
    response = requests.get("https://pokeapi.co/api/v2/pokemon/"+name)  
    
    if response.status_code != 200: 
        print(response.text)
    else:
        data = response.json()
      
    tmp_dict = {}
    
    # Collect the name of the slot 1 (and slot 2 if available) type of each Pokémon
    for slot in data["types"]:
        if slot["slot"] == 1:
            slot1_type_name = slot["type"]["name"]
        if slot["slot"] == 2:
            slot2_type_name = slot["type"]["name"]
        else:
            slot2_type_name = None
    
    # Collect the game names where each Pokémon appears
    list_games = []
    if data["game_indices"] is not None:
        for game in data["game_indices"]:
            game_name = game["version"]["name"]
            list_games.append(game_name)
    else:
        game_name = list_games

    # Collect all necessary caracteristics of each Pokémon and insertion in the DataFrame
    tmp_dict["PokemonName"] = data["name"]
    tmp_dict["PokemonID"] = data["id"]
    tmp_dict["BaseExperience"] = data["base_experience"]
    tmp_dict["Weight"] = data["weight"]
    tmp_dict["Height"] = data["height"]
    tmp_dict["Order"] = data["order"]
    tmp_dict["Slot1TypeName"] = slot1_type_name
    tmp_dict["Slot2TypeName"] = slot2_type_name
    tmp_dict["FrontDefaultSpriteURL"] = data["sprites"]["front_default"]
    tmp_dict["GameNames"] = list_games
    df_pokemon = df_pokemon.append(tmp_dict,ignore_index = True)    
    
# Convert the column GameNames to a string (with elements separated by comma and a space) instead of a list
df_pokemon["GameNames"] = [', '.join(map(str, l)) for l in df_pokemon["GameNames"]]
            
##### FILTER POKÉMON THAT APPEAR ONLY IN THE FOLLOWING GAMES: red, blue, leafgreen or white #####

# Create a boolean column indicating if the Pokémon appears in at list one of the selected games
df_pokemon["IsInSelectedGames"] = np.where((df_pokemon["GameNames"].str.contains("red")) | (df_pokemon["GameNames"].str.contains("blue")) | (df_pokemon["GameNames"].str.contains("leafgreen")) | (df_pokemon["GameNames"].str.contains("white")), True, False)

# Filtering on the value of the boolean column, only keeps the Pokémon appearing in the selected games
df_pokemon_filtered = df_pokemon[(df_pokemon["IsInSelectedGames"])]

##### TRANSFORMATIONS #####

# Modify the PokemonName column to capitalize the first letter of the name

df_pokemon_filtered["PokemonName"] = df_pokemon_filtered["PokemonName"].str.capitalize()

# Computation of the Body Mass Index and creation of the new column containing the result
# Weight is in hectograms so we need to convert it to kilograms (division by ten)
# Height is in decimeters so we need to convert it in meters (division by ten)

df_pokemon_filtered["BMI"] = (df_pokemon_filtered["Weight"] / 10) / ((df_pokemon_filtered["Height"] / 10)**2)

# Reorganize the columns and keep only the necessary ones

df_pokemon_filtered = df_pokemon_filtered[["PokemonName","PokemonID","BaseExperience","Weight","Height","BMI","Order","Slot1TypeName","Slot2TypeName","FrontDefaultSpriteURL"]]

# Change the data types to match the API documentation types

df_pokemon_filtered["PokemonID"] = df_pokemon_filtered["PokemonID"].astype(int)
df_pokemon_filtered["BaseExperience"] = df_pokemon_filtered["BaseExperience"].astype(int)
df_pokemon_filtered["Weight"] = df_pokemon_filtered["Weight"].astype(int)
df_pokemon_filtered["Height"] = df_pokemon_filtered["Height"].astype(int)
df_pokemon_filtered["Order"] = df_pokemon_filtered["Order"].astype(int)
df_pokemon_filtered["BMI"] = df_pokemon_filtered["BMI"].astype(float)

# Round the result of BMI to keep only two decimals

df_pokemon_filtered["BMI"] = df_pokemon_filtered["BMI"].round(decimals = 2)

##### SAVING OF THE RESULT IN AN EXCEL FILE #####

writer = pd.ExcelWriter("C:/Users/connectadmin/Documents/LEGO case/LEGO_PokeAPI.xlsx", engine='xlsxwriter')
df_pokemon_filtered.to_excel(writer, sheet_name="PokemonData", index=False)
workbook  = writer.book
worksheet = writer.sheets['PokemonData']
worksheet.set_column('A:A', 20)
worksheet.set_column('B:G', 15)
worksheet.set_column('H:I', 20)
worksheet.set_column('J:J', 80)
writer.save()

print("The export of " + str(df_pokemon_filtered.shape[0]) + " rows has been successful.")

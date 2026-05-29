# Import der notwendigen Module

import pandas as pd
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, text


# Arbeitsverzeichnis auf den Ordner von import.py setzen
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Laden der Rohdaten
filepath = "../data/olympics.csv"
df = pd.read_csv(filepath, sep=";", encoding="cp1252")
df = df[df['Year'] >= 1960].reset_index(drop=True) # Nur Daten ab 1960


# Erstellen der Engine

load_dotenv()
db_url = os.getenv('DATABASE_URL')
engine = create_engine(db_url + "?client_encoding=utf8")


# Tabellen in umgekehrter Reihenfolge leeren
with engine.connect() as conn:
    conn.execute(text("TRUNCATE TABLE fact_medals RESTART IDENTITY CASCADE;"))
    conn.execute(text("TRUNCATE TABLE dim_event RESTART IDENTITY CASCADE;"))
    conn.execute(text("TRUNCATE TABLE dim_athletes RESTART IDENTITY CASCADE;"))
    conn.execute(text("TRUNCATE TABLE dim_countries RESTART IDENTITY CASCADE;"))
    conn.execute(text("TRUNCATE TABLE dim_medal RESTART IDENTITY CASCADE;"))
    conn.execute(text("TRUNCATE TABLE dim_sport RESTART IDENTITY CASCADE;"))
    conn.execute(text("TRUNCATE TABLE dim_date RESTART IDENTITY CASCADE;"))
    conn.commit()


# Laden der Daten in die Tabelle dim_date

df_date = pd.DataFrame()
df_date['year'] = range(df['Year'].min(), df['Year'].max()+1, 1)
df_date['DateID'] = range(1, len(df_date)+1)
df_date = df_date[['DateID', 'year']]

df_date.columns = [col.lower() for col in df_date.columns]

df_date.to_sql('dim_date', engine, if_exists='append', index=False)
print("-- dim_date fertig geladen --")

# Laden der Daten in die Tabelle dim_sport

df_sport = pd.DataFrame()
df_sport['sport'] = df['Sport'].unique()
df_sport['SportID'] = range(1, len(df_sport)+1)
df_sport = df_sport[['SportID', 'sport']]

df_sport.columns = [col.lower() for col in df_sport.columns]

df_sport.to_sql('dim_sport', engine, if_exists='append', index=False)
print("-- dim_sport fertig geladen --")

# Laden der Daten in die Tabelle dim_medal

medal_dict = {
    "medal_name": ["Gold", "Silver", "Bronze"]
}

df_medal = pd.DataFrame(medal_dict)
df_medal['MedalID'] = range(1, len(df_medal)+1)
df_medal = df_medal[['MedalID', 'medal_name']]

df_medal.columns = [col.lower() for col in df_medal.columns]

df_medal.to_sql('dim_medal', engine, if_exists='append', index=False)
print("-- dim_medal fertig geladen --")

# Laden der Daten in die Tabelle dim_athletes

df_athletes = (
    df[['ID', 'Name', 'Sex']].drop_duplicates(subset='ID').reset_index(drop=True)
)

df_athletes = df_athletes.rename(columns={
    'ID': 'AthleteID',
    'Name': 'name',
    'Sex': 'sex'
})

df_athletes.columns = [col.lower() for col in df_athletes.columns]

df_athletes.to_sql('dim_athletes', engine, if_exists='append', index=False)
print("-- dim_athletes fertig geladen --")

# Laden der Daten in die Tabelle dim_countries

df_countries = (
    df[['Country', 'NOC']].drop_duplicates(subset='NOC').reset_index(drop=True)
)

df_countries = df_countries.rename(columns={
    'Country': 'country_name',
    'NOC': 'NOC_code'
})

df_countries['CountryID'] = range(1, len(df_countries)+1)
df_countries = df_countries[['CountryID', 'country_name', 'NOC_code']]

df_countries.columns = [col.lower() for col in df_countries.columns]

df_countries.to_sql('dim_countries', engine, if_exists='append', index=False)
print("-- dim_countries fertig geladen --")

# Laden der Daten in die Tabelle dim_event

df_event = (
    df[['Event', 'Sport']].drop_duplicates(subset=['Event']).reset_index(drop=True)
)

df_event = df_event.merge(
    df_sport[['sportid', 'sport']],
    left_on='Sport',
    right_on='sport',
    how='left'
)

df_event['EventID'] = range(1, len(df_event) + 1)
df_event = df_event.rename(columns={'Event': 'name'})
df_event = df_event[['EventID', 'sportid', 'name']]

df_event.columns = [col.lower() for col in df_event.columns]

df_event.to_sql('dim_event', engine, if_exists='append', index=False)
print("-- dim_event fertig geladen --")

# Laden der Daten in die Tabelle fact_medals

df_facts_medals = (
    df[['ID', 'Year', 'Event', 'Medal', 'Age', 'Height', 'Weight', 'NOC']].drop_duplicates(subset=['ID', 'Event', 'Year']).reset_index(drop=True)
)

df_facts_medals = df_facts_medals.merge(
    df_date[['dateid', 'year']],
    left_on='Year',
    right_on='year',
    how='left'
)

df_facts_medals = df_facts_medals.merge(
    df_event[['eventid', 'name']],
    left_on='Event',
    right_on='name',
    how='left'
)

df_facts_medals = df_facts_medals.merge(
    df_medal[['medalid', 'medal_name']],
    left_on='Medal',
    right_on='medal_name',
    how='left'
)

df_facts_medals = df_facts_medals.merge(
    df_countries[['countryid', 'noc_code']],
    left_on='NOC',
    right_on='noc_code',
    how='left'
)

df_facts_medals['FactID'] = range(1, len(df_facts_medals) + 1)
df_facts_medals = df_facts_medals.rename(columns={
    'ID': 'athlete',
    'eventid': 'event',
    'medalid': 'medal',
    'Age': 'age_at_event',
    'Height': 'body_size_at_event',
    'Weight': 'body_weight_at_event',
    'countryid': 'country_at_event'
    })
df_facts_medals = df_facts_medals[['FactID', 'dateid', 'athlete', 'event', 'medal', 'age_at_event', 'body_size_at_event', 'body_weight_at_event', 'country_at_event']]

df_facts_medals.columns = [col.lower() for col in df_facts_medals.columns]

df_facts_medals.to_sql('fact_medals', engine, if_exists='append', index=False)
print("-- fact_medals fertig geladen --")


# Überprüfung der übertragenen Zeilenlängen:

print(f"dim_date:      {len(df_date)}")
print(f"dim_sport:     {len(df_sport)}")
print(f"dim_medal:     {len(df_medal)}")
print(f"dim_athletes:  {len(df_athletes)}")
print(f"dim_countries: {len(df_countries)}")
print(f"dim_event:     {len(df_event)}")
print(f"fact_medals:   {len(df_facts_medals)}")
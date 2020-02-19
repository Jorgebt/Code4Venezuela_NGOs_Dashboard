#!/usr/bin/env python
import re
import pandas as pd
from google.cloud import bigquery
import os
import urllib.request


def get_df_from_bigquery():
    url = 'https://storage.googleapis.com/angostura-public/hult-hackathon-key.json'
    urllib.request.urlretrieve(url, './hult-hackathon-key.json')
    # Second, we add the key to our environment
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = './hult-hackathon-key.json'
    QUERY = ('select * from `angostura_dev`.eh_health_survey_response')
    client = bigquery.Client()
    df = client.query(QUERY).to_dataframe()
    return df


def create_year_week_df(df):
    """Create a "year_week" column so that you can sort reports by time order."""

    def report_week_to_date(report_week):
        week, year = report_week.split(' del ')
        year = str(year)
        week = str(int(week) - 1).zfill(2)
        return year + '-' + week

    df['year_week'] = df['report_week'].apply(report_week_to_date)
    report_counts = df.groupby(['hospital_code', 'year_week']).count()['timestamp'].unstack().unstack().reset_index()
    report_counts = report_counts.rename(axis=1, mapper={0: 'report_count'})
    return df.merge(report_counts, left_on=['hospital_code','year_week'], right_on=['hospital_code','year_week'])


def deduplicate_reports(df):
    """De-duplicate the reports by only using the latest submitted report per hospital and week."""
    # Convert timestamp column from strings to datetimes
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df.loc[df.groupby(['hospital_code', 'year_week']).idxmax(axis=0)['timestamp']]


def convert_categorical_to_numeric(cat, converter):
    """Convert values from categorical to numeric."""
    return converter[cat]

med_cat_convert = {
    'Nunca ha existido': None,
    'No hubo': 0,
    'Entre 1 y 2 días': 1,
    'Entre 3 y 5 días': 2,
    'Todos los días': 3
}

op_cat_convert = {
    'No existe': None,
    'Nunca ha existido': None,
    'No operativa': 0,
    'Menos de 3 de días': 1,
    'Entre 3 y 5 días': 2,
    'Todos los días': 3
}


def create_ordinal_columns_for_medicine(df):
    """Create a corresponding numeric (ordinal) column for each of the medicine supply columns.
    Also calculate an aggregated rating of medical supplies."""
    cols = list(df.columns)
    med_cols = []
    ordinal_cols = []
    for c in cols:
        m = re.search('(er|sx)_avail_.*', c)
        if m:
            med_cols.append(c)
    for col in med_cols:
        new_colname = col + '_ordinal'
        ordinal_cols.append(new_colname)
        df[new_colname] = df[col].apply(lambda x: convert_categorical_to_numeric(x, med_cat_convert))
    med_summary = df[ordinal_cols].apply(lambda x: sum(x) / len(x), axis=1)
    df['medical_supply_summary'] = med_summary
    return df


def create_ordinal_columns_for_operability(df):
    """Create a corresponding numeric (ordinal) column for each of the operability columns."""
    cols = list(df.columns)
    op_cols = []
    ordinal_cols = []
    for c in cols:
        m = re.search('(operability_.*)', c)
        if m:
            op_cols.append(c)
    for col in op_cols:
            new_colname = col + '_ordinal'
            ordinal_cols.append(new_colname)
            try:
                df[new_colname] = df[col].apply(lambda x: convert_categorical_to_numeric(x, op_cat_convert))
            except:
                print(col)
                raise
    return df


def add_country_venezuela(df):
    """Add country "Venezuela for all columns for ease of geolocation plotting in Tableau."""
    df['country'] = 'Venezuela'


df = get_df_from_bigquery()

### Data Cleaning Steps ###
# 1) Create an extra string column with the report week, formatted as "[Year]-[Week of Year]". This allows for sorting the data in report week order.
df = create_year_week_df(df)
# 2) De-duplicate the reports by only using the latest submitted report by hospital and week.
df = deduplicate_reports(df)
# 3) Create a corresponding numeric (ordinal) column for each of the medicine supply fields. Also calculate an aggregated rating of medical supplies.
# We replaced "never existed" values (No existe, Nunca ha existido), with null values, then set the rest of the categories on a 0 - 3 scale.
df = create_ordinal_columns_for_medicine(df)
# 4) Similarly, create a corresponding numeric column for each of the operability fields.
df = create_ordinal_columns_for_operability(df)
add_country_venezuela(df)
df.to_csv('cleaned_survey_dataset.csv')

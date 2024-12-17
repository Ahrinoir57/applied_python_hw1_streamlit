import streamlit as st
import plotly.express as px

import pandas as pd
import requests
import numpy as np

from datetime import date 
import time


def get_current_weather_data(city, api_key):
    response = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric')
    time.sleep(0.5)

    return response

def is_anomaly(t, t_mean, t_std):
    return abs(t - t_mean) > 2 * t_std


def get_season_from_date(date):
    month = date.month
    if month in [12, 1, 2]:
        return 'winter'
    elif month in [3, 4, 5]:
        return 'spring'
    elif month in [6, 7, 8]:
        return 'summer'
    else:
        return 'autumn'


st.title("Streamlit with OpenWeatherAPI (Ahrinoir)")

st.header("Data download")

uploaded_file = st.file_uploader("Choose CSV-file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write("Data preview:")
    st.dataframe(df)
else:
    st.write("Please, download CSV-файл.")


if uploaded_file is not None:
    st.header("Historical data by city")

    df['rolling_temperature'] = df.groupby('city')['temperature'].apply(lambda x: x.rolling(window=30, min_periods=1).mean()).reset_index().set_index('level_1').sort_index()['temperature']
    df['mean_temperature'] = df.groupby(['city', 'season'])['temperature'].transform("mean")
    df['std_temperature'] = df.groupby(['city', 'season'])['temperature'].transform("std")
    df['is_anomaly'] = df.apply(lambda row: is_anomaly(row['temperature'], row['mean_temperature'], row['std_temperature']), axis=1)


    cities = df['city'].unique()
    seasons = ['winter', 'spring', 'summer', 'autumn']

    chosen_city = st.selectbox('city', cities)

    city_df = df[df['city'] == chosen_city]

    #Temperature graph with anomalies

    fig = px.scatter(city_df, x='timestamp', y='temperature', color='is_anomaly',
                      color_discrete_sequence=['blue', 'red'], title = 'Temperature graph')

    st.plotly_chart(fig)


    #Rolling temperature graph

    fig = px.scatter(city_df, x='timestamp', y='rolling_temperature',
                      color_discrete_sequence=['blue'], title='Smoothed temperature graph')

    st.plotly_chart(fig)


    st.header("Current Data")

    today = date.today()
    cur_season = get_season_from_date(today)

    st.write(f'Current date is {today} and current season is {cur_season}')

    api_key = st.text_input("Insert OpenWeatherAPI key")

    if api_key != '':
        response = get_current_weather_data('Moscow', api_key)
        if response.status_code == 200:
            api_key_valid = True
            st.write('API key is valid')

            current_data = {'city': [], 'temperature': [], 'is_anomaly': []}

            for city in cities:
                response = get_current_weather_data(city, api_key)
                curr_t = response.json()['main']['temp']
                current_data['city'].append(city)
                current_data['temperature'].append(curr_t)

                part_df = df[(df['city'] == city) & (df['season'] == cur_season)]
                try:
                    t_mean = part_df['mean_temperature'][0]
                    t_std = part_df['std_temperature'][0]

                    current_data['is_anomaly'].append(is_anomaly(curr_t, t_mean, t_std))
                except:
                    print(city, cur_season)
                    current_data['is_anomaly'].append(False)
            
            current_df = pd.DataFrame(data=current_data)

            st.header('Current temperatures')
            st.dataframe(current_df)

        else:
            api_key_valid = False
            st.error('{"cod":401, "message": "Invalid API key. Please see https://openweathermap.org/faq#error401 for more info."}')






import streamlit as st
import pandas as pd
import requests

def get_current_weather_data(city, api_key):
    response = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric')

    return response

st.title("Streamlit with OpenWeatherAPI")

st.header("Data download")

uploaded_file = st.file_uploader("Choose CSV-file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write("Data preview:")
    st.dataframe(df)
else:
    st.write("Please, download CSV-файл.")


if uploaded_file is not None:
    st.header("Выбор города")

    cities = df['city'].unique()
    st.selectbox('city', cities)

    api_key = st.text_input("Insert OpenWeatherAPI key")

    if api_key != '':
        response = get_current_weather_data('Moscow', api_key)
        if response.status_code == 200:
            st.write('API key is valid')
        else:
            st.error('{"cod":401, "message": "Invalid API key. Please see https://openweathermap.org/faq#error401 for more info."}')




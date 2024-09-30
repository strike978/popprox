import streamlit as st
import pandas as pd
import numpy as np
from scipy.spatial.distance import (
    braycurtis, cityblock, euclidean
)

# Load CSV data with specified encoding
data = pd.read_csv('Modern Ancestry.txt', header=None, encoding='latin1')

# Split the first column to get population names
data[0] = data[0].str.split(':').str[-1]

# Extract population names and numerical data
populations = data[0].values
numerical_data = data.iloc[:, 1:].values

st.set_page_config(page_title='PopProx',
                   page_icon=':earth_americas:', layout='wide')
st.title('PopProx')
st.caption('Select One Population to Compare with Others')

selected_population = st.selectbox('Select Population', populations, key='pop')
use_custom_coordinates = st.checkbox('Use Custom Coordinates')
user_coordinates = st.text_input(
    'Enter Your Coordinates (comma-separated)', '')

col1, col2 = st.columns([3, 1])
with col1:
    distance_metric = st.selectbox('Select Distance Metric', [
                                   'Bray-Curtis', 'Cityblock', 'Euclidean'])
with col2:
    limit = st.number_input('Number of Closest Populations to Display',
                            min_value=1, max_value=len(populations)-1, value=10)

index_selected = np.where(populations == selected_population)[0][0]

if use_custom_coordinates:
    if user_coordinates:
        try:
            user_coordinates = np.array(
                [float(x.strip()) for x in user_coordinates.split(',')[1:]])
            if len(user_coordinates) != numerical_data.shape[1]:
                raise ValueError(
                    "The number of coordinates entered does not match the expected number.")
            selected_data = user_coordinates
        except ValueError as e:
            st.error(f"Invalid coordinates format: {
                     e}. Please enter comma-separated numerical values.")
            st.stop()
    else:
        st.error("Please enter your coordinates.")
        st.stop()
else:
    selected_data = numerical_data[index_selected]

distances = []
for i, population in enumerate(populations):
    if not use_custom_coordinates and i == index_selected:
        continue
    if distance_metric == 'Bray-Curtis':
        dist = braycurtis(selected_data, numerical_data[i])
    elif distance_metric == 'Cityblock':
        dist = cityblock(selected_data, numerical_data[i])
    elif distance_metric == 'Euclidean':
        dist = euclidean(selected_data, numerical_data[i])
    distances.append((population, dist))

distances.sort(key=lambda x: x[1])
closest_populations = distances[:limit]

st.write(f'The top {limit} populations closest to {
         selected_population if not use_custom_coordinates else "your coordinates"} using {distance_metric} distance are:')
table_data = [{"Population": population, "Percentage": f'{
    100 - (dist * 100):.2f}%'} for population, dist in closest_populations]
st.table(table_data)

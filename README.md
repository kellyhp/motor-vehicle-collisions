# Motor Vehicle Collisions in NYC

Live server: [Motor Vehicle Collisions in NYC](https://motor-vehicle-collisions-within-nyc.streamlit.app)<br>
Last Updated: July 2024

## Table of Contents
- [General Info](#general-info)
- [Reflection](#reflection)
- [Technologies](#technologies)
- [Setup](#setup)

## General Info
Motor Vehicle Collisions in NYC is an interactive dashboard designed to analyze and visualize motor vehicle collisions across New York City. 
The dashboard utilizes various data visualizations to provide insights into the frequency, locations, and causes of accidents. 
Users can explore the data through interactive maps, bar charts, line graphs, and parallel categories diagrams. 
This tool aims to help city planners, local authorities, and the general public understand collision patterns and make informed decisions to improve road safety.

## Reflection
The development of this dashboard highlighted several areas for future enhancement. Optimizing the data loading and visualization rendering processes 
can improve user experience by reducing load times and increasing responsiveness. Additionally, integrating more granular data, such as weather conditions 
and traffic volumes, could provide deeper insights into the factors contributing to collisions. Implementing real-time data updates and expanding the 
dataset to include more recent incidents can keep the dashboard current and relevant.

## Technologies
Project is created with:
- **Streamlit**
- **Pandas**
- **Plotly**
- **Pydeck**
- **Python**

## Setup
To run this project, follow these steps:
```
$ git clone https://github.com/kellyhp/motor-vehicle-collisions.git
$ cd motor-vehicle-collisions
$ pip install -r requirements.txt
$ streamlit run app.py
```

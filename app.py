import streamlit as st
import pandas as pd
import pydeck as pdk
import numpy as np
import plotly.express as px
import plotly.graph_objects as go


DATA_URL = (
    "Motor_Vehicle_Collisions_-_Crashes.csv"
)

st.title("Motor Vehicle Collisions in New York City")
st.markdown("**Kelly Phan - July 2024**")
st.markdown("This Streamlit dashboard provides a comprehensive analysis of motor vehicle"
        "collisions in New York City  🏙️💥🚗, offering insights into the frequency, locations, and causes of accidents."
        "The visualizations include **interactive maps, bar charts, line graphs, and parallel categories diagrams**, " 
        "each designed to highlight different aspects of collision data. These can provide a multi-faceted view of motor vehicle collisions in NYC, "
        "offering valuable insights for traffic management, urban planning, and public safety. By analyzing these data "
        "points, stakeholders can make informed decisions to enhance road safety and reduce the number of traffic-related injuries and fatalities.")


@st.cache_data(persist=True)
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows, parse_dates=[['CRASH_DATE', 'CRASH_TIME']])
    data.dropna(subset=['LATITUDE', 'LONGITUDE'], inplace=True)
    lowercase = lambda x:str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    data.rename(columns={'crash_date_crash_time': 'date/time'}, inplace=True)
    return data

data = load_data(100000)
original_data = data

st.header("Where are the most people injured in NYC?")
injured_people = st.slider("Number of npersons injured in vehicle collisions", 0, 19)
filtered_data = data.query("injured_persons >= @injured_people")[["latitude", "longitude"]].dropna(how="any")

if not filtered_data.empty:
    avg_lat = filtered_data['latitude'].mean()
    avg_lon = filtered_data['longitude'].mean()

    st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/light-v9',
        initial_view_state=pdk.ViewState(
            latitude=avg_lat,
            longitude=avg_lon,
            zoom=11,
            pitch=5,
        ),
        layers=[
            pdk.Layer(
                'ScatterplotLayer',
                data=filtered_data,
                get_position='[longitude, latitude]',
                get_color='[200, 30, 0, 160]',
                get_radius=20,
            ),
        ],
    ))
else:
    st.write("No data available for the selected number of injured persons.")

st.markdown("The first visualization is a **scatterplot map** showing locations where the most people are "
            "injured, allowing users to adjust a slider to filter data based on the number of injuries. "
            "This map helps identify hotspots of severe accidents,:blue-background[which can inform targeted safety measures "
            "and infrastructure improvements].")

st.header("How many collisions occur during a given time of day?")
hour = st.slider("Hours to look at", 0, 23)
data = data[data['date/time'].dt.hour == hour]

st.markdown("Vehicle collisions between %i:00 and %i:00" % (hour, (hour + 1) % 24))
midpoint = (np.average(data['latitude']), np.average(data['longitude']))

st.write(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state={
        "latitude" : midpoint[0],
        "longitude" : midpoint[1],
        "zoom" : 11,
        "pitch" : 50,
    },
    layers = [
        pdk.Layer(
            "HexagonLayer",
            data=data[['date/time', 'latitude', 'longitude']],
            get_position =['longitude', 'latitude'],
            radius=100,
            extruded=True,
            pickable=True,
            elevation_scale = 4,
            elevation_range = [0, 1000],
        ),
    ],
))

st.subheader("Breakdown by minute between %i:00 and %i:00" % (hour, (hour + 1) % 24))
filtered = data[
    (data['date/time'].dt.hour >= hour) & (data['date/time'].dt.hour < (hour + 1))
]
hist = np.histogram(filtered['date/time'].dt.minute, bins=60, range=(0, 60))[0]
chart_data = pd.DataFrame({'minute': range(60), 'crashes': hist})
fig = px.bar(chart_data, x='minute', y='crashes', hover_data=['minute', 'crashes'], height=400)
st.write(fig)

st.markdown("A **hexbin map and histogram** break down collisions by time of day, showing patterns "
            "in accident occurrences. Users can adjust the hour to see how collision frequency changes, "
            "which is crucial for understanding peak times and implementing time-specific interventions "
            "such as :blue-background[increased traffic enforcement during high-risk hours].")

st.header("Nuber of collisions in each borough")
borough_counts = original_data['borough'].value_counts().reset_index()
borough_counts.columns = ['borough', 'collisions']
borough = px.bar(borough_counts, x='borough', y='collisions')
st.write(borough)

st.markdown("The **borough-specific bar chart** illustrates the number of collisions in each borough, "
            "highlighting areas with higher accident rates. This can help :blue-background[city planners and local "
            "authorities prioritize resources and safety campaigns in the most affected areas].")

st.header("Collisions Over Time")
data['date'] = data['date/time'].dt.date
collisions_per_day = data['date'].value_counts().sort_index().reset_index()
collisions_per_day.columns = ['date', 'collisions']
col = px.line(collisions_per_day, x='date', y='collisions')
st.write(col)

st.markdown("A **line graph** tracking collisions over time provides a temporal perspective, "
            "showing trends and seasonal variations in accident rates. :blue-background[Identifying these trends "
            "can assist in long-term planning and evaluating the effectiveness of past safety initiatives.]")

st.header("Heatmap of Collisions by Date and Hour from %i:00 to %i:00" % (hour, (hour + 1) % 24))
data['date'] = data['date/time'].dt.date
data['hour'] = data['date/time'].dt.hour + data['date/time'].dt.minute / 60 

heatmap_data = data.groupby(['date', 'hour']).size().reset_index(name='collisions')

tickvals = list(range(24))
ticktext = [f'{hour}:00' for hour in tickvals]

heatmap = px.density_heatmap(
    heatmap_data, 
    x='hour', 
    y='date', 
    z='collisions', 
    color_continuous_scale='Viridis'
)
heatmap.update_xaxes(tickvals=tickvals, ticktext=ticktext, title='hour of day (0-23)')
st.write(heatmap)

st.markdown("The **heatmap of collisions by date and hour** offers a detailed view of when accidents are most frequent, combining temporal and spatial data to reveal critical periods of high risk.")

st.header("Top 10 dangerous streets by affected people")
select = st.selectbox('Affected type of people', ['Pedestrians', 'Cyclists', 'Motorists'])

if select == 'Pedestrians':
    pedestrian_data = original_data.query("injured_pedestrians >= 1 or killed_pedestrians >= 1")
    pedestrian_data = pedestrian_data.groupby('on_street_name').agg({
        'injured_pedestrians': 'sum',
        'killed_pedestrians': 'sum'
    }).reset_index()
    pedestrian_data['affected_pedestrians'] = pedestrian_data['injured_pedestrians'] + pedestrian_data['killed_pedestrians']
    top_pedestrian_streets = pedestrian_data.sort_values(by='affected_pedestrians', ascending=False).dropna(how='any')[:10]
    st.write(top_pedestrian_streets.rename(columns={'injured_pedestrians': 'Injured', 'killed_pedestrians': 'Killed', 'affected_pedestrians': 'Affected'}))
elif select == 'Cyclists':
    cyclist_data = original_data.query("injured_cyclists >= 1 or killed_cyclists >= 1")
    cyclist_data = cyclist_data.groupby('on_street_name').agg({
        'injured_cyclists': 'sum',
        'killed_cyclists': 'sum'
    }).reset_index()
    cyclist_data['affected_cyclists'] = cyclist_data['injured_cyclists'] + cyclist_data['killed_cyclists']
    top_cyclist_streets = cyclist_data.sort_values(by='affected_cyclists', ascending=False).dropna(how='any')[:10]
    st.write(top_cyclist_streets.rename(columns={'injured_cyclists': 'Injured', 'killed_cyclists': 'Killed', 'affected_cyclists': 'Affected'}))
else:
    motorist_data = original_data.query("injured_motorists >= 1 or killed_motorists >= 1")
    motorist_data = motorist_data.groupby('on_street_name').agg({
        'injured_motorists': 'sum',
        'killed_motorists': 'sum'
    }).reset_index()
    motorist_data['affected_motorists'] = motorist_data['injured_motorists'] + motorist_data['killed_motorists']
    top_motorist_streets = motorist_data.sort_values(by='affected_motorists', ascending=False).dropna(how='any')[:10]
    st.write(top_motorist_streets.rename(columns={'injured_motorists': 'Injured', 'killed_motorists': 'Killed', 'affected_motorists': 'Affected'}))

st.markdown("The **top 10 dangerous streets visualization**, categorized by affected people (pedestrians, cyclists, motorists), "
            "points out specific locations with high numbers of injuries and fatalities. "
            ":blue-background[highlightThis information is vital for targeted road safety improvements and public awareness campaigns.]")

def clean_vehicle_type(vehicle_type):
    vehicle_type = vehicle_type.replace('VEHICLE', '').strip()
    return vehicle_type.capitalize()

def clean_vehicle(vehicle_type):
    vehicle_type = vehicle_type.replace('vehicle', '').strip()
    return vehicle_type.capitalize()

filtered_data = data[((data['injured_persons'] > 0) | (data['killed_persons'] > 0)) & 
                     (data['contributing_factor_vehicle_1'] != 'Unspecified')]

top_factors = filtered_data['contributing_factor_vehicle_1'].value_counts().nlargest(3).index
top_vehicles = filtered_data['vehicle_type_1'].value_counts().nlargest(3).index

filtered_data = filtered_data[filtered_data['contributing_factor_vehicle_1'].isin(top_factors) & 
                              filtered_data['vehicle_type_1'].isin(top_vehicles)]

filtered_data['vehicle_type_1'] = filtered_data['vehicle_type_1'].apply(clean_vehicle_type)
filtered_data['vehicle_type_1'] = filtered_data['vehicle_type_1'].apply(clean_vehicle)


injured_data = filtered_data.copy()
injured_data['affected_label'] = 'Injured'
injured_data['affected_count'] = injured_data['injured_persons']

killed_data = filtered_data.copy()
killed_data['affected_label'] = 'Killed'
killed_data['affected_count'] = killed_data['killed_persons']

combined_data = pd.concat([injured_data, killed_data])

combined_data['vehicle_type_1'] = combined_data['vehicle_type_1'].astype('category')
combined_data['contributing_factor_vehicle_1'] = combined_data['contributing_factor_vehicle_1'].astype('category')
combined_data['affected_label'] = combined_data['affected_label'].astype('category')
combined_data = combined_data.reset_index(drop=True)

vehicle_dim = go.parcats.Dimension(
    values=combined_data['vehicle_type_1'],
    label="Vehicle Type",
    categoryorder='category ascending'
)

factor_dim = go.parcats.Dimension(
    values=combined_data['contributing_factor_vehicle_1'],
    label="Contributing Factor"
)

affected_dim = go.parcats.Dimension(
    values=combined_data['affected_label'],
    label="Affected",
    categoryorder='category ascending'
)

color = combined_data['affected_count']
colorscale = [[0, 'lightsteelblue'], [1, 'mediumseagreen']]

fig = go.Figure(data = [go.Parcats(
    dimensions=[vehicle_dim, factor_dim, affected_dim],
    line={'color': color, 'colorscale': colorscale},
    hoveron='color', hoverinfo='count+probability',
    labelfont={'size': 18, 'family': 'Times'},
    tickfont={'size': 16, 'family': 'Times'},
    arrangement='freeform'
)])

st.plotly_chart(fig)

st.markdown("The **parallel categories diagram** explores the relationship between vehicle types, "
            "contributing factors, and outcomes (injuries or deaths). By identifying the most common "
            "contributing factors and vehicle types involved in severe accidents, this visualization "
            "helps in understanding :blue-background[highlightunderlying causes and formulating targeted prevention strategies.]")

if st.checkbox("Show Raw Data", False):
    st.subheader("Raw Data")
    st.write(data)
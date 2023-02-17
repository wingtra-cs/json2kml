import streamlit as st
import json
import pydeck as pdk
import pandas as pd
import simplekml

st.set_page_config(layout="wide")

st.title('Flight Trigger Counter')

st.sidebar.image('./logo.png', width = 260)
st.sidebar.markdown('#')
st.sidebar.write('This application genertes an approximation of the flight trajectory based on the JSON file.')
st.sidebar.write('If you have any questions regarding the application, please contact us at support@wingtra.com.')
st.sidebar.markdown('#')
st.sidebar.info('This is a prototype application. Wingtra AG does not guarantee correct functionality. Use with discretion.')

# Upload button for JSON

uploaded_json = st.file_uploader('Please Select Project JSON file in the DATA folder.', accept_multiple_files=False)
uploaded = False

if uploaded_json is not None:
    if uploaded_json.name.lower().endswith('.json'):
        uploaded = True
    else:
        msg = 'Please upload a JSON file.'
        st.error(msg)
        st.stop()

if uploaded:
    
    # Parse and Visualize JSON
      
    data = json.load(uploaded_json)
    try:
        triggers = data['flights'][0]['geotag']
        trigger_count = len(triggers)
    except:
        msg = 'Please upload a valid Wingtra JSON file.'
        st.error(msg)
        st.stop()
    
    st.success('JSON File Uploaded.')
    
    st.subheader('There are ' + str(trigger_count) + ' triggers.')
      
    lat = []
    lon = []
    alt = []    
    for trigger in triggers:
        lat.append(float(trigger['coordinate'][0]))
        lon.append(float(trigger['coordinate'][1]))
        alt.append(float(trigger['coordinate'][2]))
    
    points_df = pd.DataFrame(zip(lat,lon,alt), columns=['lat','lon','alt'])
    st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/satellite-streets-v11',
        initial_view_state=pdk.ViewState(
            latitude=points_df['lat'].mean(),
            longitude=points_df['lon'].mean(),
            zoom=14,
            pitch=0,
         ),
         layers=[
             pdk.Layer(
                 'ScatterplotLayer',
                 data=points_df,
                 get_position='[lon, lat]',
                 get_color='[70, 130, 180, 200]',
                 get_radius=20,
             ),
             ],
         ))
    
    fname = uploaded_json.name.split('.')[0] + '_FlightTrajectory.kml'
    line_kml = simplekml.Kml()
    linestring = line_kml.newlinestring(name="Flight Trajectory")
    linestring.style.linestyle.width = 3
    linestring.coords = list(zip(points_df.lon, points_df.lat, points_df.alt))
    linestring.altitudemode = simplekml.AltitudeMode.absolute
    line_kml.save(fname)
    
    fp = open(fname, 'rb')
    st.download_button(
        label="Download Data",
        data=fp,
        file_name=fname,
        mime='application/kml',
        )
    st.stop()
      
else:
    st.stop()

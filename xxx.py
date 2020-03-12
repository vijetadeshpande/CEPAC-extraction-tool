# -*- coding: utf-8 -*-
"""
Created on Fri Jul 26 14:56:46 2019

@author: Vijeta
"""
import numpy as np
import missingno as msn
import seaborn as sns
import matplotlib.pyplot as plt
from plotly.offline import plot
import geopandas as gpd
import geoplot as gplt
#%% used libraries
from shapely.geometry import Point
from geopy import geocoders  
from geopy.geocoders import Nominatim
import pandas as pd
from geopandas import GeoDataFrame
import folium
#%%

gn = geocoders.GeoNames(country_bias = 'BR', username = 'vkd2')
geolocator = Nominatim()
df = pd.read_excel(r'C:\Users\Vijeta\Documents\Projects\Brazil PrEP\Lit and references\Epidemic properties by each city.xlsx')
df[['City', 'Region']] = df.loc[:, 'City/region'].str.split('/', expand = True)
col = df.columns.tolist()
new_cols = ['City', 'Region', col[1], col[2], col[3], col[4], col[5]]
df = df[new_cols]

for i in range(2, 5):
    df[new_cols[i]] = df.loc[:, new_cols[i]].str.split(' ', expand = True)[0].str.replace(r',', '').astype(float)
   # df[new_cols[i]] = df[new_cols[i]]
   
for i in ['Lat', 'Long', 'Add']:
    df.insert(loc = len(df.columns), column = i, value = 0)

df = df.set_index(df.loc[:, 'City'])    
for city in df.loc[:, 'City']:
    if city != "NULL":
        try:
            location = geolocator.geocode(city + r' ' + 'Brazil')
            df.loc[city, 'Add'] = location.address
            df.loc[city, 'Lat'] = location.latitude
            df.loc[city, 'Long'] = location.longitude
        except:
            df.loc[city, 'Add'] = 'Not found'
            df.loc[city, 'Lat'] = 'N/A'
            df.loc[city, 'Long'] = 'N/A'
    
    #print(city)


#%% Geopandas
geometry = [Point(xy).buffer(1.0) for xy in zip(df.loc[:, 'Long'], df.loc[:, 'Lat'])]
plot_df = df.drop(['Long', 'Lat'], axis=1)
crs = {'init': 'epsg:4326'}
gdf = GeoDataFrame(plot_df, crs=crs, geometry=geometry)
world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres')) 
base = world[world.continent == 'South America'].plot(color='white', edgecolor='black')
gdf.plot(ax = base, color = 'gray')


#%% Folium

import branca

def color_producer(continuos_input):
    if continuos_input < 24:
        return 'black'
    elif continuos_input < 32:
        return "darkred"
    elif continuos_input < 40:
        return "pink"
    else:
        return "white"

m = folium.Map(location = [-14.2350, -51.9253], tiles="OpenStreetMap", zoom_start=5)

'''
m.choropleth(
        geo_data = gdf,
        name = 'geometry',
        data = gdf.loc[:, 'MSM Population'],
        columns = ['geometry', 'MSM Population'],
        #key_on = 'feature.properties.MSM',
        fill_color = 'Greens',
        fill_opacity = 0.5,
        line_opacity = 0.2,
        legend_name = 'MSM Population')
'''

for i in gdf.loc[:, 'City']:
   folium.Circle(
      location=[df.loc[i, 'Lat'], df.loc[i,'Long']],
      popup=('City: ' + str(df.loc[i, 'City']) + ',' + '<br>'
             'HIV Prevalence in MSM: ' + str(df.loc[i, 'HIV Prevalence among MSM']) + '%' +'<br>'
             ),
      color = 'gray',
      radius=(gdf.loc[i, 'HIV Prevalence among MSM']*7000),
      fill=True,
      fill_color=color_producer(df.loc[i, 'Percent on treatment']),
      fill_opacity = 0.8,
      opacity = 0.35
   ).add_to(m)

colormap = branca.colormap.StepColormap(colors = ['black', 'darkred', 'pink', 'white'],
                                        index = [24, 28, 32, 40],
                                        vmin = 0,
                                        vmax = 100)
colormap.caption = 'Percent on treatment'
colormap.add_to(m)

#folium.TileLayer('Mapbox Bright').add_to(m)
folium.LayerControl().add_to(m)
folium.TileLayer('Mapbox Bright').add_to(m)
folium.TileLayer('stamentoner').add_to(m)
m.save('xyz.html')



#%% plotly

import plotly as py
import plotly.graph_objs as go
import plotly.figure_factory as ff

data_b = dict (
    type = 'choropleth',
    locations = df.loc[:, 'City'],
    locationmode = 'ISO-3',
    z = df.loc[:, 'HIV Prevalence among MSM'])

# color theme for plot
colorscale=["#f7fbff","#ebf3fb","#deebf7","#d2e3f3","#c6dbef","#b3d2e9","#9ecae1",             "#85bcdb","#6baed6","#57a0ce","#4292c6","#3082be","#2171b5","#1361a9","#08519c","#0b4083","#08306b"]
endpts = list(np.linspace(1, 12, len(colorscale) - 1))

#
map_b = go.Figure(data = data_b, layout = dict(geo = dict(scope = 'south america')))
py.offline.plot(map_b)









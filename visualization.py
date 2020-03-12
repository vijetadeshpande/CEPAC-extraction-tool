# -*- coding: utf-8 -*-
"""
Created on Thu Jul 25 14:06:42 2019

@author: Vijeta
"""
import branca
from shapely.geometry import Point
from geopy import geocoders  
from geopy.geocoders import Nominatim
import pandas as pd
from geopandas import GeoDataFrame
import folium
import geopandas as gpd
import os
from ggplot import ggplot, geom_line, geom_point, aes, facet_wrap, ggtitle, stat_smooth
import numpy as np
from copy import deepcopy
import os


def tornado_plot(data):
    
    # adjust data
    
    
    
    return

def bubble_plor_for_epidemic(epidemic_data, save_path):
    
    #%% generating latitude and longitude of each city by city name
    gn = geocoders.GeoNames(country_bias = 'BR', username = 'vkd2')
    geolocator = Nominatim()
    df = epidemic_data
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
    
    #%% read the lat/long data as Geopandas Geodataframe
    geometry = [Point(xy).buffer(1.0) for xy in zip(df.loc[:, 'Long'], df.loc[:, 'Lat'])]
    plot_df = df.drop(['Long', 'Lat'], axis=1)
    crs = {'init': 'epsg:4326'}
    gdf = GeoDataFrame(plot_df, crs=crs, geometry=geometry)
    
    # simple city locator plot
    #world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    #base = world[world.continent == 'South America'].plot(color='white', edgecolor='black')
    #gdf.plot(ax = base, color = 'gray')
    
    #%% Plotting with folium
    
    # supportive function (makes the continuous var a categorical and fills the 
    # the bubbles with respective color for that category)
    def color_producer(continuos_input):
        if continuos_input < 24:
            return 'black'
        elif continuos_input < 32:
            return "darkred"
        elif continuos_input < 40:
            return "pink"
        else:
            return "white"
    
    # initialize the position of the map
    m = folium.Map(location = [-14.2350, -51.9253], tiles="OpenStreetMap", zoom_start=5)
    
    #%%
    
    '''
    # Following section is for plotting a heat map as a base map
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
    
    # bubble plot
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
          fill_opacity = 0.6,
          opacity = 0.5
       ).add_to(m)
    
    # legend
    colormap = branca.colormap.StepColormap(colors = ['black', 'darkred', 'pink', 'white'],
                                            index = [24, 28, 32, 40],
                                            vmin = 0,
                                            vmax = 100)
    colormap.caption = 'Percent on treatment'
    colormap.add_to(m)
    
    m.save(save_path)
    
    return
    
def plot_transmission_results(tx_results, percentage_decline, save_path, path_names):
    
    #%% what are inputs?
    
    # transmission results
    # There'll be a folder called 'Runs prepared for ...'
    # all the folders inside that folder will have a CEPAC results folder.
    # tx_data is a dictionary and will have two keys, 'monthly' and 'popstats'
    # 'monthly' key will only have primary transmissions data
    tx_data = deepcopy(tx_results)
    t = 120
    total_var = 3
    total_val = 4
    # percentage decline
    # this is also dictionary of percentage decline values for each folder
    # having cepac results
    
    # save_path eaxact folder where you want to save your images
    
    # path_names will have paths to transmissions and sensitivity directories
    
    #%% plot percentage decline
    
    # geberate an environment object first
    # lets go for line plot
    data_plot = pd.DataFrame(columns = ['x', 'Percentage decline', 'Transmissions', 'Variable'], index = range(0, total_var*total_val))
    data_in = pd.read_excel(os.path.join(path_names['transmission'], 'Input files', 'transmission_rate_multiplier_required_inputs.xlsx'))
    col = ['Incidence rate per 100 PY specific to high-risk group 1', 
           'HIV uninfected individuals in high-risk group 1', 
           'HIV infected individuals in high-risk group 1']
    col_adj = ['Incidence', 'Uninfected', 'Infected']
    data_in[col[0]] = data_in[col[0]].round(1)
    base_val = [np.float64(0.9), 2960000, 136400]
    y1_values = {col[0]: [], col[1]: [], col[2]: []}
    for var in percentage_decline:
        if 'HIV+' in var:
            y1_values[col[2]].append(percentage_decline[var])
        elif 'HIV-' in var:
            y1_values[col[1]].append(percentage_decline[var])
        elif 'Incidence' in var:
            y1_values[col[0]].append(percentage_decline[var])
    
    for i in range(len(col)):
        idx = data_in.loc[data_in.loc[:, col[i]] != base_val[i], col[i]].index.values[0]
        data_plot.loc[idx-1:idx+3-1, 'x'] = data_in.loc[idx:idx+3, col[i]].values
        data_plot.loc[idx-1:idx+3-1, 'Variable'] = col_adj[i]
        data_plot.loc[idx-1:idx+3-1, 'Percentage decline'] = y1_values[col[i]]
    
    # plot
    df_float = data_plot.loc[data_plot.loc[:, 'Percentage decline'] <= 200, :]
    (ggplot(aes(x = 'x', y = 'Percentage decline'), df_float) + geom_line() + facet_wrap('Variable', scales = 'free')).save(os.path.join(save_path, 'Percentage decline'))
    del df_float
    #%% visualizing transmissions
    # index = range(time * number of values for each variable * number of variables)
    def set_abc(run, var_idx, var_name, var_value_idx):
        
        # set variable names
        data_plot_tx.loc[(var_idx-1)*t:((var_idx-1)*t) + t-1, 'Variable'] = var_name
        
        # set variable value
        data_plot_tx.loc[(var_idx-1)*t:((var_idx-1)*t) + t-1, 'Value'] = data_plot.loc[data_plot.loc[:, 'Variable'] == var_name, 'x'].values[var_value_idx]
        
        if 'RunA' in run:
            data_plot_tx.loc[(var_idx-1)*t:((var_idx-1)*t) + t-1, 'RunA tx'] = tx_data[var]['monthly'][run]['transmissions'].iloc[0:t].values
        elif 'RunB' in run:
            data_plot_tx.loc[(var_idx-1)*t:((var_idx-1)*t) + t-1, 'RunB tx'] = tx_data[var]['monthly'][run]['transmissions'].iloc[0:t].values
        elif 'RunC' in run:
            data_plot_tx.loc[(var_idx-1)*t:((var_idx-1)*t) + t-1, 'RunC tx'] = tx_data[var]['monthly'][run]['transmissions'].iloc[0:t].values
    
    
    data_plot_tx = pd.DataFrame(index = range(t*total_var*total_val), columns = ['Variable', 'Value', 'RunA tx', 'RunB tx', 'RunC tx'])
    var_idx = -1
    var_val_idx = [-1, -1, -1]
    for var in tx_data:
        var_idx += 1
        if 'HIV+' in var:
            var_val_idx[2] += 1
            var_name = col_adj[2]
            for run in tx_data[var]['monthly']:
                set_abc(run, var_idx, var_name, var_val_idx[2])
        elif 'HIV-' in var:
            var_val_idx[1] += 1
            var_name = col_adj[1]
            for run in tx_data[var]['monthly']:
                set_abc(run, var_idx, var_name, var_val_idx[1])
        elif 'Incidence' in var:
            var_val_idx[0] += 1
            var_name = col_adj[0]
            for run in tx_data[var]['monthly']:
                set_abc(run, var_idx, var_name, var_val_idx[0])
        else:
            continue
    
    data_plot_tx['t'] = 0
    t_float = -1
    for row in data_plot_tx.index:
        if t_float == t-1:
            t_float = -1
        t_float += 1
        data_plot_tx.loc[row, 't'] = t_float
    
    #%% plots for individual runs
    run_col = ['RunA tx', 'RunB tx', 'RunC tx']
    inci = data_plot_tx.loc[ data_plot_tx.loc[:, 'Variable'] == 'Incidence', :]
    inf = data_plot_tx.loc[ data_plot_tx.loc[:, 'Variable'] == 'Infected', :]
    uninf = data_plot_tx.loc[ data_plot_tx.loc[:, 'Variable'] == 'Uninfected', :]
    for i in run_col:
        (ggplot(aes(x = 't', y = i, color = 'Value'), data_plot_tx) + geom_line() + facet_wrap('Variable', scales = 'free')).save(os.path.join(save_path, str(i + r'_transmissions for all variable all values')))
        (ggplot(aes(x = 't', y = i), inci) + geom_line() + facet_wrap('Variable', 'Value', scales = 'free')).save(os.path.join(save_path, str(i + r'_plots for individual values of incidence')))
        (ggplot(aes(x = 't', y = i), inf) + geom_line() + facet_wrap('Variable', 'Value', scales = 'free')).save(os.path.join(save_path, str(i + r'_plots for individual values of infected population')))
        (ggplot(aes(x = 't', y = i), uninf) + geom_line() + facet_wrap('Variable', 'Value', scales = 'free')).save(os.path.join(save_path, str(i + '_plots for individual values of uninfected population')))
    
    #%% compare runs ABC
    data_plot_abc = {}
    for var in col_adj:
        float_df = pd.DataFrame(index = range(0, t*total_var*total_val), columns = ['t', 'Value', 'Transmissions', 'Run'])
        insert_idx = -1
        for val in data_plot.loc[data_plot.loc[:, 'Variable'] == var, 'x']:
            var_df = data_plot_tx.loc[data_plot_tx.loc[:, 'Variable'] == var, :]
            var_df = var_df.reset_index(drop = True)
            var_val_df = var_df.loc[var_df.loc[:, 'Value'] == val, :]
            var_val_df = var_val_df.reset_index(drop = True)
            for c in ['RunA tx', 'RunB tx', 'RunC tx']:
                insert_idx += 1
                float_df.loc[insert_idx*t:(insert_idx*t) + t-1, 'Run'] = c
                float_df.loc[insert_idx*t:(insert_idx*t) + t-1, 'Transmissions'] = var_val_df.loc[:, c].values
                float_df.loc[insert_idx*t:(insert_idx*t) + t-1, 'Run'] = c
                float_df.loc[insert_idx*t:(insert_idx*t) + t-1, 'Value'] = val
                float_df.loc[insert_idx*t:(insert_idx*t) + t-1, 't'] = np.arange(t)
        data_plot_abc[var] = float_df.dropna()
        (ggplot(aes(x = 't', y = 'Transmissions', color = 'Run'), float_df) + geom_line() + facet_wrap('Value', scales = 'free') + ggtitle(var)).save(os.path.join(save_path, str(var + '_comparison of transmissions in runs ABC')))
    
    #%% compare runs BC
    for var in data_plot_abc:
        float_df = data_plot_abc[var].loc[data_plot_abc[var].loc[:, 'Run'] != 'RunA tx', :]
        (ggplot(aes(x = 't', y = 'Transmissions', color = 'Run'), float_df) + geom_line(alpha = 0.2) + facet_wrap('Value', scales = 'free') + stat_smooth(method= 'loess', se = False) + ggtitle(var)).save(os.path.join(save_path, str(var + '_comparison of transmissions in runs BC')))

    
    return

def plot_after_transmission_results(data, path_names):
    
    # import input data for tranmission analysis
    var_and_val = pd.DataFrame(columns = ['x', 'Variable'], index = range(0, 12))
    plot_lm = pd.DataFrame(columns = ['x', 'Life Months', 'Scenario', 'Variable'], index = range(0, 24))
    data_in = pd.read_excel(os.path.join(path_names['transmission'], 'Input files', 'transmission_rate_multiplier_required_inputs.xlsx'))
    col = ['Yearly incidence in MSM', 'Number of HIV uninfected individuals (HRG size)', 'Number of HIV infected individuals in primary cohort at t=0']
    col_adj = ['Incidence', 'Uninfected', 'Infected']
    base_val = [0.009, 2960000, 136400]
    
    for i in range(len(col)):
        idx = data_in.loc[data_in.loc[:, col[i]] != base_val[i], col[i]].index.values[0]
        var_and_val.loc[idx-1:idx+3-1, 'x'] = data_in.loc[idx:idx+3, col[i]].values
        var_and_val.loc[idx-1:idx+3-1, 'Variable'] = col_adj[i]
    
    row_idx = -2
    var_idx = [-1, -1, -1]
    for var in data:
        
        if 'HIV+' in var:
            var_idx[2] += 1
            plot_lm.loc[row_idx:row_idx+1, 'x'] = var_and_val.loc[var_and_val['Variable'] == col_adj[2], 'x'].values[var_idx[2]]
            plot_lm.loc[row_idx:row_idx+1, 'Variable'] = var_and_val.loc[var_and_val['Variable'] == col_adj[2], 'Variable'].values[var_idx[2]]
            plot_lm.loc[row_idx:row_idx+1, 'Life Months'] = data[var]['popstats'].loc[:, 'LMs_'].values
            plot_lm.loc[row_idx:row_idx+1, 'Scenario'] = data[var]['popstats'].loc[:, 'RUN_NAME_'].values
        elif 'HIV-' in var:
            var_idx[1] += 1
            plot_lm.loc[row_idx:row_idx+1, 'x'] = var_and_val.loc[var_and_val['Variable'] == col_adj[1], 'x'].values[var_idx[1]]
            plot_lm.loc[row_idx:row_idx+1, 'Variable'] = var_and_val.loc[var_and_val['Variable'] == col_adj[1], 'Variable'].values[var_idx[1]]
            plot_lm.loc[row_idx:row_idx+1, 'Life Months'] = data[var]['popstats'].loc[:, 'LMs_'].values
            plot_lm.loc[row_idx:row_idx+1, 'Scenario'] = data[var]['popstats'].loc[:, 'RUN_NAME_'].values
        elif 'Incidence' in var:
            var_idx[0] += 1
            plot_lm.loc[row_idx:row_idx+1, 'x'] = var_and_val.loc[var_and_val['Variable'] == col_adj[0], 'x'].values[var_idx[0]]
            plot_lm.loc[row_idx:row_idx+1, 'Variable'] = var_and_val.loc[var_and_val['Variable'] == col_adj[0], 'Variable'].values[var_idx[0]]
            plot_lm.loc[row_idx:row_idx+1, 'Life Months'] = data[var]['popstats'].loc[:, 'LMs_'].values
            plot_lm.loc[row_idx:row_idx+1, 'Scenario'] = data[var]['popstats'].loc[:, 'RUN_NAME_'].values
            
        row_idx += 2
    
    # plot
    save_path = os.path.join(path_names['transmission'], r'Input files', r'Plots for final runs')
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    
    (ggplot(aes(x = 'x', y = 'Life Months', color = 'Scenario'), plot_lm) + geom_line() + facet_wrap('Variable', scales = 'free')).save(os.path.join(save_path, 'Comparison of '))
    
    return

def plot_longitudinal_history(data, var = []):
    
    # check if input is dataframe
    if not (isinstance(data, pd.DataFrame) | isinstance(data, pd.Series)):
        print('\nget_subset_of_out_file function in link_to_cepac_in_and_out_files.py file requires the input to be in pd.DataFrame format. Current input is not.')
        return False
    
    

#data_in.loc[:, col[0]]
#data_in[col[0]] = data_in[col[0]].round(1)
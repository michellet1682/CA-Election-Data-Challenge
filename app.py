#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import dash as d
from dash import html
import pandas as pd
from dash import dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

import addfips
import plotly.express as px
from urllib.request import urlopen
import json
import math


# In[ ]:


app = d.Dash(__name__, external_stylesheets=[dbc.themes.QUARTZ])
server = app.server
app.title = 'California 2022 Election Prop 30' 


# In[ ]:


excel_data = pd.read_excel('Hydrogen_Refueling_Stations_Last updated_10-18-2022.xlsx')


# In[ ]:


df = pd.DataFrame(excel_data)


# In[ ]:


county= df['County'].unique()
#df.groupby('County').unique()
county=np.delete(county, -1)


# In[ ]:


county_hydrogen_fuel= pd.DataFrame()

for i in range(len(county)):

    placeholder = pd.DataFrame() #placeholder dataframe
    placeholder['county'] = [county[i]] #state name into state column

    county_rows = df[df['County'] == str(county[i])] #group rows from the same state
    county_sum = county_rows['Fueling Positions'].sum() #sum of each age bin within the same state
    fuel = county_sum.sum() #add the sum of age bins together to get state population

    placeholder['total hydrogen stations'] = [fuel] #state population into state pop column

    county_hydrogen_fuel = pd.concat([county_hydrogen_fuel, placeholder], ignore_index = True) 
    #append placeholder to the state_prop data frame


# In[ ]:


def hydrogen_refuel():
    fig1 = go.Figure(data=[go.Bar(x=county_hydrogen_fuel['county'], 
                                 y = county_hydrogen_fuel['total hydrogen stations'])],
                    layout=go.Layout(title=go.layout.Title(text="Hydrogen Refueling Stations by county")))
    return fig1


# In[ ]:


ev_sales_df = pd.read_excel('New_ZEV_Sales_Last_updated_10-18-2022.xlsx')
out_of_state = ev_sales_df[(ev_sales_df['County'] == 'Out Of State') ].index
ev_sales_df.drop(out_of_state , inplace=True)
#ev_sales_df.head(n=6)


# In[ ]:


year_df = ev_sales_df.groupby(['Data Year','County']).sum(numeric_only = True)
year_df.reset_index(inplace=True)
year_df.rename(columns = {'Data Year':'Year','Number of Vehicles':'Total Purchased EV'},inplace=True)
#year_df.head()


# In[ ]:


fig2 = px.bar(year_df,
             x=year_df['Year'], 
             y='Total Purchased EV', 
             #text_auto=True,
             #log_x = True,
             color = 'County')
fig2.update_xaxes(
        tickangle = 90,
        title_text = "Year",
        title_font = {"size": 20},
        title_standoff = 25,
        tickmode = 'linear')
fig2.update_yaxes(
        tickangle = 90,
        title_text = "Total Purchased EV",
        title_font = {"size": 20},
        title_standoff = 25)
fig2.update_layout(title_text='Total Electric Vehicles Purchased by Year', title_x=0.5)
fig2['layout']['title']['font'] = dict(size=25)
fig2.update_layout()
fig2.show()


# In[ ]:


app.layout = html.Div(children=[
    # All elements from the top of the page
    html.Div([
        html.H1(children='Hello Dash'),

        html.Div(children='''
            Dash: A web application framework for Python.
        '''),

        dcc.Graph(
            id='graph1',
            figure=hydrogen_refuel()
        ),  
    ]),
    # New Div for all elements in the new 'row' of the page
    html.Div([
        html.H1(children='Hello Dash'),

        html.Div(children='''
            Dash: A web application framework for Python.
        '''),

        dcc.Graph(
            id='graph2',
            figure=fig2
        ),  
    ]),
])


# In[ ]:


fig3 = px.pie(year_df, 
              values='Total Purchased EV',
              names='County')
fig3.update_layout(title_text='Percentage of Electric Vehicles Purchased by County', title_x=0.12)
fig3.update_traces(textposition='inside')
fig3.update_layout(uniformtext_minsize=12, uniformtext_mode='hide')
fig3['layout']['title']['font'] = dict(size=25)
fig3.show()


# In[ ]:


ev_chargers = pd.read_csv("EV Chargers_Last updated 01-31-2022.csv")
ev_chargers2 = ev_chargers.drop('Total', axis=1)
ev_chargers2["Public Chargers"] = (ev_chargers2["Public Level 1"] + ev_chargers2["Public Level 2"] + 
                                   ev_chargers2["Public DC Fast"])
ev_chargers2["Private Chargers"] = (ev_chargers2["Shared Private Level 1"] + ev_chargers2["Shared Private Level 2"] + 
                                   ev_chargers2["Shared Private DC Fast"])
ev_chargers2 = ev_chargers2.drop([59])


# In[ ]:


charger_list = list(ev_chargers2) 
charger_list.remove('County')
charger_list.remove('Public Chargers')
charger_list.remove('Private Chargers')

ev_df = pd.DataFrame()
for i in range(len(charger_list)):
    placeholder = pd.melt(ev_chargers2, id_vars = ['County'], value_vars = [charger_list[i]])
    ev_df = pd.concat([ev_df, placeholder], ignore_index = True)


# In[ ]:


ev_pub = ev_chargers2[["County","Public Level 1", "Public Level 2", "Public DC Fast", "Public Chargers"]]
ev_priv = ev_chargers2[["County","Shared Private Level 1", "Shared Private Level 2", "Shared Private DC Fast", 
                       "Private Chargers"]]


# In[ ]:


all_fig = px.bar(ev_df, x="County",y=["value"], color="variable", 
       labels={'_value': 'Count'}, title='All EV Chargers per County')
all_fig.update_layout(legend = dict(title = 'Type of Charger'))


# In[ ]:


# pub_fig = px.bar(ev_pub, x="County",y=["Public Level 1", "Public Level 2", "Public DC Fast"], 
#        labels={'value': 'Count'}, title='Public EV Chargers per County')
# pub_fig.update_layout(legend = dict(title = 'Type of Public Charger'))


# In[ ]:


# priv_fig = px.bar(ev_priv, x="County",y=["Shared Private Level 1", "Shared Private Level 2", "Shared Private DC Fast"],
#       labels={'value': 'Count'}, title='Private EV Chargers per County')
# priv_fig.update_layout(legend = dict(title = 'Type of Private Charger'))


# In[ ]:


charger_amount_df = pd.read_csv('EV Chargers_Last updated 01-31-2022.csv')
charger_amount_df = charger_amount_df.dropna()


# In[ ]:


af = addfips.AddFIPS()

def create_fips_col(county):
    fips = af.get_county_fips(county, state = 'California')
    return fips

# add 'fips' column to each df
charger_amount_df['fips'] = charger_amount_df['County'].apply(create_fips_col)


# In[ ]:


charger_amount_df['log_Total'] = charger_amount_df['Total'].apply(math.log)


# In[ ]:


with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)

target_states = ['06']
counties['features'] = [f for f in counties['features'] if f['properties']['STATE'] in target_states] 


# In[ ]:


charger_fig = px.choropleth(
    charger_amount_df,
    geojson = counties,
    locations = 'fips',
    color = 'log_Total',
    scope = 'usa',
    color_continuous_scale= 'agsunset_r',
    hover_name = charger_amount_df['County'],
    hover_data= {'Total': True,
                 'fips': False,
                 'log_Total': False
                 },
    basemap_visible=True
           
)

charger_fig.update_geos(fitbounds = 'locations')
charger_fig.update_layout(height=500,margin={"r":0,"t":0,"l":0,"b":0})
charger_fig.layout.coloraxis.colorbar = {'title': 'Number of EV Chargers',
                                 'x': 0.9,
                                 'tickvals': [0,1,2,3,4,5,6,7,8,9,10, 11],
                                 'ticktext': [0, 2, 5] + [str(int(round(math.exp(val), -1))) for val in range(2,11)]}
#charger_fig.show()


# In[ ]:


ev_df = pd.read_csv('New_ZEV_Sales.csv')


# In[ ]:


out_of_state = ev_df[ (ev_df['County'] == 'Out Of State') ].index
ev_df.drop(out_of_state , inplace=True)


# In[ ]:


ev_year_df = ev_df.groupby(['Data Year','County']).sum(numeric_only = True)
ev_year_df.reset_index(inplace=True)
ev_year_df.rename(columns = {'Number of Vehicles': 'Total', 'Data Year': 'Year'}, inplace = True)


# In[ ]:


ev_year_df['fips'] = ev_year_df['County'].apply(create_fips_col)


# In[ ]:


first_year = ev_year_df['Year'].iloc[0]
last_year = ev_year_df['Year'].iloc[-1]


# In[ ]:


counties_lst = ev_year_df['County'].unique()


# In[ ]:


for year in range(first_year, last_year + 1):
    for county in counties_lst:
        if not ((ev_year_df['Year'] == year) & (ev_year_df['County'] ==  county)).any():
            temp_df = {'Year': [year], 
                       'County': [county], 
                       'Total': [0], 
                       'fips': [af.get_county_fips(county, state = 'California')]}
            temp_df = pd.DataFrame(temp_df)
            ev_year_df = pd.concat([ev_year_df, temp_df], ignore_index = True)

ev_year_df = ev_year_df.sort_values(by = 'Year')


# In[ ]:


def cumulative_sum(row):
    cur_year = row['Year']
    county = row['County']
    cum_sum = ev_year_df[(ev_year_df['Year'] <= cur_year) & (ev_year_df['County'] == county)]['Total'].sum(numeric_only=True)
    return cum_sum


# In[ ]:


ev_year_df['Cumulative Total'] = ev_year_df.apply(cumulative_sum, axis=1)


# In[ ]:


def log_0(num):
    if num == 0:
        return 0
    else:
        return math.log(num)


# In[ ]:


ev_year_df['log_Cum_Total'] = ev_year_df['Cumulative Total'].apply(log_0)


# In[ ]:


ev_year_df


# In[ ]:


ev_year_fig = px.choropleth(
    ev_year_df,
    geojson = counties,
    locations = 'fips',
    color = 'log_Cum_Total',
    scope = 'usa',
    color_continuous_scale= 'agsunset_r',
    hover_name = ev_year_df['County'],
    hover_data= {'Cumulative Total': True,
                 'fips': False,
                 'log_Cum_Total': False
                 },
    basemap_visible=True,
    animation_frame='Year'
           
)

ev_year_fig.update_geos(fitbounds = 'locations')
ev_year_fig.update_layout(height=500,margin={"r":0,"t":5,"l":0,"b":0})
ev_year_fig.layout.coloraxis.colorbar = {'title': 'Number of EVs',
                                 'x': 0.9,
                                 'tickvals': [0, 0.6, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14],
                                 'ticktext': [0, 2, 3] + [str(int(round(math.exp(val), -1))) for val in range(2,14)]
                                 }
#ev_year_fig.show()


# In[ ]:


app.layout = html.Div(children=[
    # All elements from the top of the page
    html.Div([
        html.H1(children='Hydrogen Refueling'),

        html.Div(children='''
            Other counties not listed are 0.
        '''),

        dcc.Graph(
            id='graph1',
            figure=hydrogen_refuel()
        ),
        
        html.P(
            'Southern California and the Bay area are the leaders by far when it comes to avaialbility of hydrogen refueling stations. Approximately 50% of all the hydrogen stations in CA are private and not accessible to the public which are used specifically used only for the private sector. These private stations are typically used by industrial purposes in refining and chemical processes. With a Prop30 approval, hydrogen vehicles would likely increase in number requiring more public infrastructure for refueling. This would also allow the industrial sector to tap into these stations as well making working conditions more convenient. Hydrogen fuel cells are major proponents for the ZEV sector since their only waste is water and air.'
        ),
    ]),
    # New Div for all elements in the new 'row' of the page
    html.Div([
        html.H1(children='EV Purchased by Year'),

        html.Div(children='''
            Interactive Bar Graph for EVs Purchased
        '''),

        dcc.Graph(
            id='graph2',
            figure=fig2
        ),
        
        html.P(
            'Although the earliest modern EV was sold in the late 1990s, EVs purchases started to rise in 2011. Areas with higher population density and higher median income like Los Angeles buys more EVs than other counties. The sharp increase in EV purchases in 2021 and 2022 signals the growing popularity of EVs over gas cars.'
        ),
    ]),
    
        html.Div([
        html.H1(children='Percentage of EVs Purchased'),

        html.Div(children='''
            Total Breakdown of EVs Purchased by County
        '''),

        dcc.Graph(
            id='graph3',
            figure=fig3
        ),  
    ]),
    
        html.Div([
        html.H1(children='All EV Chargers'),

        html.Div(children='''
            Chargers in California
        '''),

        dcc.Graph(
            id='graph4',
            figure=all_fig
        ),
            
        html.P(
            'Southern California and the Bay Area are EV Charger leaders by far serving the majority of EV owners in the state. A potential benefit of passing Prop30 would be the acquisition of more publicly owned EV chargers. Currently the state leading counties have over ninety-percent of the EV chargers as private entitites which are subject to the private sectors ruling. If Prop30 is withheld however,  it may allow the private sector to benefit more and generate more taxable income that would benefit the state. Private networks may cost more but,  in return they need less maintenance since there is less wear and tire on the infrastructure and allows for faster charging since it is limited to  those individuals who have access to that particular private network. Public networks may allow for more potential users but, it slows the charging speeds down substantially since the chargers would be pulling more power.'
        ),
    ]),
    
        html.Div([
        html.H1(children='Chargers Heat Map'),

        html.Div(children='''
            Map of Chargers in California
        '''),

        dcc.Graph(
            id='graph5',
            figure=charger_fig
        ),
            
        html.P(
            'Locations such as Los Angeles and San Bernardino has much more chargers than other counties. This aligns with the visuals above since the two places has much more EVs than other counties. It appears that a county might have more chargers if more residents there own an EV.'
        )
    ]),   
    
        html.Div([
        html.H1(children='EVs Heat Map'),

        html.Div(children='''
            Click the play button at the bottom to see EVs over time
        '''),

        dcc.Graph(
            id='graph6',
            figure=ev_year_fig
        ),
            
        html.P(
            'Starting in 2010, there is a massive increase in EVs purchased. Overtime, all counties increased their EV purchases, especially counties with bigger populations.'
        )
    ]),    
])


# In[ ]:


if __name__ == '__main__': 
    app.run_server()


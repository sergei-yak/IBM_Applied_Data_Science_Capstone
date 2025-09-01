# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    html.Br(),
    dcc.Dropdown(id='site-dropdown',
                 options=[
                     {'label': 'All Sites', 'value': 'ALL'},
                     {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                     {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                     {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                     {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                 ],
                 value='ALL',
                 placeholder="Select a Launch Site",
                 searchable=True
                 ),
    html.Br(),
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),
    html.P("Payload range (Kg):"),
    dcc.RangeSlider(id='payload-slider',
                    min=0,
                    max=10000,
                    step=1000,
                    marks={0: '0', 1000:'1000',2000:'2000',3000:'3000',
                           4000:'4000',5000:'5000',6000:'6000',7000:'7000',
                           8000:'8000',9000:'9000',10000:'10000'},
                    value=[min_payload, max_payload]),
    html.Br(),
    html.Div(dcc.Graph(id='success-payload-scatter-chart'))
])

# Callback for pie chart
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        success_counts = spacex_df[spacex_df['class']==1].groupby('Launch Site')['class'].count().reset_index()
        fig = px.pie(success_counts, values='class', names='Launch Site',
                     title='Total Successful Launches by Site')
        return fig
    else:
        filtered_df = spacex_df[spacex_df['Launch Site']==entered_site]
        outcome_counts = filtered_df['class'].value_counts().reset_index()
        outcome_counts.columns = ['class', 'count']
        fig = px.pie(outcome_counts, values='count', names='class',
                     title=f'Total Success/Failure for {entered_site}',
                     color='class', color_discrete_map={1:'green',0:'red'})
        return fig

# Callback for scatter chart
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown','value'),
     Input('payload-slider','value')]
)
def get_scatter_plot(entered_site, payload_range):
    low, high = payload_range
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)']>=low) & 
                             (spacex_df['Payload Mass (kg)']<=high)]
    if entered_site=='ALL':
        fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class',
                         color='Booster Version Category',
                         title='Payload vs Outcome for All Sites',
                         hover_data=['Launch Site'])
        return fig
    else:
        site_df = filtered_df[filtered_df['Launch Site']==entered_site]
        fig = px.scatter(site_df, x='Payload Mass (kg)', y='class',
                         color='Booster Version Category',
                         title=f'Payload vs Outcome for {entered_site}',
                         hover_data=['Launch Site'])
        return fig

if __name__ == '__main__':
    app.run()


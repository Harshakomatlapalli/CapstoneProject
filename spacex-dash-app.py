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

app = dash.Dash(__name__)

# Define the app layout
app.layout = html.Div([
    html.H1('SpaceX Launch Records Dashboard', style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # TASK 1: Add Launch Site Dropdown Input Component
    html.Div([
        html.Label('Select Launch Site:'),
        dcc.Dropdown(
            id='site-dropdown',
            options=[
                {'label': 'All Sites', 'value': 'ALL'},
                {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'}
            ],
            value='ALL',
            placeholder='Select a Launch Site',
            searchable=True
        ),
    ], style={'width': '50%', 'margin': 'auto', 'padding': '10px'}),
    
    # Pie Chart for Launch Outcomes
    html.Div([
        dcc.Graph(id='success-pie-chart')
    ], style={'width': '50%', 'margin': 'auto'}),
    
    # Range Slider for Payload (placed above scatter plot as per screenshot)
    html.Div([
        html.Label('Payload Mass (kg):'),
        dcc.RangeSlider(
            id='payload-slider',
            min=0,
            max=10000,
            step=1000,
            marks={i: f'{i}' for i in range(0, 11000, 1000)},
            value=[0, 10000]
        ),
    ], style={'width': '50%', 'margin': 'auto', 'padding': '10px'}),
    
    # Scatter Plot for Payload vs. Launch Outcome
    html.Div([
        dcc.Graph(id='success-payload-scatter-chart')
    ], style={'width': '50%', 'margin': 'auto'})
])

# TASK 2: Callback for Pie Chart
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # For all sites, group by Launch Site and calculate success/failure counts
        pie_data = spacex_df.groupby('Launch Site')['class'].value_counts().unstack(fill_value=0)
        pie_data = pie_data.reset_index()
        pie_data.columns = ['Launch Site', 'Failure', 'Success']
        fig = px.pie(
            pie_data,
            values='Success',
            names='Launch Site',
            title='Total Successful Launches by Site',
            color_discrete_sequence=px.colors.qualitative.Plotly
        )
        fig.update_traces(
            textinfo='percent+label',
            hoverinfo='label+percent+value'
        )
    else:
        # For a specific site, filter data and show success/failure distribution
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        outcome_counts = filtered_df['class'].value_counts().rename(index={1: 'Success', 0: 'Failure'})
        fig = px.pie(
            names=outcome_counts.index,
            values=outcome_counts.values,
            title=f'Launch Outcomes for {entered_site}',
            color_discrete_sequence=px.colors.qualitative.Plotly
        )
        fig.update_traces(
            textinfo='percent+label',
            hoverinfo='label+percent+value'
        )
    
    fig.update_layout(
        showlegend=True
    )
    return fig

# TASK 4: Callback for Scatter Plot
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_scatter_chart(selected_site, payload_range):
    min_payload, max_payload = payload_range
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= min_payload) & 
                           (spacex_df['Payload Mass (kg)'] <= max_payload)]
    
    if selected_site == 'ALL':
        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title='Payload vs. Launch Outcome for All Sites',
            labels={'class': 'Launch Outcome (1=Success, 0=Failure)'}
        )
    else:
        site_df = filtered_df[filtered_df['Launch Site'] == selected_site]
        fig = px.scatter(
            site_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title=f'Payload vs. Launch Outcome for {selected_site}',
            labels={'class': 'Launch Outcome (1=Success, 0=Failure)'}
        )
    
    fig.update_layout(
        xaxis_title='Payload Mass (kg)',
        yaxis_title='Launch Outcome',
        showlegend=True
    )
    return fig

# Run the app
if __name__ == '__main__':
    app.run()

import pandas as pd
import plotly.express as px
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash
from dash.dependencies import Output,Input
from dash.exceptions import PreventUpdate

app=dash.Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP])

#Reading Dataset

df=pd.read_csv('owid-covid-data.csv')

df_2=pd.read_csv('owid-covid-data.csv')


# Finding columns which have empty values greater than fifty-thousand
print(df.isna().sum()>50000)

#Droping Those columns having empty values greater than fifty-thousand
df.drop(['icu_patients','icu_patients_per_million','hosp_patients','hosp_patients_per_million','weekly_icu_admissions','weekly_icu_admissions_per_million',
         'weekly_hosp_admissions','weekly_hosp_admissions_per_million','total_vaccinations','people_vaccinated','people_fully_vaccinated','new_vaccinations',
         'new_vaccinations_smoothed','total_vaccinations_per_hundred','people_vaccinated_per_hundred','people_fully_vaccinated_per_hundred','new_vaccinations_smoothed_per_million',
         ],inplace=True,axis=1)

#finding values for overall world and making a seperate dataframe
df2=df.loc[df['location']=='World',['date','total_cases','new_cases','total_deaths','new_deaths']]

#droping those rows of overallworld from the original dataset so that this dataset only contain indiiviual country
df.drop(index=df2.index,inplace=True)

#filling empty rows using forward fill
df.fillna(method='ffill',inplace=True)




df_high=df_2[df_2['location'].isin(['United States','India','China','France','United Kingdom','Russia'])]

df_2.drop(index=df_high.index,inplace=True)

print(df_2[df_2['location']=='United States'])

df_2['location']='Others'
print(df_2['location'])
df_others_and_countries=pd.concat([df_2,df_high])



# Front-End Layout
app.layout=dbc.Container([
    dbc.Row(
        dbc.Col(
            'Covid DashBoard',className='text-center'
        ),
    ),
    dbc.Row([
        dbc.Col(
            [
            dbc.Card([
                dbc.CardHeader('Global Cases',className="display-4 text-warning",style={'font-family':'sans-serif'}),
                dbc.CardBody(str(df2['total_cases'].sum()), className="text-warning display-4",style={'font-family':'sans-serif'}),
            ],className="text-center",style={'background-color':'black','border':2}),
            dbc.Card([
                dbc.RadioItems(id='selection-case', options=[{'label': 'Total Cases', 'value': 'total_cases'},
                                                             {'label': 'New Cases', 'value': 'new_cases'},
                                                             ], value='total_cases', inline=True, switch=True,className='pl-2',style={'font-family':'sans-serif'}),

                    dcc.Graph(id='case-graph'),


            ],className="mb-3",
                ),

        ],width=3),
        dbc.Col([
            dbc.Card([
            dcc.Graph(id='map',figure=px.choropleth(data_frame=df,locations='iso_code',title="World Condition",template='plotly_dark',height=650),style={'font-family':'sans-serif'}),
            dbc.RadioItems(id='selection-1', options=[{'label': 'New Cases', 'value': 'new_cases'},
                                                      {'label': 'New Deaths', 'value': 'new_deaths'},
                                                      {'label': 'Total Cases', 'value': 'total_cases'},
                                                      {'label': 'Total Deaths', 'value': 'total_deaths'}],
                           switch=True,inline=True,style={'font-family':'sans-serif'}),
                ],className="mb-3")
        ],width=6),
        dbc.Col(
            [
            dbc.Card([
                dbc.CardHeader('Global Deaths',className="display-4 text-danger",style={'font-family':'sans-serif'}),
                dbc.CardBody(str(df2['total_deaths'].sum()),className="text-danger display-4",style={'font-family':'sans-serif'}),
            ],className="text-center",style={'background-color':'black','border':2}),
            dbc.Card([
                    dbc.RadioItems(id='selection-death',options=[{'label':'Total Deaths','value':'total_deaths'},
                                                                 {'label':'New Deaths','value':'new_deaths'}],value='total_deaths',switch=True,inline=True,className='pl-2',style={'font-family':'sans-serif'}),
                    dcc.Graph(id='death-graph')

            ],className="mb-3",
                ),
        ],width=3),
    ]),
        dbc.Row([
        dbc.Col([
            dcc.Dropdown(id='selection_id', options=[{'label':i,'value':i} for i in df.columns],placeholder="Select x-axis",style={'font-family':'sans-serif'}),
            dcc.Dropdown(id='selection_id1', options=[{'label':i,'value':i} for i in df.columns],placeholder="Select y-axis",style={'font-family':'sans-serif'}),
            dcc.Graph(id='line1',style={'font-family':'sans-serif'})
        ]
        )
    ],),
    dbc.Row([
        dbc.Col(
            [
                dbc.RadioItems(id='selection3',options=[{'label':i,'value':i} for i in df['continent'].unique()],switch=True,inline=True,style={'font-family':'sans-serif'}),
                dcc.Graph(
                    id='pie',style={'font-family':'sans-serif'}
                )
            ],width=6,className="text-center",style={'font-family':'sans-serif'}),
            dbc.Col(
                [
                    dcc.Graph(
                        id='pie-world',figure=px.pie(data_frame=df_others_and_countries, values='total_cases', names='location',title="Major Countries Total Cases",template='plotly_dark'),style={'font-family':'sans-serif'}
                    )
                ],width=6,className="text-center pt-4",style={'font-family':'sans-serif'}
            )
    ]),

],fluid=True)



#Call Back function for interactivity


@app.callback(Output('case-graph','figure'),Input('selection-case','value'))
def update_case_graph(selection):
    if selection=='total_cases':
        dff=df2
        fig=px.line(data_frame=dff,x='date',y='total_cases',template='plotly_dark',color_discrete_map={'total_cases':'orange'})
        return fig
    elif selection=='new_cases':
        dff = df2
        fig = px.line(data_frame=dff, x='date', y='new_cases',template='plotly_dark',color_discrete_map={'new_cases':'orange'})
        return fig

@app.callback(Output('death-graph','figure'),Input('selection-death','value'))
def update_death_graph(selection):
    if selection=='total_deaths':
        dff=df2
        fig=px.line(data_frame=dff,x='date',y='total_deaths',template='plotly_dark',color_discrete_map={'total_deaths':'red'})
        return fig
    elif selection=='new_deaths':
        dff = df2
        fig = px.line(data_frame=dff, x='date', y='new_deaths',template='plotly_dark',color_discrete_map={'total_deaths':'red'})
        return fig





@app.callback(Output('map','figure'),Input('selection-1','value'))
def update_map1(selection1):
    if selection1==None:
        raise PreventUpdate
    else:
        print(selection1)
        dff=df
        print(dff['iso_code'])
        fig=px.choropleth(template='plotly_dark',data_frame=dff,locations='iso_code',color=selection1,color_continuous_scale=px.colors.sequential.Reds,title="World Condition on "+str(selection1))
        return fig


@app.callback(Output('pie','figure'),Input('selection3','value'))
def update_pie(selection3):
    if selection3==None:
        raise PreventUpdate
    else:
        print(selection3)
        dff=df.loc[(df['continent']==selection3),['total_cases','iso_code','location']]
        fig=px.pie(data_frame=dff.nlargest(1000,'total_cases'), values='total_cases', names='location',title="Countries with higest Total Cases Based on Continent",template='plotly_dark')
        return fig




@app.callback(Output('line1','figure'),Input('selection_id','value'),Input('selection_id1','value'))
def update_scatter(selection4,selection5):
    if selection4==None and selection5==None:
        raise PreventUpdate
    else:
        dff=df
        print(selection4)
        fig=px.scatter(data_frame=dff,x=selection4,y=selection5,color='continent',title=str(selection4)+" and "+str(selection5),hover_data=['location'],template='plotly_dark')
        return fig




if __name__ == '__main__':
    app.run_server(debug=True)
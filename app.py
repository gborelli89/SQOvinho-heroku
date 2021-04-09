import os

import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go

# Carregando dados
d = pd.read_csv('https://raw.githubusercontent.com/gborelli89/SQOvinho-heroku/main/harm_vinhos.csv', delimiter=';')
d = d.set_index('Tipo')
ex = pd.read_csv('https://raw.githubusercontent.com/gborelli89/SQOvinho-heroku/main/ex_alimentos.csv', delimiter=';')
ex = ex.set_index('alimento')

# Nomes dos alimentos
foodnames1 = list(d.columns)
foodnames2 = foodnames1.copy()
foodnames2.insert(0, 'Nenhum')

def harmfun(a1, x1, a2, x2):
    return (a1*x1 + a2*x2)/(a1+a2)

def colorfun(v, g=0.75, maincol='rgba(128,128,128,0.5)', chosencol='rgba(0,186,182,0.6)'):
    
    rescol = [maincol for _ in v]
    id = [x[0] for x in enumerate(v) if x[1] > g]
    
    for i in id:
        rescol[i] = chosencol
    
    return rescol


# Inicia aplicativo

app = dash.Dash(__name__,
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0, maximum-scale=1.4, minimum-scale=0.8,'}]
                )

server = app.server

app.layout = html.Div([
    html.Div(
        html.Img(src='https://raw.githubusercontent.com/gborelli89/SQOvinho-heroku/main/seraqorna.png', style = {'width':'60%'}),
        style={'textAlign':'center'} 
    ),

    html.Div([
        html.H3('Elemento principal'),
        dcc.Dropdown(
            id = 'food1',
            options = [{'label':i, 'value':i} for i in foodnames1],
            value = 'Queijos delicados',
        ),
        html.H5('Intensidade'),
        dcc.Slider(
            id = 'weight1',
            min = 0.1,
            max = 1.0,
            step = 0.1,
            value = 1.0
        ),
        html.P(id = 'ex-food1'),

        html.Br(),

        html.H3('Elemento secundário'),
        dcc.Dropdown(
            id = 'food2',
            value = 'Nenhum',
        ),
        html.H5('Intensidade'),
        dcc.Slider(
            id = 'weight2',
            min = 0.1,
            max = 1.0,
            step = 0.1,
            value = 0.7
        ),
        html.P(id = 'ex-food2'),

        html.Br(),

        html.H6('Harmonização dos elementos individuais baseadas no livro O guia essencial do vinho: Wine Folly, 1. ed. 2016.'),

    ], style = {'width':'28%', 'display':'inline-block'} ),

    html.Div(
        dcc.Graph(id = 'graph'),
        style = {'width':'70%', 'float':'right'}
    )
])

@app.callback(
    [Output('graph','figure'), Output('ex-food1','children'), Output('food2','options'), Output('ex-food2','children')],
    [Input('food1','value'), Input('weight1','value'), Input('food2','value'), Input('weight2','value')]
)
def update_output(selected_food1, w1, selected_food2, w2):
    
    if selected_food2 == 'Nenhum':
        val = harmfun(w1, d[selected_food1], 0, d[selected_food1])
        ex2 = ''
    else:
        val = harmfun(w1, d[selected_food1], w2, d[selected_food2])
        ex2 = list(ex.loc[selected_food2])
        ex2.insert(0, 'Exemplos: ')
        ex2 = ''.join(ex2)

    fig =  go.Figure([go.Bar(x=list(val), y=list(d.index), orientation='h', marker_color=colorfun(list(val)))])
    fig.update_layout(plot_bgcolor='rgb(255,255,255)')
    fig.update_xaxes(title='Harmonização', nticks=0, tickvals=[0.0,0.5,1.0], ticktext=['Não harmoniza','Boa','Excelente'])


    ex1 = list(ex.loc[selected_food1])
    ex1.insert(0, 'Exemplos: ')
    ex1 = ''.join(ex1)

    opt2 = [{'label':x, 'value':x} for x in foodnames2 if x != selected_food1]

    return [fig, ex1, opt2, ex2]

if __name__ == '__main__':
    app.run_server(debug=True)

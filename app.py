import os

import numpy as np
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
ex = ex.set_index('Alimento')
wi = pd.read_csv('https://raw.githubusercontent.com/gborelli89/SQOvinho-heroku/main/intensidade_vinhos.csv', delimiter=';')

# Nomes dos alimentos
foodnames1 = list(d.columns)
foodnames2 = foodnames1.copy()
foodnames2.insert(0, 'Nenhum')

def findclose(s, value):
    maxval = s.Intensidade[s.Intensidade >= value].min()
    minval = s.Intensidade[s.Intensidade <= value].max()

    a = s.index[s.Intensidade == minval]
    b = s.index[s.Intensidade == maxval]

    return a.tolist() + b.tolist()


def findharm(df,wine_int):
    id = [x[0] for x in enumerate(df) if x[1] > 0]
    r = wine_int.iloc[id]
    range_values = np.linspace(min(r.Intensidade), max(r.Intensidade), 5).tolist()
    res = [findclose(r,i) for i in range_values]
    return res


def colorfun(v, id, maincol='rgba(128,128,128,0.5)', chosencol='rgba(0,186,182,0.6)'):
    
    rescol = [maincol for _ in v]
    
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
        html.Img(src='https://raw.githubusercontent.com/gborelli89/SQOvinho-heroku/main/seraqorna.png', style = {'width':'90%'}),
        style={'textAlign':'center'} 
    ),

    html.Div([
        html.H3('Classe principal'),
        dcc.Dropdown(
            id = 'food1',
            options = [{'label':i, 'value':i} for i in foodnames1],
            value = 'Queijos delicados',
        ),
        html.H4('Intensidade dentro da classe selecionada'),
        dcc.Slider(
            id = 'weight1',
            min = 0,
            max = 4,
            step = None,
            marks={
                0:'1',
                1:'2',
                2:'3',
                3:'4',
                4:'5'
            },
            value = 0
        ),
        html.P(id = 'ex-food1'),

    ], style = {'width':'100%'}#, 'display':'inline-block'} 
    ),

    html.Div([
        dcc.Graph(id = 'graph', config={'displayModeBar':False}),
    
    ], style = {'width':'100%'}#, 'float':'right'}
    ),

    html.Div(
        html.H6('Harmonização das classes baseadas no livro O guia essencial do vinho: Wine Folly, 1. ed. 2016.')
    )
    
])

@app.callback(
    [Output('graph','figure'), Output('ex-food1','children')],
    [Input('food1','value'), Input('weight1','value')]
)
def update_output(selected_food1, w1):
    
    val = d[selected_food1]
    harm = findharm(val, wi)
    # if selected_food2 == 'Nenhum':
    #     val = harmfun(w1, d[selected_food1], 0, d[selected_food1])
    #     ex2 = ''
    # else:
    #     val = harmfun(w1, d[selected_food1], w2, d[selected_food2])
    #     ex2 = list(ex.loc[selected_food2])
    #     ex2.insert(0, 'Exemplos: ')
    #     ex2 = ''.join(ex2)

    #fig =  go.Figure([go.Bar(x=list(d.index), y=list(val), marker_color=colorfun(list(val)))])
    #fig.update_yaxes(title='Harmonização', nticks=0, tickvals=[0.0,0.5,1.0], ticktext=['C','B','A'])
    ylabels = ['E','BL','BE','BA','R','TL','TMC','TE','S']
    fig =  go.Figure([go.Bar(x=list(val), y=ylabels, orientation='h', marker_color=colorfun(val,harm[w1]), hoverinfo='text',
                        hovertext=['Espumante','Branco leve','Branco encorpado','Branco aromático','Rosè',
                        'Tinto leve','Tinto de médio corpo','Tinto encorpado','Sobremesa'])])
    fig.update_xaxes(title='Harmonização',nticks=0, tickvals=[0.0,0.5,1.0], ticktext=['Não harmoniza','Boa','Excelente'], fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    fig.update_layout(plot_bgcolor='rgb(255,255,255)', margin={'l':10, 'r':10})


    ex1 = list(ex.loc[selected_food1])
    ex1.insert(0, 'Exemplos: ')
    ex1 = ''.join(ex1)

    #opt2 = [{'label':x, 'value':x} for x in foodnames2 if x != selected_food1]

    return [fig, ex1]

if __name__ == '__main__':
    app.run_server(debug=True)

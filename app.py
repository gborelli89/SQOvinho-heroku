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
#foodnames2 = foodnames1.copy()
#foodnames2.insert(0, 'Nenhum')

# Encontrando valores superior e inferior mais próximos
def findclose(s, value):
    maxval = s.Intensidade[s.Intensidade >= value].min()
    minval = s.Intensidade[s.Intensidade <= value].max()
    a = s.index[s.Intensidade == minval]
    b = s.index[s.Intensidade == maxval]
    return a.tolist() + b.tolist()

# Encontrando sugestão de harmonização
def findharm(df,wine_int):
    id = [x[0] for x in enumerate(df) if x[1] > 0]
    r = wine_int.iloc[id]
    range_values = np.linspace(min(r.Intensidade), max(r.Intensidade), 3).tolist()
    res = [findclose(r,i) for i in range_values]
    return res

# Função genérica que pode ser utilizada para definir cores e labels
def idfun(v, id, mainstring, chosenstring):
    
    restring = [mainstring for _ in v]
    
    for i in id:
        restring[i] = chosenstring
    
    return restring



# Inicia aplicativo
# UI
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
        html.H3('Alimento principal'),
        dcc.Dropdown(
            id = 'food1',
            options = [{'label':i, 'value':i} for i in foodnames1],
            value = 'Queijos delicados',
            clearable=False,
            searchable=False
        ),
        html.H4('Qual a intensidade do alimento?'),
        html.P("Exemplo com a seleção de peixes:"),
        html.Li("Tilápia, truta - Baixa"),
        html.Li("Filhote, cação - Média"),
        html.Li("Salmão, atum - Alta"),
        html.Br(),
        dcc.Slider(
            id = 'weight1',
            min = 0,
            max = 2,
            step = None,
            marks={
                0:'Baixa',
                1:'Média',
                2:'Alta'
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

# Callback
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

    ylabels = ['E','BL','BE','BA','R','TL','TMC','TE','S']
    wine_labels = ['<b>Espumante</b><br>Champagne, Cava, Prosecco<br>',
                    '<b>Branco leve</b><br>Sauvignon Blanc, Pinot Gris<br>Albariño, Muscadet, Vermentino',
                    '<b>Branco encorpado</b><br>Chardonnay, Viognier, Sémillon',
                    '<b>Branco aromático</b><br>Riesling, Chenin Blanc<br>Torrontés, Gewürztraminer',
                    '<b>Rosè</b>',
                    '<b>Tinto leve</b><br>Pinot Noir, Gamay',
                    '<b>Tinto de médio corpo</b><br>Merlot, Carménère, Cabernet Franc<br>Grenache, Barbera, Montepulciano, Negroamaro<br>Sangiovese, Primitivo (Zinfandel), Valpolicella',
                    '<b>Tinto encorpado</b><br>Cabernet Sauvignon, Malbec, Bordeaux<br>Nebbiolo, Syrah, Tempranillo, Pinotage<br>Nero D&#39;Avola, Touriga Nacional',
                    '<b>Sobremesa</b><br>Porto, Madeira, Marsala<br>Vin Santo, Xerez']
    
    colors = {'Sugestões': 'rgba(0,186,182,0.6)',
                'Outras opções': 'rgba(128,128,128,0.5)'}
    legendnames = idfun(val, harm[w1], mainstring='Outras opções', chosenstring='Sugestões')

    wdf = pd.DataFrame({'x': list(val),
                        'y': [0,1,2,3,4,5,6,7,8],
                        'label': legendnames,
                        'wines': wine_labels})

    fig =  go.Figure()

    for label, label_df in wdf.groupby('label'):    
        fig.add_trace(go.Bar(x=label_df.x, y=label_df.y, name=label, marker={'color': colors[label]}, orientation='h',
                            hoverinfo='text', hovertext=label_df.wines))

    fig.update_xaxes(title='Harmonização',nticks=0, tickvals=[0.0,0.5,1.0], ticktext=['Não harmoniza','Boa','Excelente'], fixedrange=True)
    fig.update_yaxes(tickvals=[0,1,2,3,4,5,6,7,8], ticktext=ylabels, fixedrange=True)
    fig.update_layout(plot_bgcolor='rgb(255,255,255)', margin={'l':10, 'r':10}, 
                    legend=dict(
                        orientation='h',
                        yanchor='bottom',
                        y=1,
                        xanchor='right',
                        x=1
                    ))


    ex1 = list(ex.loc[selected_food1])
    ex1.insert(0, 'Exemplos: ')
    ex1 = ''.join(ex1)

    #opt2 = [{'label':x, 'value':x} for x in foodnames2 if x != selected_food1]

    return [fig, ex1]

if __name__ == '__main__':
    app.run_server(debug=True)

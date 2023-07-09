import dash_bootstrap_components as dbc
from dash import dcc
from dash import html

import dash
from dash import html, dcc

from lib.NewsSentiment import DB_interaction, MarketSentiment, SentimentMap

dash.register_page(__name__, path='/')

##########################
## Create the marketsentiment analysis
db = DB_interaction()
#ms = MarketSentiment()
#ms.addCityIndexes(db.getCityIndexesDict())
sm = SentimentMap(db.getLatestSentiment())

figure_news_sentiment = sm.fig

layout = html.Div(children=[
  dbc.Container(
    [
      html.Center(dbc.Row(
        [
          dbc.Col(
            [
              dcc.Graph( id='graph-news_sentiment', figure=figure_news_sentiment),
            ]
          ),
        ]
      ))
    ]
  )
])

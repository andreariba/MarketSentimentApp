import dash
from dash import dcc, html
import dash_bootstrap_components as dbc

from navbar import Navbar

import argparse

from dotenv import load_dotenv

# load env variables
load_dotenv()

# parse the arguments: exposed port, 
parser = argparse.ArgumentParser(
                    prog='Market Sentiment App',
                    description='The Dash app allows to have a quick overview of the main market or specific keyword sentiment.')
parser.add_argument('--port', type=int, default=8060, help='app port to expose')
args = parser.parse_args()

print("\n**** Market Sentiment App ****\n")
print("[Dash version]:", dash.__version__)
# print("[Pandas version]:", pd.__version__)
# print("[Numpy version]:", np.__version__)

##########################
## Create the app
app = dash.Dash(__name__, use_pages=True, external_stylesheets = [dbc.themes.LUX])
app.config.suppress_callback_exceptions = True
app.layout = html.Div([
  dcc.Location(id='url', refresh=True),
  Navbar(),
  dash.page_container
])
app.title = 'MarketSentimentApp'

# run the app
if __name__=='__main__':
  print("Starting the server ...")
  app.run_server(host='0.0.0.0', port=args.port, debug=False)


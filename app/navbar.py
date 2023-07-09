import dash
import dash_bootstrap_components as dbc

def Navbar():

  navbar = dbc.NavbarSimple(
    children = [
      dbc.NavItem(dbc.NavLink("map", href=dash.page_registry['pages.map']['path'])),
    ],
    brand="Market Sentiment App",
    brand_href="/",
    sticky="top"
  )
    
  return navbar

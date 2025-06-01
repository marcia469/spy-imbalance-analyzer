import pandas as pd
from sqlalchemy import create_engine, text
import dash
from dash import html, dcc, Input, Output, State, dash_table
from datetime import date, timedelta, datetime
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from dash.exceptions import PreventUpdate
import numpy as np
import traceback

# DB Config
DB_CONFIG = {
    'host': 'alpine-vbam-prod.c7wvpkbyvjzb.us-east-1.rds.amazonaws.com',
    'port': 3306,
    'user': 'VBAM_Read',
    'password': 'read-VBAM-^6',
    'database': 'auctionResearch'
}

def get_engine():
    conn_str = (
        f"mysql+mysqlconnector://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
        f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    )
    return create_engine(conn_str)

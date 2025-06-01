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
    
def resolve_date_range(filter_type):
    today = date.today()
    if filter_type == "mtd":
        return today.replace(day=1), today
    elif filter_type in ["last_7", "last_20", "last_40"]:
        return today - timedelta(days=int(filter_type.split('_')[1])), today
    elif filter_type == "3rd_friday":
        return today - timedelta(days=365), today
    elif filter_type == "month_end":
        return today - timedelta(days=365), today
    elif filter_type == "t_minus_1":
        return today - timedelta(days=365), today
    return None, None

def get_third_fridays(start_date, end_date):
    """Get all third Fridays between start_date and end_date"""
    third_fridays = []
    current_date = start_date.replace(day=1)
    
    while current_date <= end_date:
        first_day = current_date.replace(day=1)
        days_until_friday = (4 - first_day.weekday()) % 7
        first_friday = first_day + timedelta(days=days_until_friday)
        third_friday = first_friday + timedelta(days=14)
        
        if (start_date <= third_friday <= end_date and 
            third_friday.month == current_date.month):
            third_fridays.append(third_friday)
        
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1)
    
    return third_fridays

def get_month_end_trading_days(start_date, end_date):
    """Get the last trading day of each month between start_date and end_date"""
    month_end_days = []
    current_date = start_date.replace(day=1)
    
    while current_date <= end_date:
        if current_date.month == 12:
            next_month = current_date.replace(year=current_date.year + 1, month=1)
        else:
            next_month = current_date.replace(month=current_date.month + 1)
        
        last_day_of_month = next_month - timedelta(days=1)
        last_trading_day = last_day_of_month
        while last_trading_day.weekday() > 4:
            last_trading_day -= timedelta(days=1)
        
        if start_date <= last_trading_day <= end_date:
            month_end_days.append(last_trading_day)
        
        current_date = next_month
    
    return month_end_days

def get_t_minus_1_days(start_date, end_date):
    """Get T-1 (day before last trading day) of each month between start_date and end_date"""
    t_minus_1_days = []
    month_end_days = get_month_end_trading_days(start_date, end_date)
    
    for month_end_day in month_end_days:
        t_minus_1 = month_end_day - timedelta(days=1)
        while t_minus_1.weekday() > 4:
            t_minus_1 -= timedelta(days=1)
        
        if start_date <= t_minus_1 <= end_date:
            t_minus_1_days.append(t_minus_1)
    
    return t_minus_1_days


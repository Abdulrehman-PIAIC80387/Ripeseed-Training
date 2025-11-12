import os
import calendar
from datetime import datetime
import argparse

def fetch_month_string(date):
    date = datetime.strptime(f'{date}', '%Y-%m-%d').date()
    month = date.strftime("%B")
    return month


def fetch_day_string(date):
    date = datetime.strptime(f'{date}', '%Y-%m-%d').date()
    day = date.day
    return day


def get_files_for_year(data_dir, year):
    file_list = []
    
    if not os.path.exists(data_dir):
        return file_list
    
    for root, dirs, files in os.walk(data_dir):
        for file in files:
            if str(year) in file and file.endswith('.txt'):
                full_path = os.path.join(root, file)
                file_list.append(full_path)
    
    return file_list


def get_files_for_month(data_dir, year, month):
    file_list = []
    
    if not os.path.exists(data_dir):
        return file_list
    
    month_name = calendar.month_name[month][:3]

    for root, dirs, files in os.walk(data_dir):
        for file in files:
            if str(year) in file and month_name in file:
                full_path = os.path.join(root, file)
                file_list.append(full_path)
    
    return file_list


def load_year_data(parser, file_list):
    all_readings = []
    
    for file_path in file_list:
        readings = parser.parse_file(file_path)
        all_readings.extend(readings)
    
    return sorted(all_readings, key=lambda r: r.date)


def load_month_data(parser, file_list, year, month):
    all_readings = []
    
    for file_path in file_list:
        readings = parser.parse_file(file_path)
        all_readings.extend(readings)
    
    return sorted(all_readings, key=lambda r: r.date)


def parse_year_month(value):
    try:
        parts = value.split('/')
        year = int(parts[0])
        month = int(parts[1])
        return (year, month)
    except (ValueError, IndexError):
        raise argparse.ArgumentTypeError(f"Invalid format: {value}")
    

def fetch_day_string(date_str):
    date = datetime.strptime(date_str, "%Y-%m-%d")
    return date.day

def fetch_month_string(date_str):
    date = datetime.strptime(date_str, "%Y-%m-%d")
    return date.strftime("%B")








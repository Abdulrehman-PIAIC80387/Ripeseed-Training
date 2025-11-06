import argparse
import os
from parser.file_parser import parse_weather_file
from calculations.calculate_stats import calculate_yearly_stats
from calculations.calculate_averages import calculate_monthly_averages
from reports.yearly_reports import print_yearly_report
from reports.monthly_reports import print_monthly_averages_report
from reports.bar_charts import print_bar_chart, print_bar_chart_single_liner
from utils.helpers import get_files_for_year, get_files_for_month,load_year_data,load_month_data,parse_year_month


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('data_dir')
    parser.add_argument('-e', type=int, dest='yearly_year')
    parser.add_argument('-a', type=parse_year_month, dest='monthly_avg')
    parser.add_argument('-c', type=parse_year_month, dest='monthly_chart')
    parser.add_argument('-s', action='store_true', dest='bonus_mode')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.data_dir):
        print("Error: Directory not found")
        return
    
    if args.yearly_year is not None:
        readings = load_year_data(args.data_dir, args.yearly_year)
        if len(readings) > 0:
            stats = calculate_yearly_stats(readings)
            print_yearly_report(stats)
            
            if args.monthly_avg or args.monthly_chart:
                print()

    if args.monthly_avg is not None:
        year, month = args.monthly_avg
        readings = load_month_data(args.data_dir, year, month)
        
        if len(readings) > 0:
            averages = calculate_monthly_averages(readings)
            print_monthly_averages_report(averages)
            
            if args.monthly_chart:
                print()

    if args.monthly_chart is not None:
        year, month = args.monthly_chart
        readings = load_month_data(args.data_dir, year, month)
        
        if len(readings) > 0:
            if args.bonus_mode:
                print_bar_chart_single_liner(readings)
            else:
                print_bar_chart(readings)


if __name__ == '__main__':
    main()
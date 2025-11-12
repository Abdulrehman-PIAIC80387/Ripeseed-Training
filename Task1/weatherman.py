import argparse
import os
from calculations import calculator
from reports import reports_generator
from parser.file_parser import WeatherFileParser
from utils.helpers import get_files_for_year, get_files_for_month, load_year_data, load_month_data, parse_year_month


def main():
    parser_arg = argparse.ArgumentParser()
    parser_arg.add_argument('data_dir')
    parser_arg.add_argument('-e', type=int, dest='yearly_year')
    parser_arg.add_argument('-a', type=parse_year_month, dest='monthly_avg')
    parser_arg.add_argument('-c', type=parse_year_month, dest='monthly_chart')
    parser_arg.add_argument('-s', action='store_true', dest='bonus_mode')
    
    args = parser_arg.parse_args()
    
    if not os.path.exists(args.data_dir):
        print("Error: Directory not found")
        return

    reports_obj = reports_generator.Reports()
    calculations_obj = calculator.Calculations()
    file_parser = WeatherFileParser()
    
    if args.yearly_year is not None:
        file_list = get_files_for_year(args.data_dir, args.yearly_year)
        readings = load_year_data(file_parser, file_list)
        if len(readings) > 0:
            stats = calculations_obj.calculate_yearly_stats(readings)
            reports_obj.print_yearly_report(stats)
            

    if args.monthly_avg is not None:
        year, month = args.monthly_avg
        file_list = get_files_for_month(args.data_dir, year, month)
        readings = load_month_data(file_parser, file_list, year, month)
        
        if len(readings) > 0:
            averages = calculations_obj.calculate_monthly_averages(readings)
            reports_obj.print_monthly_averages_report(averages)
            
    if args.monthly_chart is not None:
        year, month = args.monthly_chart
        file_list = get_files_for_month(args.data_dir, year, month)
        readings = load_month_data(file_parser, file_list, year, month)
        
        if len(readings) > 0:
            if args.bonus_mode:
                reports_obj.print_bar_chart_single_liner(readings)
            else:
                reports_obj.print_bar_chart(readings)


if __name__ == '__main__':
    main()
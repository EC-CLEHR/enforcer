import csv
from parser import *

from src.lib.helper.log_helper import Logging


class CSVHelper:  # TODO ENG-38315
    """
    To read and fetch data from CSV
    """

    def __init__(self, csv_path):
        self.log_helper = Logging
        self.csv_path = csv_path

    def get_list_from_csv_orion(self):
        """
        To fetch data from csv file
        :return List of data from csv
        """
        try:
            data_list = []

            f = open(self.csv_path, encoding='utf-8-sig')
            csv_reader_obj = csv.reader(f)
            headers = next(csv_reader_obj)  # store headers and capture data after headers
            headers = list(map(str.strip, headers))
            for line in csv_reader_obj:
                data_list.append(line)
            return headers, data_list
        except Exception as ex:
            raise ParserError("Issue while fetching csv data into list :" + str(ex))

    @staticmethod
    def create_csv(path, row_data: list):
        # open the file in the write mode
        with open(path, 'w') as f:
            # create the csv writer
            writer = csv.writer(f)

            # write a row to the csv file
            for row in row_data:
                writer.writerow(row)

    def add_data_to_csv(file_name, headers, data):
        """
        Adding CSV details to a file with headers and data
        :param file_name: name of CSV file
        :param headers: CSV file headers
        :param data: Rows that need to be added into the CSV file
        :return none
        """
        with open(file_name, 'w') as csvfile:
            # creating a csv writer object
            csvwriter = csv.writer(csvfile)
            # writing the fields
            csvwriter.writerow(headers)
            csvwriter.writerow(data)
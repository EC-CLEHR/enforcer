# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

test_Environment = ''

# URL
class Url:
    def api_base_url(self, test_Environment):
        if test_Environment == 'dev':
            Base_Url = f'https://devccm.enablecomp.com/'
        elif test_Environment == 'prod':
            Base_Url = f'https://ccm.enablecomp.com/'
        else:
            Base_Url = f'https://devccm.enablecomp.com/'
        return Base_Url

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

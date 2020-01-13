# budget
A simple telegram bot to account for expenses when renting a room

to install:
1) pip install Flask
2) in config.ini:
  1) token - this is the token of your telegram bot
  2) name_list - list of nicknames involved in budgeting
  3) id - this is telegram id of user
  4) renta - this is the amount of monthly rent for this user. This amount will be charged by the command \pay_renta
3) python3 main.py
4) budget.json and log.csv will be created automatically

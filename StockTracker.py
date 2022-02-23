# ------------------------------------------------------------------------------------------------ #
#    This application sends a user an email if the stock's price goes bellow a specified amount    #
# ------------------------------------------------------------------------------------------------ #

from selenium import webdriver
import time
import yagmail
import os
import re
from datetime import datetime as dt
from pytz import timezone
from selenium.webdriver.common.keys import Keys

valid_email = "^[-!#$%&'*+/0-9=?A-Z^_a-z{|}~](\.?[-!#$%&'*+/0-9=?A-Z^_a-z{|}~])*@[a-zA-Z](-?[a-zA-Z0-9])*(\.[a-zA-Z](-?[a-zA-Z0-9])*)+$"

# ------------- checks if the stock market is open ------------- #

def check_time():
    global market, emailing
    Eastern = timezone('US/Eastern')
    market_hours = dt.now(Eastern)
    now = dt.now()
    market_open = now.replace(hour = 9, minute = 30)
    market_open = Eastern.localize(market_open)
    market_close = now.replace(hour = 16, minute = 00)
    market_close = Eastern.localize(market_close)
    day = dt.isoweekday(market_hours)

    while True:
        time.sleep(60)
        if day >= 1 and day < 6:
            if market_hours > market_open and market_hours < market_close:
                market = True
                return market
            else:
                market = False
                emailing = False
                market_open = market_open.strftime("%I:%M %p")
                market_close = market_close.strftime("%I:%M %p")
                print(f'The stock market is closed at the moment.\nPlease try again in market hours: {market_open}, {market_close}, Monday through Friday')
                quit()
        else:
            market = False
            emailing = False
            print('The stock market is not open during the weekends.\nPlease try again during the work week.')
            quit()
            

# -------------------------- validates email address ------------------------- #
def check_sender():
    global sender
    global sndr
    while sndr == True:
        sender = input("Please enter your email address.\n")
        match = re.fullmatch(valid_email, sender)   
        if match is None:
            print('Please enter a valid email address.\n')
            continue
        else:
            sndr = False


def check_change():
    global emailing, stock, stock_short, stock_change, value_floor, value_ceiling, stock_ceiling, stock_floor
    # ----------- Setting up parameters to allow for easier webscraping ---------- #
    options = webdriver.ChromeOptions()
    options.add_argument("disable-infobars") # Disables information bar that might distract from web scraping.
    options.add_argument("start-maximized") # Starts the browser full size
    options.add_argument("disable-dev-shm-usage")
    options.add_argument("no-sandbox") # Allows greater privileges on the webpage.

    # -------------- These help us avoid detection when web scraping ------------- #

    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("excludeSwitches", ["enable-logging"]) 
    options.add_argument("disable-blink-features=AutomationControlled")
    confirming = True
    
    while confirming: 
        desired_stock = input('Please enter your desired stock:\n')

        driver = webdriver.Chrome(options = options)
        driver.get("https://finance.yahoo.com/")
        time.sleep(1)
        driver.find_element(by='xpath', value='//*[@id="yfin-usr-qry"]').send_keys(desired_stock + Keys.RETURN)
        driver.minimize_window()
        
        
        # ------------------------ verifies the stock exists in yahoo's directory ------------------------ #
        while True:
            try:
                d = driver.find_element(by='xpath', value='//*[@id="quote-header-info"]/div[2]/div[1]/div[1]/h1')
                print(f'You have chosen {d.text}')
                change_it = input('Is this the stock you would like to watch for? Y/N?\n')
                if change_it[0].upper() == 'Y':
                    confirming = False
                    break
                elif change_it[0].upper() == 'N':
                    confirming = True
                    break
                else:
                        print('Please enter Y/n.\n')
                        continue        
            except:
                    driver.find_element(by='xpath', value='/html/body/div[1]')
                    print('Check to make sure you entered a valid stock.\n')
                    continue
    # ---------------------------------------- set alert limit --------------------------------------- #
    stock = d.text
    while market == True:
        while True:   # Set the alert for when stock increases/decreases by this % or more
            notifier = False
            limit_type = int(input('When would you like to be notified :\n1. Significant percentage change.\n2. Stock drops below set value .\n3. Stock rises over set value.\n'))
            while notifier == False:
                if limit_type == 1:
                    percentage = input('Set the alert for when stock increases/decreases by this % or more:\n')
                    try:
                        percentage = float(percentage)
                    except ValueError:
                        print('Please input an integer or a float, not a string.\n')
                        continue
                    print(f"{stock} is being tracked! you will be notified if it changes by {percentage}%\n")
                    time.sleep(10) # every 10 seconds it'll check again for changes
                    
                    stock_change = driver.find_element(by = "xpath", value = '//*[@id="quote-header-info"]/div[3]/div[1]/div[1]/fin-streamer[3]/span')
                    stock_change = stock_change.text
                    stock_change = re.sub("[()]","", stock_change)
                    stock_change_clean = float(stock_change.strip('$%'))

                    if abs(stock_change_clean) >= float(percentage):
                        emailing = True
                        notifier = True
                        return d, stock_change
                    else:
                        emailing = False
                        continue 
                elif limit_type == 2:
                    value_floor = input(f'Please enter a value floor to be notified if {stock} drops below it.\n')
                    try:
                        value_floor = float(value_floor)
                    except ValueError:
                        print('Please input an integer or a float, not a string.\n')
                        continue
                    print(f"{stock} is being tracked! you will be notified if it drops below {value_floor}\n")
                    time.sleep(10)
                    stock_floor = driver.find_element(by ="xpath", value = '//*[@id="quote-header-info"]/div[3]/div[1]/div[1]/fin-streamer[1]')
                    stock_floor = stock_floor.text
                    
                    if float(stock_floor) < value_floor:
                        emailing = True
                        notifier = True
                        return d, stock_floor, value_floor
                    else:
                        emailing = False
                        continue 

                elif limit_type == 3:
                    value_ceiling = input(f'Please enter a value ceiling to be notified if {stock} rises above it.\n')
                    try:
                        value_ceiling = float(value_ceiling)
                    except ValueError:
                        print('Please input an integer or a float, not a string.\n')
                        continue
                    print(f"{stock} is being tracked! you will be notified if it rises above {value_ceiling}\n")
                    time.sleep(10)
                    stock_ceiling = driver.find_element(by ="xpath", value = '//*[@id="quote-header-info"]/div[3]/div[1]/div[1]/fin-streamer[1]')
                    stock_ceiling = stock_ceiling.text
                    
                    if float(stock_ceiling) > value_ceiling:
                        emailing = True
                        notifier = True
                        return d, stock_ceiling, value_ceiling
                    else:
                        emailing = False
                        continue
                else:
                    print('Please pick an option between 1 to 3.\n')
                    continue      


def main():
    market = True
    while market == True:
        global sndr
        sndr = True
            
        check_time()
        check_sender()
        check_change()
        
        while emailing:

            subject = f'A Significant Change in {stock} Detected'


            try:
                if stock_change:
                    contents = f'Dear User,\nA significant change in {stock} has been detected.\nThe change in index is {stock_change}%.\nYou will be notified if any other significant changes will occur within market hours.'
            except NameError:
                try:
                    if stock_ceiling:
                        contents = f'Dear User,\nA significant change in {stock} has been detected.\n{stock} rose above {value_ceiling} to a value of {stock_ceiling}.\nYou will be notified if any other significant changes will occur within market hours.'
                except NameError:
                    contents = f'Dear User,\nA significant change in {stock} has been detected.\n{stock} dropped below {value_floor} to a value of {stock_floor}.\nYou will be notified if any other significant changes will occur within market hours.'

            # Make sure you've made an environment variable as your app password to login to your email account.
            # for more information please refer to the readme file.
            yag = yagmail.SMTP(user=sender, password=os.getenv('PASSWORD'))

            yag.send(to=sender, subject=subject, contents=contents)
main()

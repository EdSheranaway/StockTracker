# StockTracker

This command line application automates checking stock market changes on a requested stock using https://finance.yahoo.com/ and sends the user an email notifiying if it surpasses a defined limit. This app requires the user to set up an environment variable to access their email. in order to setup an environment variable please refer to: https://chlee.co/how-to-setup-environment-variables-for-windows-mac-and-linux/

It uses regular expressions to validate the email, selenium to webscrape real time stock information, and datetime module to confirm whether the stock market is open or not.

## weather-notify-bot
    .Synopsis

    Author:
        KeepCalmWherever

    Purposes:
        Tried to develop telegram bot which requires you to authenticate via email and then shows weather with period from 1 to 3 days (for free API requests it's limited as this :) )

        About script flow, firstly to use this bot you need to have public account for email notification, while first running script requires from you enter next params:

            External API key - Ext_Key
            API link - Api_link (I used API from https://www.weatherapi.com/docs/ that's the bot works only with link http://api.weatherapi.com/v1 but it can be tuned easily for another ;) )
            Bout API key - Bot_Api_key

            Your notify email - Enc_Work_email
            Your app external password from notify email - Enc_Work_email_pass
            SMTP server name on which you registred your notify email - Enc_Work_email_smtp

            All this data will be encypted via ryptography.fernet and put to file with name _credential.json in root directory, a key will be placed also there what is not secure but for learning purposes it's OK :) structure of file is below
            [
                {
                    "Api_link": "",
                    "Ext_Key": "",
                    "Bot_Api_key": "",
                    "Enc_Work_email": "",
                    "Enc_Work_email_pass": "",
                    "Enc_Work_email_smtp": "",
                    "Enc_key": ""
                }
            ]

        After user will need to pass verification by clicking /registration and then /validatecode, code will be sent to entered by user email, email itself is checking via regular expression , all this data is saved in file with name _registration_logs.json
        Of cource we might use database but for learning purpoces it's also OK, structure of file is below:
        [
            {
                "id": "dummy",
                "username": "dummy",
                "mail": "dummy",
                "code": "dummy",
                "registred": "dummy",
                "city": "dummy"
            }....
        ]

    Functions:
        outside bot:
            def convert_json(weather_json, range_ = None)
            def _creds(action, file_name = None) - this function saves creds which will be used for API queries and working with BOT, saved in fie with nae _credential.json
            def _collect_weather_info(params) - api function itself, works only with http://api.weatherapi.com/v1 but can be tuned easily for other APIs, extracts weather data
            def _create_reg_file() - saves initial file with dummy user
            def _generateCodeAndlog(email) - saves intial data about user and saved as well code for verification
            def _sendmail(email, code = None, notify = None) - send notify email with code to pass verification and if code matches after it sends confirmation email
            def _parseaddress(email) - checks if entered email is valid or not

        inside bot handler:
            def start(message) - start command
            def message_handler(message) - parser for text entered by user in bot
            def registration(email) - to initiate registration steps, user will need to enter email address and after pass /validatecode
            def valid_code(auth) - to validate code if user provides the same code as received by entered email, if they match confirmation email is sent to him after
            def setcity(city) - set city name for checking weather, might be changed by passing /setcity, saved in _registration_logs.json file
            def save_json(second) - save city name in _registration_logs.json or update currenct value
            def checkweather(period) - period for weather checking 1, 2 and 3 days, thise periods are restricted by API resource
    Comment:
        Thanks https://www.weatherapi.com for free API requests which are enough in learning purposes :)

"""""""""
    .Synopsis
    
    Author: 
        KeepCalmWherever
        
    Purposes: 
        Tried to develop telegram bot which requires you to authenticate via email and then shows weather with period from 1 to 3 days (for free API requests it's limited as this :) )

"""""""""

import json, telebot, smtplib, random, re, os, requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from os.path import exists as file_exists
from cryptography.fernet import Fernet
from getpass import getpass

# convet json
def convert_json(weather_json, range_ = None):
    String = '************************************'
    if range_ == None:
        String +=  f'''

Time: {str(weather_json['location']['localtime'])}\n
City: {str(weather_json['location']['name'])}\n
Region: {str(weather_json['location']['region'])}\n 
Current Temp (C): {str(weather_json['current']['temp_c'])}\n
State: {str(weather_json['current']['condition']['text'])}\n
Wind (MPH): {str(weather_json['current']['wind_mph'])}\n
Wind direction: {str(weather_json['current']['wind_dir'])}

************************************
'''
    else:
        for i in range(0, range_):
            City = weather_json['location']['name']
            Region = weather_json['location']['region']
            init = weather_json['forecast']['forecastday'][i]
            String +=  f'''

Date: {str(init['date'])}\n
City: {str(City)}\n
Region: {str(Region)}\n
Av Temp (C): {str(init['day']['avgtemp_c'])}\n
State: {str(init['day']['condition']['text'])}\n
Wind Max (MPH): {str(init['day']['maxwind_mph'])}\n
************************************
'''
    return  String    

# save cred as secure string
def _creds(action, file_name = None):
    if action == 'Encrypt':
        key = Fernet.generate_key()
        def _encrypt(string_, key):
            fernet = Fernet(key)
            return fernet.encrypt(string_.encode('utf-8')), key

        Bot_api_key = getpass("\nPlease enter your BOT API key: ")
        External_api_key = getpass("\nPlease enter your KEY FROM API: ")
        Api_link = getpass("\nPlease enter your EXTERNAL API LINK: ")

        Work_email = getpass("\nPlease enter your NOTIFY EMAIL ADDRESS: ")
        Work_email_pass = getpass("\nPlease enter your PASSWORD FROM NOTIFY EMAIL ADDRESS: ")
        Work_email_smtp = getpass("\nPlease enter your SMTP SERVER NAME: ")

        Enc_Bot_api_key = _encrypt(Bot_api_key, key)
        Enc_External_api_key = _encrypt(External_api_key, key)
        Enc_Api_link = _encrypt(Api_link, key)

        Enc_Work_email = _encrypt(Work_email, key)
        Enc_Work_email_pass = _encrypt(Work_email_pass, key)
        Enc_Work_email_smtp = _encrypt(Work_email_smtp, key)
    
        API_query_params = {
            "Api_link": f'{Enc_Api_link[0].decode()}',
            "Ext_Key": f'{Enc_External_api_key[0].decode()}',
            "Bot_Api_key": f'{Enc_Bot_api_key[0].decode()}',
            "Enc_Work_email": f'{Enc_Work_email[0].decode()}',
            "Enc_Work_email_pass": f'{Enc_Work_email_pass[0].decode()}',
            "Enc_Work_email_smtp": f'{Enc_Work_email_smtp[0].decode()}',
            "Enc_key": f'{Enc_Bot_api_key[1].decode()}'
        }
        temp_ = []
        temp_.append(API_query_params)
        json_obj = json.dumps(temp_, indent = 4) 
        with open ('_credential.json', 'w') as cred_file:
            cred_file.write(json_obj)  
        return "_credentil.json file has been created"

    elif action == 'Dencrypt':
        def _dencrypt(string_, key):
            fernet = Fernet(key)
            return fernet.decrypt(string_)
        with open(file_name, 'rb') as cred_file:
            cred_info = json.load(cred_file)
        Enc_key = cred_info[0]['Enc_key'].encode()

        Ext_Key = _dencrypt(cred_info[0]['Ext_Key'].encode(), Enc_key)
        Api_link = _dencrypt(cred_info[0]['Api_link'].encode(), Enc_key)
        Bot_Api_key = _dencrypt(cred_info[0]['Bot_Api_key'].encode(), Enc_key)

        Enc_Work_email = _dencrypt(cred_info[0]['Enc_Work_email'].encode(), Enc_key)
        Enc_Work_email_pass = _dencrypt(cred_info[0]['Enc_Work_email_pass'].encode(), Enc_key)
        Enc_Work_email_smtp = _dencrypt(cred_info[0]['Enc_Work_email_smtp'].encode(), Enc_key)

        return {'Ext_Key': Ext_Key.decode(), "Api_link": Api_link.decode(), "Bot_Api_key": Bot_Api_key.decode(), 'Enc_Work_email': Enc_Work_email.decode(), 'Enc_Work_email_pass': Enc_Work_email_pass.decode(), 'Enc_Work_email_smtp': Enc_Work_email_smtp.decode()}   

# connect to API and collect data
def _collect_weather_info(params):
    try:
        City = params['City'] 
        Key = params['Key'] 
        Accesstype = params['Accesstype']
        Link = params['Api_link']
        Api_method = params['Api_method']
        Forecast = params['Forecast']
        if Accesstype == 'Api_key':
            if params['Api_method'] == 'current.json':
                API_Link = f'{Link}{Api_method}?key={Key}&q={City}'               
            elif params['Api_method'] == 'forecast.json':
                API_Link = f'{Link}{Api_method}?key={Key}&q={City}&days={Forecast}'
        return (requests.get(API_Link)) 
    except:
        return "API error"     

# create json reg file
def _create_reg_file():
    if file_exists('_registration_logs.json') == False:
        init_data = [{'id': "dummy", 'username': 'dummy', 'mail': 'dummy', 'code': 'dummy', 'registred': 'dummy', 'freq': 'dummy', 'forecast': 'dummy', 'city': 'dummy'}]
        json_obj = json.dumps(init_data, indent = 4)  
        with open('_registration_logs.json', 'w') as fp: 
            fp.write(json_obj)   

# generate and log code for registration
def _generateCodeAndlog(email):
    random_number = random.randrange(1000, 100000)
    init_data = {'id': email.chat.id, 'username': email.chat.username, 'mail': email.text, 'code': random_number, 'registred': 'false', 'city': 'n/a'}
    if os.stat('_registration_logs.json').st_size == 0:
        json_obj = json.dumps(init_data, indent = 4)  
        with open('_registration_logs.json', 'w') as fp: 
            fp.write(json_obj)   
    else:    
        with open('_registration_logs.json') as fp:
            listObj = json.load(fp)
            listObj.append(init_data)
            with open('_registration_logs.json', 'w') as json_file:
                json.dump(listObj, json_file, indent=4, separators=(',',': '))
    return random_number

# send mail for registration
def _sendmail(email, code = None, notify = None):
    email_creds = _creds('Dencrypt', '_credential.json')
    sender_address = email_creds['Enc_Work_email'].replace("'", "")
    sender_pass = email_creds['Enc_Work_email_pass'].replace("'", "")
    smtp = email_creds['Enc_Work_email_smtp'].replace("'", "")
    if code:
        mail_content = f"Dear, \n\nPlease use this code {code} for confirmation of registration"
        receiver_address = email.text
        message = MIMEMultipart()
        message['From'] = sender_address
        message['To'] = receiver_address
        message['Subject'] = 'Registration mail for Weather Forecast telegram bot'

        message.attach(MIMEText(mail_content, 'plain'))
        payload = MIMEBase('application', 'octate-stream')
        payload.add_header('Content-Disposition', 'attachment')
        session = smtplib.SMTP(smtp, 587)
        session.starttls()
        session.login(sender_address, sender_pass)
        text = message.as_string()
        session.sendmail(sender_address, receiver_address, text)
        session.quit()
    elif notify: 
        mail_content = "Dear, \n\nPlease check below weather nofitication"
        receiver_address = email
        message = MIMEMultipart()
        message['From'] = sender_address
        message['To'] = receiver_address
        message['Subject'] = 'Registration in Weather Forecast telegram bot has been completed'

        message.attach(MIMEText(mail_content, 'plain'))
        payload = MIMEBase('application', 'octate-stream')
        payload.add_header('Content-Disposition', 'attachment')
        session = smtplib.SMTP(smtp, 587)
        session.starttls()
        session.login(sender_address, sender_pass)
        text = message.as_string()
        session.sendmail(sender_address, receiver_address, text)
        session.quit()      
    else:
        mail_content = "Dear, \n\nYou have been registered successfully"
        receiver_address = email
        message = MIMEMultipart()
        message['From'] = sender_address
        message['To'] = receiver_address
        message['Subject'] = 'Registration in Weather Forecast telegram bot has been completed'

        message.attach(MIMEText(mail_content, 'plain'))
        payload = MIMEBase('application', 'octate-stream')
        payload.add_header('Content-Disposition', 'attachment')
        session = smtplib.SMTP(smtp, 587)
        session.starttls()
        session.login(sender_address, sender_pass)
        text = message.as_string()
        session.sendmail(sender_address, receiver_address, text)
        session.quit()   

# validate address
def _parseaddress(email):
    email = email.text
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if re.fullmatch(regex, email):
        return True
    else:
        return False

# interactive part 
if file_exists('_credential.json') != True:
    print("No _credential.json exists, it should be created\n")
    _creds('Encrypt', '_credential.json')    
    Bot_Api_key = (_creds('Dencrypt', '_credential.json')['Bot_Api_key']).replace("'", "")
else:
    Bot_Api_key = (_creds('Dencrypt', '_credential.json')['Bot_Api_key']).replace("'", "")

ourbot = telebot.TeleBot(f'{Bot_Api_key}') 
_create_reg_file()

# init work with bot
@ourbot.message_handler(commands=['start'])
def start(message):
    ourbot.send_message(message.chat.id, 'Hi there! Welcome to Weather Forecast bot! \nPlease perform initial registration by using command /registration')

@ourbot.message_handler(commands=['help'])
def start(message):
    ourbot.send_message(message.chat.id, '/start - to start work with bot \n/registration - to perform registration \n/validatecode - to confirm code for registration \n/setcity - to determine your city \n/checkweather - to check weather')

# commands
@ourbot.message_handler(content_types=["text"])
def message_handler(message):
    if message.text.strip() == "/registration": 
        with open('_registration_logs.json') as fp:
            listObj = json.load(fp)
            ifregisred = [listObj[i] for i in range(len(listObj)) if listObj[i]['id'] == message.from_user.id]
        if len(ifregisred) == 1:
            if ifregisred[0]['registred'] == 'true':
                ourbot.send_message(message.chat.id, 'You have been already registred and verified, to see list commands /help')      
            else:
                ourbot.send_message(message.chat.id, 'Registration is not completed yet, please pass verification /validatecode')   
        else:    
            email = ourbot.send_message(message.chat.id, 'Please enter your email address') 
            ourbot.register_next_step_handler(email, registration) 
    elif message.text.strip() == "/validatecode":
        with open('_registration_logs.json') as fp:
            listObj = json.load(fp)
            ifregisred = [listObj[i]['mail'] for i in range(len(listObj)) if listObj[i]['id'] == message.from_user.id and listObj[i]['registred'] == 'true']
        if len(ifregisred) == 1:
            ourbot.send_message(message.chat.id, f'Your account has been already verified via email {ifregisred[0]}, to see list commands /help') 
        else:    
            auth = ourbot.send_message(message.chat.id, 'Please enter the provided code')
            ourbot.register_next_step_handler(auth, valid_code) 
    elif message.text.strip() == "/setcity":
        with open('_registration_logs.json') as fp:
            listObj = json.load(fp)
            ifregisred = [listObj[i] for i in range(len(listObj)) if listObj[i]['id'] == message.from_user.id]
        if  len(ifregisred) == 1:
             with open('_registration_logs.json') as fp:
                listObj = json.load(fp)
                ifregisred = [listObj[i] for i in range(len(listObj)) if listObj[i]['id'] == message.from_user.id and listObj[i]['city'] == 'n/a']
                if len(ifregisred) == 1:
                    city = ourbot.send_message(message.chat.id, 'Please enter your city') 
                    ourbot.register_next_step_handler(city, setcity) 
                else:
                    city = ourbot.send_message(message.chat.id, 'You have already provided city name, do you want to update it? (Yes/No)')  
                    city = ourbot.register_next_step_handler(city, setcity)                           
        else:
            if ifregisred[0]['code'] == 'n/a' and ifregisred[0]['registred'] == 'false':
                ourbot.send_message(message.chat.id, 'Registration is not completed yet, please pass /registration') 
            elif ifregisred[0]['code'] != 'n/a' and ifregisred[0]['registred'] == 'false':
                ourbot.send_message(message.chat.id, 'Registration is not completed yet, please pass /validatecode')                
    elif message.text.strip() == "/checkweather":
        with open('_registration_logs.json') as fp:
            listObj = json.load(fp)
            ifregisred = [listObj[i] for i in range(len(listObj)) if listObj[i]['id'] == message.from_user.id]
            if len(ifregisred) == 1:
                if  ifregisred[0]['code'] != 'n/a' and ifregisred[0]['registred'] == 'true' and ifregisred[0]['city'] != 'n/a':
                    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
                    ForRightNow = telebot.types.KeyboardButton("For Right Now")
                    ForTwoDays = telebot.types.KeyboardButton("For Two Days")
                    ForWeek = telebot.types.KeyboardButton("For Thee Days")
                    markup.add(ForRightNow)
                    markup.add(ForTwoDays)
                    markup.add(ForWeek)  
                    period = ourbot.send_message(message.chat.id, 'Select period for forecast:',  reply_markup=markup)  
                    ourbot.register_next_step_handler(period, checkweather)      
                else:
                    if ifregisred[0]['city'] != 'n/a':
                        if ifregisred[0]['code'] == 'n/a' and ifregisred[0]['registred'] == 'false':
                            ourbot.send_message(message.chat.id, 'Registration is not completed yet, please pass /registration') 
                        elif ifregisred[0]['code'] != 'n/a' and ifregisred[0]['registred'] == 'false':
                            ourbot.send_message(message.chat.id, 'Verification is not completed yet, please pass /validatecode')  
                    elif ifregisred[0]['city'] == 'n/a':
                        ourbot.send_message(message.chat.id, 'City name is not determined yet, please pass /setcity')    
            else:
                ourbot.send_message(message.chat.id, 'Registration is not completed yet, please pass /registration')             
    else:
        ourbot.send_message(message.chat.id, 'Incorrect request, to see list commands /help')  
# registration
def registration(email):   
    checkformat = _parseaddress(email)
    if checkformat:
        code = _generateCodeAndlog(email)
        _sendmail(email, code)
        ourbot.send_message(email.chat.id, 'Mail with confirmation code has been sent to the entered email, please use /validatecode to complete registration')
    else:
        ourbot.send_message(email.chat.id, 'Provided email has incorrect format, plenase enter correct one /registration')    

# validation  
def valid_code(auth):
    with open('_registration_logs.json') as fp:
        listObj = json.load(fp)
        ifregisred = None
        for i in range(len(listObj)):
            if str(listObj[i]['code']) == str(auth.text) and listObj[i]['id'] == auth.chat.id:
                ifregisred = listObj[i] 
    if ifregisred:
        ourbot.send_message(auth.chat.id, 'You have successfully registred, to use bot you need to provide us city name, please pass /setcity')
        ifregisred.update({'registred': 'true'})
        with open('_registration_logs.json', 'w') as amend_file:
            json.dump(listObj, amend_file, indent=4, separators=(',',': ')) 
        _sendmail(ifregisred['mail'])
    else:
        ourbot.send_message(auth.chat.id, 'Entered code is not valid, please enter correct one /validatecode or re check email /registration') 

# setcity
def setcity(city):
    if city.text.lower() == 'yes':
        second = ourbot.send_message(city.chat.id, 'Please enter city name')
        second = ourbot.register_next_step_handler(second, save_json)  
    elif city.text.lower() == 'no':
        ourbot.send_message(city.chat.id, 'To see list commands /help')    
    else:
        with open('_registration_logs.json') as fp:
            listObj = json.load(fp)
            ifregisred = [listObj[i] for i in range(len(listObj)) if listObj[i]['id'] == city.from_user.id]
            ifregisred[0]['city'] = city.text
            with open('_registration_logs.json', 'w') as amend_file:
                json.dump(listObj, amend_file, indent=4, separators=(',',': ')) 
                ourbot.send_message(city.chat.id, 'City has been configured, please select /checkweather to check weather')     

# save city to json
def save_json(second):
        if second.text.lower().isalpha():
            with open('_registration_logs.json') as fp:
                listObj = json.load(fp)
                ifregisred = [listObj[i] for i in range(len(listObj)) if listObj[i]['id'] == second.from_user.id]
                ifregisred[0]['city'] = second.text
                with open('_registration_logs.json', 'w') as amend_file:
                    json.dump(listObj, amend_file, indent=4, separators=(',',': ')) 
                ourbot.send_message(second.chat.id, 'City has been configured, please select /checkweather to check weather')
        else:
            ourbot.send_message(second.chat.id, 'City name is incorrect, please enter correct one /setcity')  

# checkweather    
def checkweather(period):
    Api_info = _creds('Dencrypt', '_credential.json')
    range_ = period.text
    with open('_registration_logs.json') as fp:
        listObj = json.load(fp)
        ifregisred = [listObj[i] for i in range(len(listObj)) if listObj[i]['id'] == period.from_user.id]
        RequestedCity = ifregisred[0]['city']

    API_query_params = {
        'Forecast': 'none',
        'City': RequestedCity,
        'Key': Api_info['Ext_Key'],
        'Api_method': 'none',
        'Accesstype': 'Api_key',
        'Api_link': Api_info['Api_link']
    }

    if range_ == "For Right Now":
        API_query_params.update({'Api_method': 'current.json'})
        weather_json = _collect_weather_info(API_query_params) 
        if weather_json == 'API error':
                 ourbot.send_message(period.chat.id, 'Something with API link, please wati till its fixed')  
        else:
            if weather_json.reason != 'OK':
                with open('_registration_logs.json') as fp:
                    listObj = json.load(fp)
                    ifregisred = [listObj[i] for i in range(len(listObj)) if listObj[i]['id'] == period.from_user.id]
                    username = ifregisred[0]['username']
                    mail = ifregisred[0]['mail']
                    city = ifregisred[0]['city']
                    ourbot.send_message(period.chat.id, f'Please check your settings, city name is not vaild pass /setcity \n\nUser name: {username} \nEmail: {mail} \nCity: {city}')
            else:
                weather_json = weather_json.json()  
                ourbot.send_message(period.chat.id, f'Please see below \n\n{convert_json(weather_json)} \n\n To check for another period pass /checkweather')
                #json_obj = json.dumps(weather_json, indent = 4) 
                #with open('_weather_data.json', 'w') as weather_info:
                    #weather_info.write(json_obj)      
    elif range_ == "For Two Days":
        API_query_params.update({'Api_method': 'forecast.json'})
        API_query_params.update({'Forecast': '3'})
        weather_json = _collect_weather_info(API_query_params)
        if weather_json == 'API error':
                ourbot.send_message(period.chat.id, 'Something with API link, please wati till its fixed, to see list commands /help')  
        else:
            if weather_json.reason != 'OK':
                with open('_registration_logs.json') as fp:
                    listObj = json.load(fp)
                    ifregisred = [listObj[i] for i in range(len(listObj)) if listObj[i]['id'] == period.from_user.id]
                    username = ifregisred[0]['username']
                    mail = ifregisred[0]['mail']
                    city = ifregisred[0]['city']
                    ourbot.send_message(period.chat.id, f'Please check your settings, city name is not vaild pass /setcity \n\nUser name: {username} \nEmail: {mail} \nCity: {city}')
            else:
                weather_json = weather_json.json()  
                ourbot.send_message(period.chat.id, f'Please see below \n\n{convert_json(weather_json, 2)} \n\n To check for another period pass /checkweather')
                #json_obj = json.dumps(weather_json, indent = 4)  
                #with open('_weather_data.json', 'w') as weather_info:
                    #weather_info.write(json_obj)    
    elif range_ == "For Thee Days":
        API_query_params.update({'Api_method': 'forecast.json'})
        API_query_params.update({'Forecast': '4'})
        weather_json = _collect_weather_info(API_query_params)
        if weather_json == 'API error':
            ourbot.send_message(period.chat.id, 'Something with API link, please wati till its fixed')  
        else:
            if weather_json.reason != 'OK':
                with open('_registration_logs.json') as fp:
                    listObj = json.load(fp)
                    ifregisred = [listObj[i] for i in range(len(listObj)) if listObj[i]['id'] == period.from_user.id]
                    username = ifregisred[0]['username']
                    mail = ifregisred[0]['mail']
                    city = ifregisred[0]['city']
                    ourbot.send_message(period.chat.id, f'Please check your settings, city name is not vaild pass /setcity \n\nUser name: {username} \nEmail: {mail} \nCity: {city}')
            else:
                weather_json = weather_json.json()  
                ourbot.send_message(period.chat.id, f'Please see below \n\n{convert_json(weather_json, 3)} \n\n To check for another period pass /checkweather')
                #json_obj = json.dumps(weather_json, indent = 4)  
                #with open('_weather_data.json', 'w') as weather_info:
                    #weather_info.write(json_obj)    

ourbot.polling(none_stop=True)

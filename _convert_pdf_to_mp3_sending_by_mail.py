""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    .Synopsis
    
    Author: 
        KeepCalmWherever
        
    Purposes: 
        learning python :)
        
    Functions:
        def sending_file(FileMP3Name):
            Params:
                PDF file path, var name - FilePath
                Language, var name - Language
                Name for MP3 file, var name - FileMP3Name
                    
        def ConvertPDFtoMP3(Filepath, language, FileMP3Name)
            Params:
                Sender address, var name - sender_address
                Sender password, var name - sender_pass
                Received address, var name - receiver_address
                SMTP server name, var name smtp
                
    Comment:         
        For public SMTP servers (example mail or gmail) it should be configured external application access in account settings
                
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# import part
from os.path import exists as file_exists
from gtts import gTTS
import pdfplumber, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from getpass import getpass

# converting PDF
def ConvertPDFtoMP3(Filepath, language, FileMP3Name):
    # reading part
    print("Processing PDF file")
    InitialData = pdfplumber.open(FilePath)
    Pages = InitialData.pages
    InitText = [Pages[i].extract_text()for i in range(len(Pages))]
    Text = (''.join(InitText)).replace('\n', '')
    print("Text is ready for saving to MP3, doing... please do not close window")
    # saving part
    ToSaveMP3 = (gTTS(Text, lang=Language, slow=False, lang_check=True) )
    ToSaveMP3.save(f'{FileMP3Name}.mp3')
    print("MP3 file has been saved")
    
# send doc to mail
def sending_file(FileMP3Name):
    mail_content = f'Please find in attached file MP3 version of {FileMP3Name}'
    #The mail addresses and password
    sender_address = input("\nPlease enter your email address: ")
    sender_pass = getpass("\nPlease enter your password: ")
    receiver_address = input("\nPlease enter receiver address: ")
    smtp = input("\nPlease enter smtp server name: ")
    #Setup the MIME
    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = receiver_address
    message['Subject'] = f'Converted MP3 file {FileMP3Name}'
    #The subject line
    #The body and the attachments for the mail
    message.attach(MIMEText(mail_content, 'plain'))
    attach_file = open(FileMP3Name, 'rb') # Open the file as binary mode
    payload = MIMEBase('application', 'octate-stream')
    payload.set_payload(attach_file.read())
    encoders.encode_base64(payload) #encode the attachment
    #add payload header with filename
    payload.add_header('Content-Disposition', 'attachment', filename=FileMP3Name)
    message.attach(payload)
    #Create SMTP session for sending the mail
    session = smtplib.SMTP(smtp, 587) #use gmail with port
    session.starttls() #enable security
    session.login(sender_address, sender_pass) #login with mail_id and password
    text = message.as_string()
    session.sendmail(sender_address, receiver_address, text)
    session.quit()
    print('File has been shared with', receiver_address)

# intractive part
FilePath = input(("\nPlease enter PDF file path: ")).replace('"', '')
Language = input("\nPlease enter language (en/ru/fr etc): ")
FileMP3Name = input(("\nPlease enter name for MP3 file: ")).replace('.mp3', '')
while file_exists(FilePath) != True:
    print("Provided path does not exist locally, please enter correct one")    
    FilePath = input().replace('"', '') 

ConvertPDFtoMP3(FilePath, Language, FileMP3Name)
isSend = input("\nDo you want to share generated MP3 file by mail? (Yes/No)")
if isSend == "Yes":
    sending_file(FileMP3Name)

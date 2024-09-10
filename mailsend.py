import smtplib
import imghdr

from email.message import EmailMessage

Sender_Email = "trafficviolation3@gmail.com"
Password = "zatkalvbqfqgeduw"


def sendmail(image=None, subject="Subject", message="Message", to = "techvkj@gmail.com"):
    try:
        print("Sending Mail...", end = "")
        newMessage = EmailMessage()                         
        newMessage['Subject'] = subject
        newMessage['From'] = Sender_Email                   
        newMessage['To'] = to                   
        newMessage.set_content(message) 

        if image is not None:
            with open(image, 'rb') as f:
                image_data = f.read()
                image_type = imghdr.what(f.name)
                image_name = f.name

            newMessage.add_attachment(image_data, maintype='image', subtype=image_type, filename=image_name)

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(Sender_Email, Password)              
            smtp.send_message(newMessage)
        
        print(" Done...")
    except:
        print("Failed")

if __name__ == "__main__":
    sendmail()
        
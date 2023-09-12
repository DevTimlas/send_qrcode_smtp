from fastapi import FastAPI
from pydantic import BaseModel
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import smtplib
import qrcode
import io

app = FastAPI()

# Google SMTP server configuration
smtp_server = "smtp.gmail.com"
smtp_port = 465
sender_email = "timcodedata@gmail.com"
sender_pass = "wgkvwbqdpmibjykf"
subject = "Hi, your user details is ready" # request.subject
message = "Download and scan the QR Code to get your Details" # request.message
# receiver_email = "timilehinoladejo18@gmail.com"


class EmailRequest(BaseModel):
    username: str
    password: str
    receiver_email: str


@app.post("/send_email")
async def send_email_with_qr_code(request: EmailRequest):
    username = request.username
    password = request.password
    receiver_email = request.receiver_email

    # Create a QR code image in memory
    qr_data = f"Username: {username}\nPassword: {password}"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # Create an email with the QR code image as an attachment
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject

    # Attach the message text
    msg.attach(MIMEText(message, "plain"))

    # Attach the QR code image
    image_buffer = io.BytesIO()
    img.save(image_buffer, format="PNG")
    image_buffer.seek(0)
    attachment = MIMEImage(image_buffer.read(), name="qr_code.png")
    msg.attach(attachment)

    # Send the email
    with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
        server.login(sender_email, sender_pass)
        server.sendmail(sender_email, receiver_email, msg.as_string())

    return {"message": "Email sent with QR code attachment"}


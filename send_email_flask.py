from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import qrcode
import io
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

app = Flask(__name__)
CORS(app)

# Google SMTP server configuration
smtp_server = "smtp.gmail.com"
smtp_port = 465
sender_email = "timcodedata@gmail.com"
sender_pass = "wgkvwbqdpmibjykf"
subject = "Hi, your user details are ready"  # request.subject
message = "Download and scan the QR Code to get your Details"  # request.message
# receiver_email = "timilehinoladejo18@gmail.com"


class EmailRequest:
    def __init__(self, firstName, lastName, username, email, image):
        self.firstName = firstName
        self.lastName = lastName
        self.username = username
        self.email = email
        self.image = image


@app.route("/send_email", methods=["POST"])
def send_email_with_qr_code():
    if request.headers.get("Content-Type") == "application/json":
        # Handle JSON request
        data = request.get_json()
        username = data["username"]
        lastName = data["lastName"]
        firstName = data["firstName"]
        email = data["email"]
        image_path = data.get("image")  # Get the image path from JSON if available
    else:
        # Handle form-data request
        username = request.form["username"]
        lastName = request.form["lastName"]
        firstName = request.form["firstName"]
        email = request.form["email"]
        image = request.files["image"]
        image_path = None

    if image_path:
        # Process the image file if provided as a path
        img_bg = Image.open(image_path)
    else:
        # Process the image file from file upload
        img_bg = Image.open(image)

    qr_data = f"Username: {username}\nFirstname: {firstName}\nLastname: {lastName}"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=3,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    pos = (img_bg.size[0] - img.size[0], img_bg.size[1] - img.size[1])

    img_bg.paste(img, pos)

    msg = MIMEMultipart()
    msg["From"] = email
    msg["To"] = email
    msg["Subject"] = subject

    msg.attach(MIMEText(message, "plain"))

    image_buffer = io.BytesIO()
    img_bg.save(image_buffer, format="PNG")
    image_buffer.seek(0)
    attachment = MIMEImage(image_buffer.read(), name="qr_code.png")
    msg.attach(attachment)

    with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
        server.login(sender_email, sender_pass)
        server.sendmail(sender_email, email, msg.as_string())

    return jsonify({"message": "Email sent with QR code attachment"})


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=80)


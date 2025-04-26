import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import time

# Configuration
PRODUCT_URL = "https://shop.amul.com/product/amul-whey-protein-chocolate-34g-pack-of-60-sachets"  # Replace with the actual product URL
CHECK_INTERVAL = 3600  # Check every hour (in seconds)
EMAIL_SENDER = "your_email@gmail.com"  # Your email
EMAIL_PASSWORD = "your_app_password"  # App-specific password
EMAIL_RECEIVER = "receiver_email@gmail.com"  # Your email or another recipient
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

def send_email(subject, body):
    """Send an email notification."""
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

def check_stock():
    """Check if the product is in stock."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(PRODUCT_URL, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Check for "Add to Cart" button (indicates in stock)
        add_to_cart = soup.find("button", {"class": "add-to-cart"})  # Adjust class based on actual website
        if add_to_cart and "disabled" not in add_to_cart.get("class", []):
            return True, "Amul Chocolate Whey Protein is in stock!"
        return False, "Still out of stock."
    except Exception as e:
        return False, f"Error checking stock: {e}"

def main():
    print("Starting stock monitoring...")
    while True:
        in_stock, message = check_stock()
        print(message)
        if in_stock:
            send_email("Amul Whey Protein In Stock!", f"The product is back in stock! Check it out: {PRODUCT_URL}")
            break
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()

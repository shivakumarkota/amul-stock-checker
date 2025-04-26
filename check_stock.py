import requests
import smtplib
from email.mime.text import MIMEText
import time
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# Configuration
API_URL = "https://shop.amul.com/api/1/entity/ms.products?q=%7B%22alias%22:%22amul-chocolate-whey-protein-34-g-or-pack-of-60-sachets%22%7D&limit=1"
PRODUCT_URL = "https://shop.amul.com/en/product/amul-chocolate-whey-protein-34-g-or-pack-of-60-sachets"
CHECK_INTERVAL = 300  # Check every 5 minutes (in seconds)
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
MAX_RUNTIME = 5 * 3600  # 5 hours (GitHub Actions job limit is 6 hours)

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
        logging.info("Email sent successfully!")
        return True
    except Exception as e:
        logging.error(f"Failed to send email: {e}")
        return False

def check_stock():
    """Check if the product is in stock via API."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://shop.amul.com/",
    }
    try:
        response = requests.get(API_URL, headers=headers)
        response.raise_for_status()
        data = response.json()

        # Check inventory quantity in the first product
        if data.get("data") and len(data["data"]) > 0:
            inventory_quantity = data["data"][0].get("inventory_quantity", 0)
            if inventory_quantity > 0:
                return True, f"Amul Chocolate Whey Protein is in stock! Quantity: {inventory_quantity}"
            return False, "Still out of stock."
        return False, "No product data found in API response."
    except Exception as e:
        return False, f"Error checking stock: {e}"

def main():
    start_time = time.time()
    logging.info("Starting stock monitoring for Amul Chocolate Whey Protein...")
    
    while time.time() - start_time < MAX_RUNTIME:
        in_stock, message = check_stock()
        logging.info(message)
        if in_stock:
            success = send_email("Amul Whey Protein In Stock!", f"{message}\nCheck it out: {PRODUCT_URL}")
            if success:
                logging.info("Stock found and email sent. Stopping script.")
                break
        time.sleep(CHECK_INTERVAL)
    
    logging.info("Max runtime reached. Exiting.")

if __name__ == "__main__":
    main()

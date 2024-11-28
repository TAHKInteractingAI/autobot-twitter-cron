from __future__ import print_function
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
import os
import time
import pandas as pd
from googleapiclient.discovery import build 
from google.oauth2 import service_account
from dotenv import load_dotenv
load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
credentials = service_account.Credentials.from_service_account_info({
  "type": os.getenv('TYPE'),
  "project_id": os.getenv('PROJECT_ID'),
  "private_key_id": os.getenv('PRIVATE_KEY_ID'),
  "private_key": os.getenv('PRIVATE_KEY').replace("\\n", "\n"),
  "client_email": os.getenv('CLIENT_EMAIL'),
  "client_id": os.getenv('CLIENT_ID'),
  "auth_uri": os.getenv('AUTH_URI'),
  "token_uri": os.getenv('TOKEN_URI'),
  "auth_provider_x509_cert_url": os.getenv('AUTH_PROVIDER_CERT_URL'),
  "client_x509_cert_url": os.getenv('CLIENT_CERT_URL'),
  "universe_domain": os.getenv('UNIVERSE_DOMAIN')
})
spreadsheet_service = build('sheets', 'v4', credentials=credentials)

SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
RANGE_NAME = 'input_tweet!A:F'
sheet = spreadsheet_service.spreadsheets()
result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
values = result.get('values', [])
max_cols = max(len(row) for row in values)
values = [row + [''] * (max_cols - len(row)) for row in values]
df = pd.DataFrame(values[1:], columns=values[0])
df = df.fillna('')
# df.head()
print('CONNECTED TO GOOGLE SHEET')

"""# **LOGIN TWEET**"""
# Đường dẫn cần tạo thư mục
folder_path = 'Data_Twitter'

# Tạo thư mục nếu chưa tồn tại
if not os.path.exists(folder_path):
    os.makedirs(folder_path)

# Cài đặt các tùy chọn cho Chrome
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument('--headless')  # Chế độ headless
options.add_argument('--disable-gpu')  # Tắt GPU
options.add_argument('--no-sandbox')  # Không sử dụng sandbox
# options.add_argument('--diable-dev-shm-uage')
# Khởi động Chrome với các tùy chọn
# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

browser = webdriver.Chrome(options=options)
browser.implicitly_wait(12)
# Truy cập trang web
browser.get('https://x.com/i/flow/login')
time.sleep(7)

try:
    # Locate the email input field and enter the email
    input_email = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="text"]'))
    )
    input_email.send_keys("henry_universes")
except Exception as e:
    print(f"An error occurred: {e}")

try:
    button_next = browser.find_element(By.XPATH, "//button[.//span[text()='Next']]")
    button_next.click()
    time.sleep(5)
except Exception as e:
    print(f"An error occurred: {e}")

"""Nếu xuất hiện form yêu cầu nhập email thì chạy 2 cell code bên dưới. Còn không bỏ qua"""
try:
    input_phone_or_email = browser.find_element(By.XPATH, '//input[@data-testid="ocfEnterTextTextInput"]')
    input_phone_or_email.send_keys('henry.universes@tahkfoundation.org')
    time.sleep(1)
except Exception as e:
    print(f"An error occurred: {e}")

try:
    button_next = browser.find_element(By.XPATH, "//button[.//span[text()='Next']]")
    button_next.click()
    time.sleep(5)
except Exception as e:
    print(f"An error occurred: {e}")

try:
    input_phone_or_email = browser.find_element(By.XPATH, '//input[@data-testid="ocfEnterTextTextInput"]')
    input_phone_or_email.send_keys('henry.phd@ah-globalgroup.com')
    time.sleep(1)
except Exception as e:
    print(f"An error occurred: {e}")

try:
    button_next = browser.find_element(By.XPATH, "//button[.//span[text()='Next']]")
    button_next.click()
    time.sleep(5)
except Exception as e:
    print(f"An error occurred: {e}")

try:
    input_password = browser.find_element(By.XPATH, '//input[@autocomplete="current-password"]')
    input_password.send_keys("Henry@2023CA")
except Exception as e:
    print(f"An error occurred: {e}")
  
try:
    button_login = browser.find_element(By.XPATH, '//button[contains(.//span/text(), "Log in")]')
    button_login.click()
    time.sleep(10)
except Exception as e:
    print(f"An error occurred: {e}")

"""*Nếu được yêu cầu nhập mã code thì kiểm tra email lấy code và chạy cell dưới, ko thì bỏ qua 2 bước*"""
# input_element = browser.find_element(By.XPATH, '//input[@data-testid="ocfEnterTextTextInput"]')
# input_element.send_keys('iq2mx2mh')
# browser.save_screenshot(screenshot_path)
# display(Image(filename=screenshot_path))

# button_next_confirm = browser.find_element(By.XPATH, "//button[.//span[text()='Next']]")
# button_next_confirm.click()
# time.sleep(3)
# browser.save_screenshot(screenshot_path)
# display(Image(filename=screenshot_path))

"""# **BOT TWEET**"""
# Function to process each row and post a tweet
def post_tweet_from_row(row, index):
    try:
        tweet_text = row.get('Tweet content', '')  # Full tweet content
        tweet_image = os.path.abspath('.' + row.get('IMAGE', ''))  # This will be the image path
        tags = row.get('TAG', '')  # mentions (tagging other users)
        hashtags = row.get('HASHTAG', '')  # hashtags
        subtags = row.get('SUBTAG', '')  # subtags (additional context)

        # Ensure proper formatting for tags and hashtags
        formatted_tags = ' '.join([f"@{tag.strip()}" for tag in tags.split(',') if tag.strip()])
        formatted_hashtags = ' '.join([f"#{hashtag.strip()}" for hashtag in hashtags.split(',') if hashtag.strip()])
        formatted_subtags = ' '.join([f"#{subtag.strip()}" for subtag in subtags.split(',') if subtag.strip()])

        # Combine the tweet content with tags, hashtags, and subtags
        combined_text = f"{formatted_hashtags}\n{tweet_text}\n{formatted_tags}\n{formatted_subtags}"

        # Locate the tweet input field and input the combined tweet content
        try:
            tweet_input = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.public-DraftStyleDefault-block.public-DraftStyleDefault-ltr'))
            )
            ActionChains(browser).move_to_element(tweet_input).click().perform() # Click to focus on the input field
            print("checked")
            tweet_input.send_keys(combined_text)
            tweet_input.send_keys(Keys.ESCAPE)
            print(f"Tweet content input successfully for tweet {index + 1}.")
        except Exception as e:
            print(f"An error occurred while inputting tweet {index + 1}: {e}")
            df.at[index, 'Status'] = 'Failed'
            return  # Skip to the next tweet if there's an error

        # Upload the image if it exists and is a valid file path
        if tweet_image and os.path.exists(tweet_image):
            try:
                # Find the image upload button
                upload_button = WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
                )
                upload_button.send_keys(tweet_image)
                time.sleep(5)  # Send the image path to the file input
                print(f"Image {tweet_image} uploaded successfully for tweet {index + 1}.")
                time.sleep(3)  # Wait for the image to upload
            except Exception as e:
                print(f"An error occurred while uploading the image for tweet {index + 1}: {e}")
                df.at[index, 'Status'] = 'Failed'
                return  # Skip to the next tweet if there's an error

        # Post the tweet by clicking the "Post all" button
        try:
            post_all_button = WebDriverWait(browser, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='tweetButtonInline' and @role='button']"))
            )
            browser.execute_script("arguments[0].scrollIntoView(true);", post_all_button)
            post_all_button.click()
            print("clicked success")
            print(f"Post all button clicked for tweet {index + 1}.")
        except Exception as e:
            print(f"An error occurred while clicking the Post all button for tweet {index + 1}: {e}")
            df.at[index, 'Status'] = 'Failed'
            return  # Skip to the next tweet if there's an error

        time.sleep(5)

        # Confirm the tweet was posted by checking for a specific element that appears after posting
        try:
            # Match with the first part of the combined_text to confirm post
            confirmation_element = WebDriverWait(browser, 20).until(
                EC.presence_of_element_located((By.XPATH, f"//span[contains(text(), '{tweet_text[:30]}')]"))
            )
            print(f"Tweet {index + 1} posted successfully.")
            # Update status in the DataFrame
            df.at[index, 'Status'] = 'Success'
        except Exception as e:
            print(f"Unable to confirm if Tweet {index + 1} was posted: {e}")
            df.at[index, 'Status'] = 'Failed'

    except Exception as e:
        print(f"An error occurred while processing tweet {index + 1}: {e}")
        df.at[index, 'Status'] = 'Failed'

# Iterate through each row and post tweets (starting from tweet 1 onwards)
for index, row in df.loc[df['Status'] == ''].iterrows():
    post_tweet_from_row(row, index)

# Update Google Sheets with the new status
def update_google_sheet_status(df, spreadsheet_id, range_name):
    """Updates the Google Sheet with the status of each tweet."""
    # Prepare data to update
    values = [df.columns.values.tolist()] + df.values.tolist()

    # Prepare the body for the update request
    body = {
        'values': values
    }

    # Update the Google Sheet with new statuses
    result = spreadsheet_service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id, range=range_name,
        valueInputOption="RAW", body=body).execute()

    print(f"{result.get('updatedCells')} cells updated.")

# Call the function to update the sheet
update_google_sheet_status(df, SPREADSHEET_ID, RANGE_NAME)

# Close the browser
browser.quit()

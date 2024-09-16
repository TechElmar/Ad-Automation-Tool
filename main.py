import schedule
import time
from new_kijiji import *
from functools import partial
from scheduler import *

# Create ads here:
ad_1 = partial(create_kijiji_ad,
               category_id='CATEGORY_ID_1', # Change this to the category ID found in the URL: # https://www.kijiji.ca/p-admarkt-post-ad.html?categoryId={category_id}&siteLocale=en_CA
               email='YOUR_EMAIL_1',  # Change to the email associated with the Kijiji account
               password='YOUR_PASSWORD_1',  # Change to the password associated with the Kijiji account
               self_offer=True,
               offer_cashless_payment=True,
               cash_accepted=True,
               title='TITLE_PLACEHOLDER_1',  # Replace with the title of the ad
               description='DESCRIPTION_PLACEHOLDER_1',  # Replace with the description of the ad
               tags='TAG1,TAG2,TAG3,',  # Replace with tags relevant to the ad
               address='ADDRESS_PLACEHOLDER_1',  # Replace with the address where the service is offered
               images=['IMAGE_PATH_PLACEHOLDER_1'],  # Replace with the path to the image(s)
               youtube_url=None,  # Replace with YouTube URL if applicable, otherwise set to None
               phone_number='PHONE_NUMBER_PLACEHOLDER_1',  # Replace with the phone number
               package_type='PACKAGE_TYPE_PLACEHOLDER_1',  # Replace with the package type (e.g., Basic, Premium)
               area_location='AREA_LOCATION_PLACEHOLDER_1')  # Replace with the area location (e.g., Alberta, Calgary)

ad_2 = partial(create_kijiji_ad,
               category_id='CATEGORY_ID_2',  # Change this to the category ID found in the URL
               email='YOUR_EMAIL_2',  # Change to the email associated with the Kijiji account
               password='YOUR_PASSWORD_2',  # Change to the password associated with the Kijiji account
               self_offer=True,
               offer_cashless_payment=True,
               cash_accepted=True,
               title='TITLE_PLACEHOLDER_2',  # Replace with the title of the ad
               description='DESCRIPTION_PLACEHOLDER_2',  # Replace with the description of the ad
               tags='TAG1,TAG2,TAG3,',  # Replace with tags relevant to the ad
               address='ADDRESS_PLACEHOLDER_2',  # Replace with the address where the service is offered
               images=['IMAGE_PATH_PLACEHOLDER_2'],  # Replace with the path to the image(s)
               youtube_url=None,  # Replace with YouTube URL if applicable, otherwise set to None
               phone_number='PHONE_NUMBER_PLACEHOLDER_2',  # Replace with the phone number
               package_type='PACKAGE_TYPE_PLACEHOLDER_2',  # Replace with the package type (e.g., Basic, Premium)
               area_location='AREA_LOCATION_PLACEHOLDER_2')  # Replace with the area location (e.g., Alberta, Calgary)

# Schedule ads here:
## Uncomment and configure these lines based on your requirements
# set_schedule(ad=ad_1, days="DAY_OF_WEEK", start_times=["START_TIME_1", "START_TIME_2"], delete_times=["DELETE_TIME_1", "DELETE_TIME_2"])
# set_schedule(ad=ad_2, days="DAY_OF_WEEK", start_times=["START_TIME_1", "START_TIME_2"], delete_times=["DELETE_TIME_1", "DELETE_TIME_2"])

# Example schedule for ad_1
set_schedule(ad=ad_1, days="day", start_times=["10:50", "14:55", "21:35", "22:20"],
             delete_times=["12:50", "16:50", "21:45", "23:59"])
# Example schedule for ad_2
set_schedule(ad=ad_2, days="day", start_times=["11:10", "15:55", "21:45", "22:30"],
             delete_times=["13:50", "17:50", "21:55", "23:59"])

# Run scheduled tasks
while True:
    schedule.run_pending()
    check_delete_come()  # Ensure to define this function in the scheduler module
    time.sleep(60)

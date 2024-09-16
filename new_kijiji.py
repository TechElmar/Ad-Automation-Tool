from selenium_module import *
import pickle
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import datetime
import re
import threading
import traceback
import json
import os
from datetime import timedelta

dir_path = os.path.dirname(os.path.realpath(__file__))
sep = os.sep
folder_path = dir_path + sep + 'ads data'
lock = threading.Lock()
second_lock = threading.Lock()
pickle.dump(True, open("single_thread.pkl", "wb"))


def add_delete_schedule(id, seconds_to_add, email, password):
    with lock:
        try:
            with open(dir_path + sep + 'ads_delete_data.json', 'r') as file:
                delete_data = json.load(file)
        except:
            delete_data = []

        # Get the current time
        current_time = datetime.datetime.now()

        # Calculate the future time by adding seconds
        future_time = current_time + timedelta(seconds=seconds_to_add)

        # Append the data to the list
        delete_data.append({'id': id, 'future_time': str(
            future_time), 'email': email, 'password': password})

        # Save the updated JSON data back to the file

        with open(dir_path + sep + 'ads_delete_data.json', 'w') as file:
            json.dump(delete_data, file, indent=4)


def add_redelete_schedule(target_id):
    try:
        with lock:
            with open(dir_path + sep + 'ads_delete_data.json', 'r+') as file:
                data = json.load(file)
                for item in data:
                    if item['id'] == target_id:
                        future_time = datetime.datetime.strptime(
                            item['future_time'], '%Y-%m-%d %H:%M:%S.%f')
                        new_future_time = future_time + timedelta(minutes=15)
                        item['future_time'] = new_future_time.strftime(
                            '%Y-%m-%d %H:%M:%S.%f')

                file.seek(0)  # Move the file pointer to the beginning
                json.dump(data, file, indent=4)
                file.truncate()  # Truncate the file to remove any extra content

        print(f"Updated future_time for ID {target_id} by 15 minutes.")
    except FileNotFoundError:
        print(f"File {dir_path + sep + 'ads_delete_data.json', 'r'} not found.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


def check_delete_come():
    with lock:
        try:
            with open(dir_path + sep + 'ads_delete_data.json', 'r') as file:
                delete_data = json.load(file)
        except FileNotFoundError:
            delete_data = []

    current_time = datetime.datetime.now()
    updated_data = []

    for entry in delete_data:
        future_time_str = entry.get('future_time')

        if future_time_str:
            future_time_entry = datetime.datetime.strptime(
                future_time_str, '%Y-%m-%d %H:%M:%S.%f')

            if current_time > future_time_entry:
                # Delete entries with the same ID
                delete_data = [
                    e for e in delete_data if e.get('id') != entry['id']]

                # Save the updated JSON data back to the file
                with lock:
                    with open(dir_path + sep + 'ads_delete_data.json', 'w') as file:
                        json.dump(delete_data, file, indent=4)

                new_future_time = future_time_entry + \
                                  datetime.timedelta(minutes=15)
                entry['future_time'] = new_future_time.strftime(
                    '%Y-%m-%d %H:%M:%S.%f')
                updated_data.append(entry)
                # Execute your custom function here
                # Create a new thread for running the delete_ads_thread function
                ad_thread = threading.Thread(target=delete_ad_by_id, args=(
                    entry['id'], entry['email'], entry['password']))

                # Start the thread
                ad_thread.start()
    if updated_data:
        print(updated_data)
    with lock:
        # Load data from 'second_delete.json'
        try:
            with open(dir_path + sep + 'second_delete.json', 'r') as second_file:
                second_delete_data = json.load(second_file)
        except FileNotFoundError:
            second_delete_data = []

        # Append data from 'second_delete.json' to updated_data
        updated_data.extend(second_delete_data)

        # Save the updated JSON data back to 'ads_delete_data.json'

        with open(dir_path + sep + 'second_delete_data.json', 'w') as file:
            json.dump(updated_data, file, indent=4)


def isLogin(driver):
    try:
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located(
            (By.XPATH, "//a[text()='Sign In']")))
        return False
    except:
        return True


def login_with_password(driver, email, password):
    try:
        wait = WebDriverWait(driver, 15)
        driver.get(
            'https://www.kijiji.ca/consumer/login?redirectUrl=%2Fp-select-category.html%3F')

        email_input = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'input[type="email"]')))
        email_input.send_keys(email)
        sleep(1)
        password_input = driver.find_element(
            By.CSS_SELECTOR, 'input[type="password"]')
        sleep(4)
        password_input.send_keys(password)
        try:
            keep_signin = driver.find_element(
                By.XPATH, "//label[text()='Keep me signed in']")
            driver.execute_script("arguments[0].click();", keep_signin)
        except:
            print('no save login button')
        sleep(5)
        signin = driver.find_element(By.XPATH, "//button[text()='Sign in']")
        driver.execute_script("arguments[0].click();", signin)
        sleep(180)
        pickle.dump(driver.get_cookies(), open("cookies.pkl", "wb"))
    except Exception as e:
        print(e)
        print('can\'t login with password')


def login_with_cookies(driver):
    try:
        cookies = pickle.load(open("cookies.pkl", "rb"))
        for cookie in cookies:
            driver.add_cookie(cookie)
        sleep(5)
        driver.refresh()
        sleep(2)
    except Exception as e:
        print(e)


def find_ad_id(url):
    # Define a regular expression pattern to match the adId parameter in the URL
    pattern = r'adId=(\d+)'

    # Use re.search to find the first match of the pattern in the URL
    match = re.search(pattern, url)

    # Check if a match was found
    if match:
        # Extract and return the adId value from the match
        ad_id = match.group(1)
        return ad_id
    else:
        # Return None if no adId was found in the URL
        return None


def login(email=None, password=None):
    driver = getDriver()
    driver.get("https://www.kijiji.ca")
    login_with_cookies(driver)
    if not isLogin(driver):
        driver.delete_all_cookies()
        login_with_password(driver, email, password)
    else:
        return driver
    if not isLogin(driver):
        print('False to login')
    return driver


def create_video_TV_ad(
        delete_time,
        email,
        password,
        category_id,
        self_offer=True,
        sales_by_owner=True,
        willing_to_drop_off=False,
        willing_to_ship=False,
        offer_curbside_pick_up=False,
        offer_cashless_payment=False,
        cash_accepted=False,
        # use one of these: (New/Used - Like new/Used - Good/Used - Fair)
        condition=None,
        title='this is an ads',
        description='this is an description',
        tags=None,  # change it into a line like this: tv, video, remote
        images=['C:\\Users\\duong\\Downloads\\Web automation(2).png'],
        youtube_url=None,
        location=None,
        # choose one of ("Fixed"/"Free"/"Please Contact"/"Swap/Trade")
        price_type='Free',
        price='5',
        city=None,
        phone_number=None,
        try_again=0
):
    try:
        if try_again >= 3:
            return
        while True:
            with lock:
                st = pickle.load(open("single_thread.pkl", "rb"))
            if not st:
                sleep(5 * 60)
            else:
                break
        with lock:
            pickle.dump(False, open("single_thread.pkl", "wb"))
        check_ad_title_and_delete(title=title, email=email, password=password)
        driver = login(email, password)
        wait = WebDriverWait(driver, 20)
        driver.get(
            f'https://www.kijiji.ca/p-admarkt-post-ad.html?categoryId={category_id}&siteLocale=en_CA')
        # wait until the site finish loading
        wait.until(EC.presence_of_element_located(
            (By.XPATH, "//span[text()='I want to find']")))
        if not self_offer:
            try:
                self_offer_button = wait.until(EC.presence_of_element_located(
                    (By.XPATH, "//span[text()='I want to find']")))
                driver.execute_script(
                    "arguments[0].click();", self_offer_button)
            except:
                print('can\'t set find product')
        if not sales_by_owner:
            try:
                sales_by_button = wait.until(EC.presence_of_element_located(
                    (By.XPATH, "//label[text()='Business']")))
                driver.execute_script("arguments[0].click();", sales_by_button)
                sleep(1)
            except:
                print('can\'t set to business')
        if willing_to_drop_off:
            try:

                drop_off_button = wait.until(EC.presence_of_element_located(
                    (By.XPATH, "//label[text()='Willing to drop-off / deliver']")))
                driver.execute_script("arguments[0].click();", drop_off_button)
                sleep(1)
            except:
                print('can\'t set willing to drop off')
        if willing_to_ship:
            try:
                willing_ship_button = wait.until(EC.presence_of_element_located(
                    (By.XPATH, "//label[text()='Willing to ship the item']")))
                driver.execute_script(
                    "arguments[0].click();", willing_ship_button)
                sleep(1)
            except:
                print('can\'t set willing to ship')
        if offer_curbside_pick_up:
            try:
                offer_curbside_pick_up_button = wait.until(EC.presence_of_element_located(
                    (By.XPATH, "//label[text()='Offer curbside pick up']")))
                driver.execute_script(
                    "arguments[0].click();", offer_curbside_pick_up_button)
                sleep(1)
            except:
                print('can\'t add curbside pick up')
        if offer_cashless_payment:
            try:
                cashless_button = wait.until(EC.presence_of_element_located(
                    (By.XPATH, "//label[text()='Offer cashless payment']")))
                driver.execute_script("arguments[0].click();", cashless_button)
                sleep(1)
            except:
                print('can\' set cashless payment')
        if cash_accepted:
            try:
                cash_accepted_button = wait.until(EC.presence_of_element_located(
                    (By.XPATH, "//label[text()='Cash accepted']")))
                driver.execute_script(
                    "arguments[0].click();", cash_accepted_button)
                sleep(1)
            except:
                print('can\'t set cash accepted')
        if condition:
            try:
                select_condition = Select(wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'select[id="condition_s"]'))))
                if condition == 'New':
                    select_condition.select_by_value('new')
                if condition == 'Used - Like new':
                    select_condition.select_by_value('usedlikenew')
                if condition == 'Used - Good':
                    select_condition.select_by_value('usedgood')
                if condition == 'Used - Fair':
                    select_condition.select_by_value('usedfair')
            except:
                print('can\' add condition')
        title_input = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'input[id="postad-title"]')))
        title_input.send_keys(title)
        sleep(1)
        description_input = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'textarea[id="pstad-descrptn"]')))
        description_input.send_keys(description)
        sleep(1)
        if tags:
            try:
                tags = tags + '\n'
                tags_input = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'input[id="pstad-tagsInput"]')))
                tags_input.send_keys(tags)
                sleep(1)
            except:
                print('can\'t add tags')
        if images:
            image_keys = '\n'.join(images)
            try:
                wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'input[type="file"]'))).send_keys(image_keys)
                sleep(1)
            except:
                traceback.print_exc()
                print('can\'t upload image')
        if youtube_url:
            try:
                wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'input[id="YoutubeURL"]'))).send_keys(youtube_url)
                sleep(1)
            except:
                print('can\'t add youtube url')
        if location:
            try:
                location_change_button = wait.until(
                    EC.presence_of_element_located((By.XPATH, "//button[text()='Change']")))
                driver.execute_script(
                    "arguments[0].click();", location_change_button)
                sleep(0.5)
                sleep(15)
                location_input = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'textarea[id="location"]')))
                location_input.send_keys(location)
                sleep(15)
                location_selector = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div[id="LocationSelector-item-0"]')))
                driver.execute_script(
                    "arguments[0].click();", location_selector)
                sleep(15)
            except Exception as e:
                traceback.print_exc()
                print('used input location')
        if city:
            try:
                select_city = Select(wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'select[id="postingLocation"]'))))
                select_city.select_by_visible_text(city)
            except:
                traceback.print_exc()
                print('unable to located city')
        if price_type == 'Fixed':
            try:
                wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'input[id="PriceAmount"]'))).send_keys(price)
            except:
                print('can\'t set price type')
        else:
            try:
                price_type_button = wait.until(EC.presence_of_element_located(
                    (By.XPATH, f"//label[text()='{price_type}']")))
                driver.execute_script(
                    "arguments[0].click();", price_type_button)
            except:
                print('can\' choose price type')

        if phone_number:
            try:
                phone_input = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'input[id="PhoneNumber"]')))
                phone_input.send_keys(phone_number)
            except:
                print('can\'t add phone number')
        sleep(300)
        post_ad_button = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//button[text()='Post Your Ad']")))
        driver.execute_script("arguments[0].click();", post_ad_button)
        sleep(60)
        ad_id = find_ad_id(driver.current_url)
        print(ad_id)
        if not ad_id:
            raise Exception('ID not founded')
        add_delete_schedule(ad_id, delete_time, email, password)
        try:
            current_time = datetime.datetime.now()
            with lock:
                with open('log.txt', 'a', encoding='utf-8') as f:
                    f.write(
                        f'[{current_time}] succesfully created video ad: {title}\n')
        except:
            print(e)
        driver.quit()
    except Exception as e:
        # Get the current date and time
        current_datetime = datetime.datetime.now()

        # Format the date and time as a string (you can customize the format)
        formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")

        # Create a filename using the formatted date and time
        filename = f"file_{formatted_datetime}.png"
        driver.save_screenshot(filename)
        driver.quit()
        print(e)
        traceback.print_exc()
        print('can\'t create TV ad')
        try:
            current_time = datetime.datetime.now()
            with lock:
                with open('log.txt', 'a', encoding='utf-8') as f:
                    f.write(
                        f'[{current_time}] False to create video ad: {title}\n error: {traceback.format_exc()}\n')
            threading.Timer(900, create_video_TV_ad, args=(delete_time, email, password, category_id, self_offer,
                                                           sales_by_owner, willing_to_drop_off, willing_to_ship,
                                                           offer_curbside_pick_up, offer_cashless_payment,
                                                           cash_accepted,
                                                           condition, title, description, tags, images, youtube_url,
                                                           location, price_type, price, city, phone_number,
                                                           try_again + 1)).start()
        except:
            print(e)
    finally:
        with lock:
            pickle.dump(True, open("single_thread.pkl", "wb"))


def run_threaded(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread.start()


def create_kijiji_ad(
        delete_time,
        email,
        password,
        category_id,
        area_location='Alberta,Calgary',
        self_offer=True,
        offer_cashless_payment=False,
        cash_accepted=False,
        title='this is an ads',
        description='this is an description',
        tags=None,  # change it into a line like this: tv, video, remote
        address=None,
        images=['C:\\Users\\duong\\Downloads\\Web automation(2).png'],
        youtube_url=None,
        phone_number=None,
        package_type='Basic',
        try_again=0
):
    try:
        if try_again >= 3:
            return
        while True:
            with lock:
                st = pickle.load(open("single_thread.pkl", "rb"))
            if not st:
                sleep(5 * 60)
            else:
                break
        with lock:
            pickle.dump(False, open("single_thread.pkl", "wb"))
        check_ad_title_and_delete(title=title, email=email, password=password)
        driver = login(email, password)
        wait = WebDriverWait(driver, 20)
        driver.get(
            f'https://www.kijiji.ca/p-post-ad.html?categoryId={category_id}&siteLocale=en_CA')
        try:
            next_button = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//a[text()='Go']")))
            areas = area_location.split(',')
            areas = [area.strip() for area in areas]
            for area in areas:
                area_button = wait.until(EC.presence_of_element_located(
                    (By.XPATH, f"//a[text()='{area}']")))
                driver.execute_script("arguments[0].click();", area_button)
                sleep(0.5)
            driver.execute_script("arguments[0].click();", next_button)
        except Exception as e:
            print(e)
        if not self_offer:
            try:
                self_offer_button = wait.until(EC.presence_of_element_located(
                    (By.XPATH, "//span[text()='I want to find']")))
                driver.execute_script(
                    "arguments[0].click();", self_offer_button)
            except Exception as e:
                print('can\'t set to find')
        if offer_cashless_payment:
            try:
                cashless_button = wait.until(EC.presence_of_element_located(
                    (By.XPATH, "//label[text()='Offer cashless payment']")))
                driver.execute_script("arguments[0].click();", cashless_button)
                sleep(1)
            except Exception as e:
                print('can\'t set cashless paymment')
        if cash_accepted:
            try:
                cash_accepted_button = wait.until(EC.presence_of_element_located(
                    (By.XPATH, "//label[text()='Cash accepted']")))
                driver.execute_script(
                    "arguments[0].click();", cash_accepted_button)
                sleep(1)
            except Exception as e:
                print('can\'t set cash accepted')
        wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'input[id="postad-title"]')))
        title_input = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'input[id="postad-title"]')))
        title_input.send_keys(title)
        sleep(1)
        description_input = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'textarea[id="pstad-descrptn"]')))
        description_input.send_keys(description)
        sleep(1)
        if tags:
            try:
                tags = tags + '\n'
                tags_input = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'input[id="pstad-tagsInput"]')))
                tags_input.send_keys(tags)
                sleep(1)
            except:
                print('can\' add tags')
        try:
            address_input = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'textarea[aria-labelledby="LocationSelector-label"]')))
            address_input.send_keys(address)
            sleep(15)
            location_selector = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'div[id="LocationSelector-item-0"]')))
            driver.execute_script("arguments[0].click();", location_selector)
            sleep(5)
        except Exception as e:
            traceback.print_exc()
            print('can\' pick suggest location')
        if images:
            image_keys = '\n'.join(images)
            try:
                wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'input[type="file"]'))).send_keys(image_keys)
                sleep(1)
            except:
                traceback.print_exc()
                print('can\'t upload image')
        if youtube_url:
            try:
                wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'input[id="YoutubeURL"]'))).send_keys(youtube_url)
                sleep(1)
            except:
                print('can\'t add youtube url')
        if phone_number:
            try:
                phone_input = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'input[id="PhoneNumber"]')))
                phone_input.send_keys(phone_number)
            except:
                print('can\'t add phone number')
        sleep(5)

        if package_type == "Basic":
            package_id = '0'
        elif package_type == 'Plus':
            package_id = '1'
        elif package_type == 'Premium':
            package_id = '2'
        elif package_type == 'Supreme':
            package_id = '3'
        else:
            package_id = '0'
        package = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, f'button[data-qa-id="package-{package_id}-bottom-select"]')))
        driver.execute_script("arguments[0].click();", package)
        sleep(300)
        post_ad = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//button[text()='Post Your Ad']")))
        driver.execute_script("arguments[0].click();", post_ad)

        sleep(60)
        ad_id = find_ad_id(driver.current_url)
        if not ad_id:
            raise ('ID not founded')
        add_delete_schedule(ad_id, delete_time, email, password)
        try:
            current_time = datetime.datetime.now()
            with lock:
                with open('log.txt', 'a', encoding='utf-8') as f:
                    f.write(
                        f'[{current_time}] succesfully created plumbing ad: {title}\n')
        except:
            print(e)
        driver.quit()
    except:
        # Get the current date and time
        current_datetime = datetime.datetime.now()

        # Format the date and time as a string (you can customize the format)
        formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")

        # Create a filename using the formatted date and time
        filename = f"file_{formatted_datetime}.png"
        driver.save_screenshot(filename)

        print('can\' add plumber ad')
        try:
            current_time = datetime.datetime.now()
            with lock:
                with open('log.txt', 'a', encoding='utf-8') as f:
                    f.write(
                        f'[{current_time}] False to create plumbing ad: {title}\n error: {traceback.format_exc()}\n')
            threading.Timer(900, create_kijiji_ad, args=(delete_time,
                                                           email,
                                                           password,
                                                           category_id,
                                                           area_location,
                                                           self_offer,
                                                           offer_cashless_payment,
                                                           cash_accepted,
                                                           title,
                                                           description,
                                                           tags,  # change it into a line like this: tv, video, remote
                                                           address,
                                                           images,
                                                           youtube_url,
                                                           phone_number, package_type,
                                                           try_again + 1)).start()

            driver.quit()
        except Exception as e:
            print(e)
    finally:
        with lock:
            pickle.dump(True, open("single_thread.pkl", "wb"))


def delete_all_ads(driver):
    driver = login()
    driver.get('https://www.kijiji.ca/m-my-ads/active/1')
    wait = WebDriverWait(driver, 15)
    try:
        delete_buttons = wait.until(EC.presence_of_all_elements_located(
            ((By.XPATH, "//span[text()='Delete']"))))
        number_of_ads = len(delete_buttons)
        for delete_button in delete_buttons:
            try:
                delete_button.click()
                try:
                    wait.until(EC.presence_of_element_located(
                        (By.XPATH, "//button[text()='Prefer not to say']"))).click()
                    sleep(1)
                    wait.until(EC.presence_of_element_located(
                        (By.XPATH, "//button[text()='Delete My Ad']"))).click()
                    if number_of_ads > 1:
                        delete_all_ads(driver)
                    else:
                        return
                except Exception as e:
                    print(e)
                    driver.get('https://www.kijiji.ca/m-my-ads/active/1')
                sleep(5)
            except Exception as e:
                print(e)
    except Exception as e:
        print(e)
    driver.quit()


def check_ad_alive(driver, ad_id):
    try:
        driver.get(
            f'https://www.kijiji.ca/v-view-details.html?adId={ad_id}&siteLocale=en_CA')
        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_element_located(
            (By.XPATH, "//h1[text()='Hmm... Apparently this page no longer exists.']")))
        return True
    except:
        return False


def delete_ad_by_id(ad_id, email=None, password=None):
    try:
        while True:
            with lock:
                st = pickle.load(open("single_thread.pkl", "rb"))
            if not st:
                sleep(5 * 60)
            else:
                break
        with lock:
            pickle.dump(False, open("single_thread.pkl", "wb"))
        driver = login(email, password)
        driver.get('https://www.kijiji.ca/m-my-ads/active/1')
        sleep(5)
        wait = WebDriverWait(driver, 15)
        ad_cell = wait.until(EC.presence_of_element_located(
            ((By.XPATH, f'//tr[@data-qa-id="ad-id-{ad_id}"]/following-sibling::div[1]'))))

        delete_button = ad_cell.find_element(
            By.CSS_SELECTOR, 'button[aria-label="Delete Ad"]')
        driver.execute_script("arguments[0].click();", delete_button)
        try:
            delete_reason = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//button[text()='Prefer not to say']")))
            driver.execute_script("arguments[0].click();", delete_reason)
            sleep(3)
            delete_my_ad_button = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//button[text()='Delete My Ad']")))
            driver.execute_script("arguments[0].click();", delete_my_ad_button)

        except Exception as e:
            print(e)
            driver.get('https://www.kijiji.ca/m-my-ads/active/1')
        sleep(5)

        if check_ad_alive(driver=driver, ad_id=ad_id):
            raise Exception('ads not deleted')
        try:
            with lock:
                current_time = datetime.datetime.now()
                with open('log.txt', 'a', encoding='utf-8') as f:
                    f.write(f'[{current_time}] Deleted one ad id: {ad_id}\n')
        except Exception as e:
            print(e)
        driver.quit()

    except:
        try:
            add_delete_schedule(id=ad_id, seconds_to_add=600)
            with lock:
                current_time = datetime.datetime.now()
                with open('log.txt', 'a', encoding='utf-8') as f:
                    f.write(
                        f'[{current_time}] cant\'t delete one ad: id = {ad_id}\n error: {traceback.format_exc()}\n')
            # Get the current date and time
            current_datetime = datetime.datetime.now()

            # Format the date and time as a string (you can customize the format)
            formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")

            # Create a filename using the formatted date and time
            filename = f"file_{formatted_datetime}.png"
            driver.save_screenshot(filename)
        except Exception as e:
            print(e)
    finally:
        with lock:
            pickle.dump(True, open("single_thread.pkl", "wb"))
        driver.quit()


def check_ad_title_and_delete(title, email, password):
    driver = login(email, password)
    print('checking active ads')
    driver.get('https://www.kijiji.ca/m-my-ads/active/1')
    wait = WebDriverWait(driver, 15)
    try:
        ad_cell = wait.until(
            EC.presence_of_element_located((By.XPATH, f'//a[text()="{title}"]/ancestor::tr/following-sibling::div[1]')))
        print(ad_cell.get_attribute("innerHTML"))
        delete_button = WebDriverWait(ad_cell, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'button[aria-label="Delete Ad"]')))
        driver.execute_script("arguments[0].click();", delete_button)
        try:
            delete_reason = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//button[text()='Prefer not to say']")))
            driver.execute_script("arguments[0].click();", delete_reason)
            sleep(3)
            delete_my_ad_button = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//button[text()='Delete My Ad']")))
            driver.execute_script("arguments[0].click();", delete_my_ad_button)

        except Exception as e:
            print(e)
            driver.get('https://www.kijiji.ca/m-my-ads/active/1')
        sleep(5)
    except:
        print(f'no ad with title: {title}')

    finally:
        driver.quit()
        try:
            with lock:
                current_time = datetime.datetime.now()
                with open('log.txt', 'a', encoding='utf-8') as f:
                    f.write(f'[{current_time}] checked ad: {title}\n')
        except Exception as e:
            print(e)

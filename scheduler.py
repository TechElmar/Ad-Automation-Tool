from functools import partial
import schedule
from new_kijiji import *
from datetime import datetime


def set_schedule(ad, days, start_times, delete_times):
    if not isinstance(days, list):
        days = [days]
    for day in days:
        for index, start_time in enumerate(start_times):
            # Create datetime objects from the time strings
            time1 = datetime.strptime(start_time, "%H:%M")
            time2 = datetime.strptime(delete_times[index], "%H:%M")

            # Calculate the time difference in seconds
            time_difference_seconds = abs((time1 - time2).total_seconds())
            new_ad = partial(ad, delete_time=time_difference_seconds)

            exec(f'schedule.every().{day.lower()}.at(start_time).do(run_threaded, new_ad)')


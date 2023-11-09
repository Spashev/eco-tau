from datetime import datetime, timedelta


def has_passed_30_minutes(target_time):
    current_time = datetime.now()
    time_difference = current_time - target_time
    return time_difference >= timedelta(minutes=30)


def has_passed_2_minutes(target_time):
    current_time = datetime.now()
    time_difference = current_time - target_time
    return time_difference >= timedelta(minutes=2)

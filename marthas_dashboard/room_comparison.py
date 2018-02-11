from datetime import datetime, timedelta


def generate_15_min_timestamps():
    timestamps = []
    first_time = datetime.strptime("00:00:00", "%H:%M:%S")
    end_time = datetime.strptime("23:59:59", "%H:%M:%S")
    while first_time < end_time:
        timestamps.append(first_time.strftime("%H:%M:%S"))
        first_time += timedelta(minutes=15)
    return timestamps
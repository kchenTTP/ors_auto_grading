import datetime

from hydra import compose, initialize


def get_start_date(current_date: datetime.date = datetime.datetime.now().date()) -> datetime.date:
    with initialize(version_base=None, config_path="../conf"):
        config = compose(config_name="config")

    fall_start = datetime.datetime.strptime(
        f"{config.dates.fall}-{current_date.year}", "%m-%d-%Y"
    ).date()
    spring_start = datetime.datetime.strptime(
        f"{config.dates.spring}-{current_date.year}", "%m-%d-%Y"
    ).date()

    if current_date < fall_start and current_date > spring_start:
        return spring_start
    elif current_date > fall_start and current_date > spring_start:
        return fall_start
    else:
        return fall_start - datetime.timedelta(days=365.24)

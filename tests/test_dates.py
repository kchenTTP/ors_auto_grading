import datetime

from app_utils import datetime_helper


def test_get_start_date() -> None:
    cur_date = datetime.datetime.now().date()
    spring_start = datetime.date(year=cur_date.year, month=2, day=1)
    fall_start = datetime.date(year=cur_date.year, month=9, day=1)
    last_fall_start = fall_start - datetime.timedelta(days=365.24)

    test_date = datetime.date(year=cur_date.year, month=4, day=30)
    result = datetime_helper.get_start_date(current_date=test_date)

    assert result == spring_start

    test_date = datetime.date(year=cur_date.year, month=2, day=15)
    result = datetime_helper.get_start_date(current_date=test_date)

    assert result == spring_start

    test_date = datetime.date(year=cur_date.year, month=10, day=15)
    result = datetime_helper.get_start_date(current_date=test_date)

    assert result == fall_start

    test_date = datetime.date(year=cur_date.year, month=12, day=15)
    result = datetime_helper.get_start_date(current_date=test_date)

    assert result == fall_start

    test_date = datetime.date(year=cur_date.year, month=1, day=15)
    result = datetime_helper.get_start_date(current_date=test_date)

    assert result == last_fall_start

    test_date = datetime.date(year=cur_date.year, month=1, day=1)
    result = datetime_helper.get_start_date(current_date=test_date)

    assert result == last_fall_start

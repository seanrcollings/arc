import datetime
from hypothesis import given, assume, note
from hypothesis import strategies as st

import pytest
import arc
from arc import errors


@given(st.datetimes())
def test_datetime(date: datetime.datetime):
    assume(not date.microsecond)

    @arc.command
    def dt(val: datetime.datetime):
        return val

    assert dt(date.isoformat()) == date

    with pytest.raises(errors.ArgumentError):
        dt("dt bad")


@given(st.dates())
def test_date(date: datetime.date):
    @arc.command
    def dt(val: datetime.date):
        return val

    assert dt(date.isoformat()) == date

    with pytest.raises(errors.ArgumentError):
        dt("dt bad")


@given(st.times())
def test_time(time: datetime.time):
    assume(not time.microsecond)

    @arc.command
    def dt(val: datetime.time):
        return val

    assert dt(time.isoformat()) == time

    with pytest.raises(errors.ArgumentError):
        dt("dt bad")

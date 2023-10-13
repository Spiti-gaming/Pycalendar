import datetime
from dataclasses import dataclass


@dataclass
class TimeManip2:
    type_year: bool = True
    time_stamp_start: str = None
    time_stamp_stop: str = None
    start: datetime = None
    end: datetime = None
    today: datetime.date = datetime.date.today()

    def __post_init__(self):
        if self.type_year:
            self.years()
        else:
            self.week()
        self.time_stamp_start = str(int(datetime.datetime.combine(self.start, datetime.time.min).timestamp() * 1000))
        self.time_stamp_stop = str(int(datetime.datetime.combine(self.end, datetime.time.max).timestamp() * 1000))

    def years(self):
        self.start = datetime.date.fromisoformat(str(self.today.year) + '-08-01')
        self.end = datetime.date.fromisoformat(str(self.today.year + 1) + '-08-01')

    def week(self):
        self.start = self.today - datetime.timedelta(days=self.today.weekday())
        self.end = self.start + datetime.timedelta(days=20)


if __name__ == "__main__":
    date = TimeManip2(type_year=True)
    date2 = TimeManip2(type_year=False)

    print(date)
    print(date2)

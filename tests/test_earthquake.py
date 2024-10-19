import datetime as dt
import unittest

from jasiapi import Earthquake, earthquake


class EarthquakeTest(unittest.TestCase):
    def test(self):
        a = earthquake(
            # 1. the event date is between:
            "2000/01/01 00:00",
            "2020/01/01 00:00",
            # 2. magnitude is between 2 and 10
            magnitude=(2, 10),
            # 3. depth of the hypocenter is between 10 km and 100 km
            depth=(10, 100),
            # 4. maximum intensity is 3, at least
            intensity=3,
            # (search by largest to smallest on maximum intensity)
            sort="intensity",
            # 5. observed intensity 4 at Tokyo, at least
            station_pref=[
                "東京都",
            ],
            station_intensity=4,
            # 6. the epicenter locates the pacific coast of Tohoku
            epicenter_area=[
                (35.1, 142.14),
                (41.29, 142.14),
                (41.29, 145.68),
                (35.1, 145.68),
            ],
        )

        e = [
            Earthquake(
                id="20110311144618",
                time=dt.datetime(
                    2011,
                    3,
                    11,
                    14,
                    46,
                    18,
                    100000,
                    tzinfo=dt.timezone(dt.timedelta(seconds=32400)),
                ),
                location="三陸沖",
                latitude=38.1033,
                longitude=142.86,
                depth=24.0,
                magnitude=9.0,
                intensity=7,
            ),
            Earthquake(
                id="20050816114625",
                time=dt.datetime(
                    2005,
                    8,
                    16,
                    11,
                    46,
                    25,
                    700000,
                    tzinfo=dt.timezone(dt.timedelta(seconds=32400)),
                ),
                location="宮城県沖",
                latitude=38.1483,
                longitude=142.277,
                depth=42.0,
                magnitude=7.2,
                intensity="6L",
            ),
            Earthquake(
                id="20121207171830",
                time=dt.datetime(
                    2012,
                    12,
                    7,
                    17,
                    18,
                    30,
                    800000,
                    tzinfo=dt.timezone(dt.timedelta(seconds=32400)),
                ),
                location="三陸沖",
                latitude=38.0183,
                longitude=143.867,
                depth=49.0,
                magnitude=7.3,
                intensity="5L",
            ),
        ]
        self.assertEqual(e, a)


if __name__ == "__main__":
    unittest.main()

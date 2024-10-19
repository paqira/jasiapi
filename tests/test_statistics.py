import datetime as dt
import unittest

from jasiapi import (
    Statistics,
    StatisticsSummary,
    statistics,
)


class StatisticsTest(unittest.TestCase):
    def test(self):
        stats, summary = statistics(
            # 1. the event date is between:
            "2000/01/01 00:00",
            "2020/01/01 00:00",
            # 2. magnitude is between 2 and 10
            magnitude=(2, 10),
            # 3. depth of the hypocenter is between 10 km and 100 km
            depth=(10, 100),
            # 4. maximum intensity is 3, at least
            intensity=3,
            # (agg by year)
            method="year",
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

        self.assertEqual(21, len(stats))
        self.assertEqual(
            Statistics(
                key=dt.datetime(
                    2000,
                    1,
                    1,
                    0,
                    0,
                    tzinfo=dt.timezone(dt.timedelta(seconds=32400)),
                ),
                unit="year",
                one=0,
                two=0,
                three=0,
                four=0,
                five_L=0,
                five_H=0,
                six_L=0,
                six_H=0,
                seven=0,
            ),
            stats[0],
        )

        self.assertEqual(
            StatisticsSummary(
                one=0,
                two=0,
                three=0,
                four=2,
                five_L=0,
                five_H=1,
                six_L=0,
                six_H=0,
                seven=0,
            ),
            summary,
        )


if __name__ == "__main__":
    unittest.main()

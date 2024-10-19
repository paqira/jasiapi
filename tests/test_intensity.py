import datetime as dt
import unittest

from jasiapi import Earthquake, Intensity, intensity


class IntensityTest(unittest.TestCase):
    def test(self):
        ints, eq = intensity("20110311144618")

        self.assertEqual(
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
            eq,
        )

        self.assertEqual(2901, len(ints))

        self.assertEqual(
            Intensity(
                station_name="栗原市築館（旧）＊",
                station_number=2205220,
                latitude=38.73,
                longitude=38.73,
                intensity=7,
            ),
            ints[0],
        )


if __name__ == "__main__":
    unittest.main()

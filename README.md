# jasiapi

This package provides unofficial Python binding of *[JMA Seismic Intensity DB Search][SIDB]*
(*気象庁震度データベース検索*) API.

[SIDB]: https://www.data.jma.go.jp/svd/eqdb/data/shindo/index.php

## Usage

You can install `jasiapi` from PyPI:

```shell
pip install jasiapi
```

One can online search to fundamental information of the earthquake event at Japan,
hypocenter, magnitude, JAM (max) seismic intensity and its statistics,
from 1919 until 2 days ago (UTC+9).

Please use this with restraint,
because it calls Web API every calling function and this is unofficial.

1919 年から 2 日前までの地震の基本的な情報（震度、マグニチュード、震源）をオンラインで検索できます。関数を呼び出す度に気象庁の（非公式な）
Web API を叩いています。節度を守ってご利用ください。

```python
import jasiapi


# Search earthquake satisfies all following conditions:
# 下記条件の地震を全て満たす地震を検索
earthquakes = jasiapi.earthquake(
    # 1. the event date is between:
    # 1. 以下の期間に発災した地震
    "2000/01/01 00:00", "2020/01/01 00:00",
    # 2. magnitude is between 2 and 10,
    # 2. マグニチュードが 2 から 10 
    magnitude=(2, 10),
    # 3. depth of hypocenter is between 10 km and 100 km,
    # 3. かつ、震源の深さが 10 km から 100 km 
    depth=(10, 100),
    # 4. maximum intensity is 3, at least,
    # 4. 最大震度が少なくとも震度 3
    intensity=3,
    # (search by largest to smallest on maximum intensity)
    # （最大震度の降順（大から小）で検索）
    sort="intensity",
    # 5. observed intensity 4 at Tokyo, at least
    # 5. 東京都で少なくとも震度 4 を観測
    station_pref=["東京都", ],
    station_intensity=4,
    # 6. epicenter locates the pacific coast of Tohoku
    # 6. 震源が東北沖に位置する
    epicenter_area=[(35.1, 142.14), (41.29, 142.14), (41.29, 145.68), (35.1, 145.68)],
)

# Prints (manually formatted):
# [
#   Earthquake(
#       id='20110311144618',
#       time=datetime.datetime(2011, 3, 11, 14, 46, 18, 100000, tzinfo=UTC+9),
#       location='三陸沖',
#       latitude=38.1033,
#       longitude=142.86,
#       depth=24.0,
#       magnitude=9.0,
#       intensity=7
#   ),
#   # and go on
# ]
print(earthquakes)


# Search JAM seismic intensity of the earthquake ID 20110311144618
# ID 20110311144618 の地震の震度を検索
intensities, earthquake = jasiapi.intensity('20110311144618')

# Prints (manually formatted):
# [
#     Intensity(
#         station_name='栗原市築館（旧）＊',
#         station_code=2205220,
#         latitude=38.73,
#         longitude=38.73,
#         intensity=7
#     ),
#     # and go on
# ]
print(intensities)
```

## LICENSE

MIT

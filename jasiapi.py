"""Unofficial Python binding of *JMA Seismic Intensity Database Search* (気象庁 震度データベース検索) API."""

from __future__ import annotations

import datetime as dt
from typing import Any, Final, Literal, NamedTuple, Sequence

import requests

__all__ = [
    "earthquake",
    "statistics",
    "intensity",
    #
    "Earthquake",
    "Statistics",
    "StatisticsSummary",
    "Intensity",
    "CodeResolver",
    #
    "Error",
    "BadRequestError",
]

__version__: Final = "0.1.0"

TOP: Final = "https://www.data.jma.go.jp/svd/eqdb/data/shindo/index.html"
URL: Final = "https://www.data.jma.go.jp/svd/eqdb/data/shindo/api/api.php"

EPICENTER: Final = "https://www.data.jma.go.jp/svd/eqdb/data/shindo/js/epi.json"
CITY: Final = "https://www.data.jma.go.jp/svd/eqdb/data/shindo/js/city.json"
STATION: Final = "https://www.data.jma.go.jp/svd/eqdb/data/shindo/js/station.json"

PREFECTURE: Final = {
    10: "北海道",
    20: "青森県",
    21: "岩手県",
    22: "宮城県",
    23: "秋田県",
    24: "山形県",
    25: "福島県",
    30: "茨城県",
    31: "栃木県",
    32: "群馬県",
    33: "埼玉県",
    34: "千葉県",
    35: "東京都",
    36: "神奈川県",
    37: "新潟県",
    38: "富山県",
    39: "石川県",
    40: "福井県",
    41: "山梨県",
    42: "長野県",
    43: "岐阜県",
    44: "静岡県",
    45: "愛知県",
    46: "三重県",
    50: "滋賀県",
    51: "京都府",
    52: "大阪府",
    53: "兵庫県",
    54: "奈良県",
    55: "和歌山県",
    56: "鳥取県",
    57: "島根県",
    58: "岡山県",
    59: "広島県",
    60: "徳島県",
    61: "香川県",
    62: "愛媛県",
    63: "高知県",
    70: "山口県",
    71: "福岡県",
    72: "佐賀県",
    73: "長崎県",
    74: "熊本県",
    75: "大分県",
    76: "宮崎県",
    77: "鹿児島県",
    80: "沖縄県",
}

# global state of code resolver
_code_resolver: CodeResolver | None = None


class Error(Exception):
    """Base error class."""

    pass


class BadRequestError(Error, IOError):
    """Error of request failed."""

    pass


def _request(data: dict[str, Any]):
    res = requests.post(URL, data=data)
    return res.json()


def _solve_station_info(  # noqa: C901
    station_pref: Sequence[int | str] | None,
    station_city: Sequence[int | str] | None,
    station: Sequence[int | str] | None,
    station_intensity: Literal[1, 2, 3, 4, "5L", "5H", "6L", "6H", 7, "A", "B", "C", "D"] | None,
):
    global _code_resolver

    if station_pref is None:
        _station_pref = [99]
    else:
        if _code_resolver is None:
            _code_resolver = CodeResolver()

        _station_pref = []
        for pref in station_pref:
            if pref in _code_resolver.prefecture_codes():
                _station_pref.append(pref)
            else:
                data = _code_resolver.prefecture_code(pref)
                _station_pref.append(data)

    if station_city is None:
        _station_city = [99]
    else:
        if _code_resolver is None:
            _code_resolver = CodeResolver()

        _station_city = []
        for city in station_city:
            if city in _code_resolver.city_codes():
                _station_city.append(city)
            else:
                data = _code_resolver.city_code(city)
                _station_city.append(data)

    if station is None:
        _station = [99]
    else:
        if _code_resolver is None:
            _code_resolver = CodeResolver()

        _station = []
        for st in station:
            if st in _code_resolver.station_codes():
                _station.append(st)
            else:
                data = _code_resolver.station_code(st)
                _station.append(data)

    if station_intensity is None:
        station_intensity = 1
    else:
        station_intensity = _parse_input_intensity(station_intensity)
    return _station_pref, _station_city, _station, station_intensity


def earthquake(
    start: dt.datetime | dt.date | str,
    end: dt.datetime | dt.date | str,
    *,
    magnitude: tuple[float, float] = (0.0, 9.9),
    depth: tuple[int, int] = (0, 999),
    intensity: Literal[1, 2, 3, 4, "5L", "5H", "6L", "6H", 7, "A", "B", "C", "D"] = 1,
    sort: Literal["start", "end", "intensity", "scale"] = "start",
    station_pref: Sequence[int | str] | None = None,
    station_city: Sequence[int | str] | None = None,
    station: Sequence[int | str] | None = None,
    station_intensity: Literal[1, 2, 3, 4, "5L", "5H", "6L", "6H", 7, "A", "B", "C", "D"] | None = None,
    epicenter_region: Sequence[str] | None = None,
    epicenter_area: Sequence[tuple[float, float]] = None,
) -> list[Earthquake]:
    """Search for earthquakes (a.k.a. hypocenter).

    The conditions are **AND** condition except `station_pref`, `station_city` and `station`.

    It searches for earthquakes whose seismic intensity was observed in that area
    or by seismic intensity station, if one specify
    `station_pref`, `station_city`, `station` and/or `station_intensity`.

    If `epicenter_region` and/or `epicenter_area` is specified,
    it searches for earthquakes whose hypocenter locates at the region/area.

    `station_pref`, `station_city` and `station` accept Japanese name only,
    :class:`CodeResolver` helps to find such names and codes.

    Args:
        start: search earthquake which occurs after the date (inclusive),
               supports :obj:`'yyyy/mm/dd hh:mm'` and :obj:`'yyyy-mm-dd hh:mm'` formats
               when :obj:`str` given
        end: search earthquake which occurs before the date (may inclusive),
             support the same format of `start`
        magnitude: magnitude range (inclusive) of earthquake
        depth: depth (km) range (inclusive) of earthquake
        intensity: maximum JMA seismic intensity of the resulting earthquake is equal or greater than.
                   The value means the JAM seismic intensity,
                   especially, :obj:`'5L'` and :obj:`'A'` means *5 Lower*,
                   :obj:`'5H'` and :obj:`'B'` does *5 Higher*,
                   :obj:`'6L'` and :obj:`'C'` does *6 Lower*,
                   and :obj:`'6H'` and :obj:`'D'` does *6 Higher*.
        sort: sorting method, we note that it only returns first 1,000 results **without warning**;
              :obj:`'start'` means 'start to end' search,
              :obj:`'end'` does end to start,
              and :obj:`'intensity'` means largest to smallest by maximum intensity
              and :obj:`'scale'` does largest to smallest by scale
              (author: unclear what scale means...)
        station_pref: prefecture code/name where the station, which observed the earthquake, is located
        station_city: city code/name where the station, which observed the earthquake, is located,
                 `station_pref` ignores when specified
        station: station code/name which observed the earthquake,
                 `station_pref` and `station_city` ignore when specified
        station_intensity: search earthquakes which observed JMA seismic intensity is equal or greater than
        epicenter_region: region name of epicenter
        epicenter_area: corners (a pair of latitude and longitude in decimal degree)
                        of area that epicenter is in (convex hull)

    Returns:
        a list of :class:`Earthquake` (hypocenter info)

    Raises:
        BadRequestError: if the search failed

    Examples:
        >>> # Search earthquake satisfies all following conditions:
        ... eqs = earthquake(
        ...     # 1. the event date is between:
        ...     "2000/01/01 00:00", "2020/01/01 00:00",
        ...     # 2. magnitude is between 2 and 10
        ...     magnitude=(2, 10),
        ...     # 3. depth of hypocenter is between 10 km and 100 km
        ...     depth=(10, 100),
        ...     # 4. observed maximum intensity is 3, at least
        ...     intensity=3,
        ...     # (search by higher to lower on intensity)
        ...     sort="intensity",
        ...     # 5. observed, at least, intensity 4 at Tokyo
        ...     station_pref=["東京都", ],
        ...     station_intensity=4,
        ...     # 6. epicenter locates the pacific coast of Tohoku
        ...     epicenter_area=[(35.1, 142.14), (41.29, 142.14), (41.29, 145.68), (35.1, 145.68)],
        ... )
        >>> eqs
        [
            Earthquake(
                id='20110311144618',
                time=datetime.datetime(2011, 3, 11, 14, 46, 18, 100000, tzinfo=UTC+9),
                location='三陸沖',
                latitude=38.1033,
                longitude=142.86,
                depth=24.0,
                magnitude=9.0,
                intensity=7
            ),
            # and go on
        ]
    """
    _intensity = _parse_input_intensity(intensity)

    args = (station_pref, station_city, station, station_intensity, epicenter_region, epicenter_area)
    is_additional_cond = any(map(lambda v: v is not None, args))

    args = (station_pref, station_city, start, station_intensity)
    is_station_mode = any(map(lambda v: v is not None, args))

    _station_pref, _station_city, _station, station_intensity = _solve_station_info(
        station_pref, station_city, station, station_intensity
    )

    if epicenter_region is None:
        epicenter_region = [99]

    data = {
        "mode": "search",
        "dateTimeF[]": _parse_input_date(start),
        "dateTimeT[]": _parse_input_date(end),
        "mag[]": magnitude,
        "dep[]": depth,
        "maxInt": _intensity,
        "Sort": _parse_input_sort(sort),
        "Comp": "C0",  # for stats.
        #
        "additionalC": "true" if is_additional_cond else "false",
        #
        "observed": "true" if is_station_mode else "false",
        "pref[]": _station_pref,
        "city[]": _station_city,
        "station[]": _station,
        "obsInt": station_intensity,
        "epi[]": epicenter_region,
        # "ture" if stats. mode
        "seisCount": "false",
    }

    if epicenter_area is not None:
        data = {**data, **_parse_input_area(epicenter_area)}

    json = _request(data=data)

    if isinstance(json["res"], str):
        raise BadRequestError(json["res"])
    return list(map(_parse_earthquake, json["res"]))


def statistics(
    start: dt.datetime | dt.date | str,
    end: dt.datetime | dt.date | str,
    magnitude: tuple[float, float] = (0.0, 9.9),
    depth: tuple[float, float] = (0, 999),
    intensity: Literal[1, 2, 3, 4, "5L", "5H", "6L", "6H", 7, "A", "B", "C", "D"] = 1,
    method: Literal["year", "month", "day"] = None,
    station_pref: Sequence[int | str] | None = None,
    station_city: Sequence[int | str] | None = None,
    station: Sequence[int | str] | None = None,
    station_intensity: Literal[1, 2, 3, 4, "5L", "5H", "6L", "6H", 7, "A", "B", "C", "D"] = None,
    epicenter_region: Sequence[str] | None = None,
    epicenter_area: Sequence[tuple[float, float]] = None,
) -> tuple[list[Statistics], StatisticsSummary | None]:
    """Search occurrence of earthquake.

    See :func:`earthquake` for detail.

    Args:
        start: search earthquake which occurs after the date (inclusive),
               supports :obj:`'yyyy/mm/dd hh:mm'` and :obj:`'yyyy-mm-dd hh:mm'` formats
               when :obj:`str` given
        end: search earthquake which occurs before the date (may inclusive),
             support the same format of `start`
        magnitude: magnitude range (inclusive) of earthquake
        depth: depth (km) range (inclusive) of earthquake
        intensity: maximum JMA seismic intensity of the resulting earthquake is equal or greater than
        method: method of aggrigation, :obj:`'day'` is aviable for 1 month search duration,
                and :obj:`'month'` is three years search duration;
                it automatically determins the method from data when :obj:`None` given;
                it aggs by hour on short duration search
        station_pref: prefecture code/name where the station, which observed the earthquake, is located
        station_city: city code/name where the station, which observed the earthquake, is located,
                 `station_pref` ignore when specified
        station: station code/name which observed the earthquake,
                 `station_pref` and `station_city` ignore when specified
        station_intensity: search earthquakes which observed JMA seismic intensity is equal or greater than
        epicenter_region: region name of epicenter
        epicenter_area: corners (a pair of latitude and longitude in decimal degree)
                        of area that epicenter is in (convex hull)

    Returns:
        a pair of :class:`Statistics` list and :obj:`StatisticsSummary`

    Raises:
        BadRequestError: if the search failed

    Examples:
        >>> # Search earthquake satisfies all following conditions:
        ... stats, summary = earthquake(
        ...     # 1. the event date is between:
        ...     "2000/01/01 00:00", "2020/01/01 00:00",
        ...     # 2. magnitude is between 2 and 10
        ...     magnitude=(2, 10),
        ...     # 3. depth of hypocenter is between 10 km and 100 km
        ...     depth=(10, 100),
        ...     # 4. observed maximum intensity is 3, at least
        ...     intensity=3,
        ...     # (agg by year)
        ...     method="year",
        ...     # 5. observed, at least, intensity 4 at Tokyo
        ...     station_pref=["東京都", ],
        ...     station_intensity=4,
        ...     # 6. epicenter locates the pacific coast of Tohoku
        ...     epicenter_area=[(35.1, 142.14), (41.29, 142.14), (41.29, 145.68), (35.1, 145.68)],
        ... )
        >>> stats
        [
            Statistics(
                key=datetime.datetime(2000, 1, 1, 0, 0, tzinfo=UTC+9), unit='year',
                one=0, two=0, three=0, four=0, five_L=0, five_H=0, six_L=0, six_H=0, seven=0
            ),
            # and go on
        ]
        >>> summary
        StatisticsSummary(one=0, two=0, three=0, four=2, five_L=0, five_H=1, six_L=0, six_H=0, seven=0)
    """
    _intensity = _parse_input_intensity(intensity)

    args = (station_pref, station_city, station, station_intensity, epicenter_region, epicenter_area)
    is_additional_cond = any(map(lambda v: v is not None, args))

    args = (station_pref, station_city, start, station_intensity)
    is_station_mode = any(map(lambda v: v is not None, args))

    _station_pref, _station_city, _station, station_intensity = _solve_station_info(
        station_pref, station_city, station, station_intensity
    )

    if epicenter_region is None:
        epicenter_region = [99]

    data = {
        "mode": "search",
        "dateTimeF[]": _parse_input_date(start),
        "dateTimeT[]": _parse_input_date(end),
        "mag[]": magnitude,
        "dep[]": depth,
        "maxInt": _intensity,
        "Sort": "S0",  # for earthquake
        "Comp": _parse_input_window(method),
        #
        "additionalC": "true" if is_additional_cond else "false",
        #
        "observed": "true" if is_station_mode else "false",
        "pref[]": _station_pref,
        "city[]": _station_city,
        "station[]": _station,
        "obsInt": station_intensity,
        "epi[]": epicenter_region,
        # "ture" if stats. mode
        "seisCount": "true",
    }

    if epicenter_area is not None:
        data = {**data, **_parse_input_area(epicenter_area)}

    json = _request(data=data)

    if isinstance(json["res"], str):
        raise BadRequestError(json["res"])

    result = []
    summary = None
    for d in json["res"]:
        if d["lb"] == "合計":
            summary = StatisticsSummary(
                one=int(d["S1"]) if d["S1"] else 0,
                two=int(d["S2"]) if d["S2"] else 0,
                three=int(d["S3"]) if d["S3"] else 0,
                four=int(d["S4"]) if d["S4"] else 0,
                five_L=int(d["SA"]) if d["SA"] else 0,
                five_H=int(d["SB"]) if d["SB"] else 0,
                six_L=int(d["SC"]) if d["SC"] else 0,
                six_H=int(d["SD"]) if d["SD"] else 0,
                seven=int(d["S7"]) if d["S7"] else 0,
            )
        else:
            data = _parse_statistics(d)
            result.append(data)
    return result, summary


def intensity(id: str) -> tuple[list[Intensity], Earthquake]:
    """Search observed JMA seismic intensity of the earthquake.

    Args:
        id: ID of earthquake, i.e. :attr:`Earthquake.id` that :func:`earthquake` returns

    Returns:
        A pair of observed intensities and the queried earthquake data

    Raises:
        BadRequestError: if the search failed

    Examples:
        >>> ints, eq = intensity('20110311144618')
        >>> ints
        [
            Intensity(
                station_name='栗原市築館（旧）＊',
                station_code=2205220,
                latitude=38.73,
                longitude=38.73,
                intensity=7
            ),
            # and go on
        ]
        >>> eq
        Earthquake(
            id='20110311144618',
            time=datetime.datetime(2011, 3, 11, 14, 46, 18, 100000, tzinfo=UTC+9),
            location='三陸沖',
            latitude=38.1033,
            longitude=142.86,
            depth=24.0,
            magnitude=9.0,
            intensity=7
        )
    """
    data = {
        "mode": "event",
        "id": id,
    }

    json = _request(data=data)

    if isinstance(json["res"], str):
        raise BadRequestError(json["res"])
    assert len(json["res"]["hyp"]) == 1, "unexpected response, make issue with query data"
    return list(map(_parse_intensity, json["res"]["int"])), _parse_earthquake(json["res"]["hyp"][0])


class Earthquake(NamedTuple):
    """Earthquake data."""

    id: str
    """ID of the event"""
    time: dt.datetime
    """Datetime of the event"""
    location: str
    """Name of hypocenter location (in Japanese)"""
    latitude: float
    """Latitude of hypocenter (decimal deg)"""
    longitude: float
    """Longitude of hypocenter (decimal deg)"""
    depth: float
    """Depth of hypocenter (km)"""
    magnitude: float | None
    """JAM magnitude"""
    intensity: Literal[1, 2, 3, 4, "5L", "5H", "6L", "6H", 7]
    """Max JAM seismic intensity observed"""


class Statistics(NamedTuple):
    """Statistics of seismic intensity par :attr:`key`."""

    key: dt.datetime
    """Key of stat."""
    unit: Literal["year", "month", "date", "hour"]
    """Unit of aggregation"""
    one: int
    """Number of the station that observes JMA seismic intensity 1"""
    two: int
    """Number of the station that observes JMA seismic intensity 2"""
    three: int
    """Number of the station that observes JMA seismic intensity 3"""
    four: int
    """Number of the station that observes JMA seismic intensity 4"""
    five_L: int  # noqa: N815
    """Number of the station that observes JMA seismic intensity 5 low"""
    five_H: int  # noqa: N815
    """Number of the station that observes JMA seismic intensity 5 high"""
    six_L: int  # noqa: N815
    """Number of the station that observes JMA seismic intensity 6 low"""
    six_H: int  # noqa: N815
    """Number of the station that observes JMA seismic intensity 6 high"""
    seven: int
    """Number of the station that observes JMA seismic intensity 7"""


class StatisticsSummary(NamedTuple):
    """Summary of statistics of seismic intensity."""

    one: int
    """Number of the station that observes JMA seismic intensity 1"""
    two: int
    """Number of the station that observes JMA seismic intensity 2"""
    three: int
    """Number of the station that observes JMA seismic intensity 3"""
    four: int
    """Number of the station that observes JMA seismic intensity 4"""
    five_L: int  # noqa: N815
    """Number of the station that observes JMA seismic intensity 5 low"""
    five_H: int  # noqa: N815
    """Number of the station that observes JMA seismic intensity 5 high"""
    six_L: int  # noqa: N815
    """Number of the station that observes JMA seismic intensity 6 low"""
    six_H: int  # noqa: N815
    """Number of the station that observes JMA seismic intensity 6 high"""
    seven: int
    """Number of the station that observes JMA seismic intensity 7"""


class Intensity(NamedTuple):
    """Intensity data."""

    station_name: str
    """Name of station which observes the intensity"""
    station_number: int
    """Station number (numeric code) which observes the intensity"""
    latitude: float
    """Latitude of the station"""
    longitude: float
    """Longitude of the station"""
    intensity: Literal[1, 2, 3, 4, "5L", "5H", "6L", "6H", 7]
    """Observed JAM seismic intensity"""


class CodeResolver:
    """Resolver of prefecture/city/station code to name each other.

    We note that this fetches data from the official cite
    when calling :meth:`__init__`.
    """

    _prefecture: Final[dict[int, str]] = PREFECTURE
    _prefecture_rev: Final[dict[str, int]] = {v: k for k, v in PREFECTURE.items()}
    _city: Final[dict[int, str]]
    _city_rev: Final[dict[str, int]]
    _station: Final[dict[int, str]]
    _station_rev: Final[dict[str, int]]
    _region: Final[tuple[str]]

    def __init__(self):  # noqa: D107
        res = requests.get(CITY)
        self._city = {int(obj["code"]): obj["name"] for obj in res.json() if obj["disp"]}
        self._city_rev = {v: k for k, v in self._city.items()}

        res = requests.get(STATION)
        self._station = {int(obj["code"]): obj["name"] for obj in res.json() if obj["disp"]}
        self._station_rev = {v: k for k, v in self._station.items()}

        res = requests.get(EPICENTER)
        self._region = tuple(obj["name"] for obj in res.json())

    def prefecture_codes(self) -> tuple[int, ...]:
        """Returns all prefecture codes."""
        return tuple(self._prefecture.keys())

    def prefecture_names(self) -> tuple[str, ...]:
        """Returns all prefecture names."""
        return tuple(self._prefecture.values())

    def prefecture_name(self, code: int | str) -> str:
        """Resolve prefecture name from code.

        Args:
            code: prefecture code

        Returns:
            its prefecture name (in Japanese)
        """
        return self._prefecture[int(code)]

    def prefecture_code(self, name: str) -> int:
        """Resolve prefecture code from name.

        Args:
            name: prefecture name (in Japanese)

        Returns:
            its prefecture code
        """
        return self._prefecture_rev[name]

    def is_prefecture_code(self, code: int | str) -> bool:
        """Test `code` is valid prefecture code or not.

        Args:
            code: prefecture code

        Returns:
            :obj:`True` if `code` is valid prefecture code
        """
        return int(code) in self._prefecture

    def is_prefecture_name(self, name: str) -> bool:
        """Test `name` is valid prefecture name or not.

        Args:
            name: prefecture name

        Returns:
            :obj:`True` if `name` is valid prefecture name
        """
        return name in self._prefecture

    def city_codes(self) -> tuple[int, ...]:
        """Returns all city codes."""
        return tuple(self._city.keys())

    def city_names(self) -> tuple[str, ...]:
        """Returns all city names."""
        return tuple(self._city.values())

    def city_name(self, code: int | str) -> str:
        """Resolve city name from code.

        Args:
            code: city code

        Returns:
            its city name (in Japanese)
        """
        return self._city[int(code)]

    def city_code(self, name: str) -> int:
        """Resolve city code from name.

        Args:
            name: city name (in Japanese)

        Returns:
            its city code
        """
        return self._city_rev[name]

    def is_city_code(self, code: int | str) -> bool:
        """Test `code` is valid city code or not.

        Args:
            code: city code

        Returns:
            :obj:`True` if `code` is valid city code
        """
        return int(code) in self._city

    def is_city_name(self, name: str) -> bool:
        """Test `name` is valid city name or not.

        Args:
            name: city name

        Returns:
            :obj:`True` if `name` is valid city name
        """
        return name in self._city_rev

    def station_codes(self) -> tuple[int, ...]:
        """Returns all seismic station code."""
        return tuple(self._station.keys())

    def station_names(self) -> tuple[str, ...]:
        """Returns all seismic station names."""
        return tuple(self._station.values())

    def station_name(self, code: int | str) -> str:
        """Resolve seismic station name from code.

        Args:
            code: seismic station code

        Returns:
            its seismic station name (in Japanese)
        """
        return self._station[int(code)]

    def station_code(self, name: str) -> int:
        """Resolve seismic station code from name.

        Args:
            name: seismic station name (in Japanese)

        Returns:
            its seismic station code
        """
        return self._station_rev[name]

    def is_station_code(self, code: int | str) -> bool:
        """Test `code` is valid seismic station code or not.

        Args:
            code: seismic station code

        Returns:
            :obj:`True` if `code` is valid seismic station code
        """
        return int(code) in self._station

    def is_station_name(self, name: str) -> bool:
        """Test `name` is valid seismic station name or not.

        Args:
            name: prefecture name

        Returns:
            :obj:`True` if `name` is valid seismic station name
        """
        return name in self._station_rev

    def region_names(self) -> tuple[str]:
        """Returns all region names."""
        return self._region

    def is_region_name(self, name: str) -> bool:
        """Test `name` is valid region name or not.

        Args:
            name: region name

        Returns:
            :obj:`True` if `name` is valid region name
        """
        return name in self._region


def _parse_input_date(data: dt.datetime | dt.date | str):
    if isinstance(data, str):
        for fmt in ("%Y/%m/%d %H:%M", "%Y-%m-%d %H:%M"):
            try:
                data = dt.datetime.strptime(data, fmt)
            except ValueError:
                continue
            else:
                break
        else:
            raise ValueError(data)
    return [data.strftime("%Y-%m-%d"), data.strftime("%H:%M") if isinstance(data, dt.datetime) else "00:00"]


def _parse_input_intensity(v):
    if v == "5L":
        return "A"
    elif v == "5H":
        return "B"
    elif v == "6L":
        return "C"
    elif v == "6H":
        return "D"
    return v


def _parse_input_area(v: Sequence[tuple[float, float]]):
    return {f"boundsAr[{idx}][]": row for idx, row in enumerate(v)}


def _parse_input_sort(v: str):
    if v == "start":
        return "S0"
    elif v == "end":
        return "S1"
    elif v == "intensity":
        return "S2"
    elif v == "scale":
        return "S4"
    raise ValueError(v)


def _parse_input_window(v: str | None):
    if v is None:
        return "C0"
    elif v == "day":
        return "C1"
    elif v == "month":
        return "C2"
    elif v == "year":
        return "C3"
    raise ValueError(v)


def _parse_str_intensity(s: str) -> Literal[1, 2, 3, 4, "5L", "5H", "6L", "6H", 7]:
    if s == "震度１":
        return 1
    elif s == "震度２":
        return 2
    elif s == "震度３":
        return 3
    elif s == "震度４":
        return 4
    elif s == "震度５弱":
        return "5L"
    elif s == "震度５強":
        return "5H"
    elif s == "震度６弱":
        return "6L"
    elif s == "震度６強":
        return "6H"
    elif s == "震度７":
        return 7
    raise ValueError(s)


def _parse_earthquake(d: dict):
    dep, unit = d["dep"].split(" ")
    assert unit == "km"

    try:
        mag = float(d["mag"])
    except ValueError:
        mag = None

    return Earthquake(
        id=d["id"],
        time=dt.datetime.strptime(d["ot"], "%Y/%m/%d %H:%M:%S.%f").replace(tzinfo=dt.timezone(dt.timedelta(hours=9))),
        location=d["name"],
        # latS=d["latS"],
        # lngS=d["lonS"],
        latitude=float(d["lat"]),
        longitude=float(d["lon"]),
        depth=float(dep),
        magnitude=mag,
        intensity=_parse_str_intensity(d["maxI"]),
        # max_intensity_class=d['maxIcls'],
        # maxS=d["maxS"],
        # maxS_class=d["maxScls"],
    )


def _parse_statistics(d: dict):
    specs = (
        ("year", "%Y年"),
        ("month", "%Y/%m"),
        ("day", "%Y/%m/%d"),
        ("hour", "%Y/%m/%d %Hh"),
    )

    lb: str = d["lb"]
    for unit, fmt in specs:  # noqa: B007
        try:
            key = dt.datetime.strptime(lb, fmt).replace(tzinfo=dt.timezone(dt.timedelta(hours=9)))
        except ValueError:
            continue
        else:
            break
    else:
        raise ValueError(lb)

    return Statistics(
        key=key,
        unit=unit,
        one=int(d["S1"]) if d["S1"] else 0,
        two=int(d["S2"]) if d["S2"] else 0,
        three=int(d["S3"]) if d["S3"] else 0,
        four=int(d["S4"]) if d["S4"] else 0,
        five_L=int(d["SA"]) if d["SA"] else 0,
        five_H=int(d["SB"]) if d["SB"] else 0,
        six_L=int(d["SC"]) if d["SC"] else 0,
        six_H=int(d["SD"]) if d["SD"] else 0,
        seven=int(d["S7"]) if d["S7"] else 0,
    )


def _parse_intensity(d: dict):
    return Intensity(
        station_name=d["name"],
        station_number=int(d["code"]),
        latitude=float(d["lat"]),
        longitude=float(d["lat"]),
        intensity=_parse_str_intensity(d["int"]),
    )


if __name__ == "__main__":
    pass

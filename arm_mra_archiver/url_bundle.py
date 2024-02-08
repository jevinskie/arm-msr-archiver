from typing import Final

from attrs import define, field
from urllib3.util.url import Url


@define
class URLBundle:
    sysreg_url: Final[Url] = field()
    aarch64_url: Final[Url] = field()
    aarch32_url: Final[Url] = field()
    sysreg_url_live: bool | None = field(default=None)
    aarch64_url_live: bool | None = field(default=None)
    aarch32_url_live: bool | None = field(default=None)

from typing import Final

from attrs import define, field


@define
class URLBundle:
    sysreg_url: Final[str] = field()
    aarch64_url: Final[str] = field()
    aarch32_url: Final[str] = field()
    v8_major_version: Final[str | None] = field(default=None)
    v8_beta_version: Final[str | None] = field(default=None)
    v8_date: Final[str | None] = field(default=None)
    v9_date: Final[str | None] = field(default=None)
    sysreg_url_live: bool | None = field(default=None)
    aarch64_url_live: bool | None = field(default=None)
    aarch32_url_live: bool | None = field(default=None)

    @property
    def is_v8(self) -> bool:
        return self.v8_major_version is not None

    @property
    def is_v8_v1(self) -> bool:
        assert self.v8_date is None
        return self.v8_beta_version is not None

    @property
    def is_v8_v2(self) -> bool:
        assert self.v8_beta_version is None
        return self.v8_date is not None

    @property
    def is_v9(self) -> bool:
        return self.v9_date is not None

    @property
    def date(self) -> str | None:
        if self.v8_date is not None:
            return self.v8_date
        elif self.v9_date is not None:
            return self.v9_date
        else:
            return None

    @property
    def beta_version(self) -> str | None:
        return self.v8_beta_version

    @property
    def all_live(self) -> bool:
        return all((self.sysreg_url_live, self.aarch64_url_live, self.aarch32_url_live))

    @property
    def any_live(self) -> bool:
        return any((self.sysreg_url_live, self.aarch64_url_live, self.aarch32_url_live))

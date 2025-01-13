import logging
import typing
from functools import cached_property

import requests

from .url_bundle import URLBundle

log = logging.getLogger("arm-mra-archiver:url_checker")


class URLChecker:
    def url_is_live(self, url: str) -> bool:
        try:
            resp = self.session.head(url)
        except requests.RequestException as e:
            log.exception(f"Got exception requesting HEAD on {url}.", exc_info=e)
            return False
        requests.status_codes.codes.ok = typing.cast(int, requests.status_codes.codes.ok)
        return resp.status_code == requests.status_codes.codes.ok

    @cached_property
    def session(self) -> requests.Session:
        return requests.Session()


def get_live_urls(url_bundles: tuple[URLBundle, ...]) -> tuple[URLBundle, ...]:
    chk = URLChecker()
    for bndl in url_bundles:
        bndl.sysreg_url_live = chk.url_is_live(bndl.sysreg_url)
        bndl.aarch64_url_live = chk.url_is_live(bndl.aarch64_url)
        bndl.aarch32_url_live = chk.url_is_live(bndl.aarch32_url)

    return tuple(filter(lambda b: b.any_live, url_bundles))

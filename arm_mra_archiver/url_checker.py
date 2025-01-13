import asyncio
import logging
import time
import typing
from functools import cached_property

import aiohttp
import attrs
import requests
from tqdm.asyncio import tqdm_asyncio

from .url_bundle import URLBundle

log = logging.getLogger("arm-mra-archiver:url_checker")


@attrs.define(auto_attribs=True)
class URLCheckerAsync:
    concurrency: int = 4
    timeout: int | None = None
    session: aiohttp.ClientSession | None = None
    semaphore: asyncio.Semaphore = attrs.field(init=False)

    def __attrs_post_init__(self) -> None:
        self.semaphore = asyncio.Semaphore(self.concurrency)
        if self.timeout is None:
            self.timeout = 60

    async def create_session(self) -> None:
        """Create a shared session."""
        if self.session is not None:
            raise ValueError(f"create_session() self.session is None self: {self}")
        self.session = aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(limit=self.concurrency), timeout=aiohttp.ClientTimeout(total=self.timeout)
        )

    async def close_session(self) -> None:
        """Close the shared session."""
        if self.session is None:
            raise ValueError(f"close_session() self.session is not None self: {self}")
        await self.session.close()

    async def check_url_liveness(self, url: str) -> bool:
        """Check if a URL is live using the shared session."""
        async with self.semaphore:
            if self.session is None:
                raise ValueError("check_url_liveness() session is None")
            async with self.session.head(url) as response:
                print(f"url: {url} response: {response}")
                time.sleep(0.1)
                return response.status == 200

    async def check_urls_liveness(self, urls: list[str]) -> list[bool]:
        """Check liveness of multiple URLs."""
        tasks = [self.check_url_liveness(url) for url in urls]
        return await tqdm_asyncio.gather(*tasks)


class URLCheckerSync:
    def __init__(self, concurrency: int = 100, timeout: int | None = None):
        self.checker = URLCheckerAsync(concurrency=concurrency, timeout=timeout)

    async def _check_urls_async(self, urls: list[str]) -> list[bool]:
        """Internal method to handle async operations."""
        await self.checker.create_session()
        try:
            return await self.checker.check_urls_liveness(urls)
        finally:
            await self.checker.close_session()

    def check_urls(self, urls: list[str]) -> list[bool]:
        """Synchronously check liveness of a list of URLs."""
        return asyncio.run(self._check_urls_async(urls))


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
    # chk = URLChecker()
    urls: set[str] = set()
    for bndl in url_bundles:
        urls.update((bndl.sysreg_url, bndl.aarch64_url, bndl.aarch32_url))

    urls_list: list[str] = list(urls)
    chk2 = URLCheckerSync()
    urls_live_list: list[bool] = chk2.check_urls(urls_list)
    print(f"any(urls_live_list) = {any(urls_live_list)}")
    urls_live: dict[str, bool] = dict(zip(urls_list, urls_live_list))

    for bndl in url_bundles:
        bndl.sysreg_url_live = urls_live[bndl.sysreg_url]
        bndl.aarch64_url_live = urls_live[bndl.aarch64_url]
        bndl.aarch32_url_live = urls_live[bndl.aarch32_url]

    return tuple(filter(lambda b: b.any_live, url_bundles))

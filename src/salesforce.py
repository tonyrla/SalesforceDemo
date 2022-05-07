from datetime import timedelta
from functools import wraps
import os
from pathlib import Path
from typing import Any, Dict, List
from typing import Callable
from assertionengine import AssertionOperator

from robot.libraries.BuiltIn import BuiltIn
from robot.libraries.BuiltIn import RobotNotRunningError
from Browser import Browser, ElementState

import pyotp

class Utils:
    __slots__ = "get_ununsed_filename"
    @staticmethod
    def get_unused_filename(target_path: Path|str) -> Path:
        target_path = Path(target_path)
        resolved_path = target_path.resolve()
        if resolved_path.exists():
            try:
                part = resolved_path.name.rpartition("_")
                count = int(part[2].rpartition(".")[0])
                filename = resolved_path.parent / (part[0] + "_" + str(count + 1) + resolved_path.suffix)
            except ValueError:
                count = 1
                filename = resolved_path.parent / (resolved_path.stem + "_1" + resolved_path.suffix)
                part = filename.name.rpartition("_")
                count = int(part[2].rpartition(".")[0])
            while filename.exists():
                count = count + 1
                filename = resolved_path.parent / str(part[0] + "_" + str(count) + resolved_path.suffix)
        else:
            return resolved_path
        return filename


class Salesforce:
    __slots__ = ("username", "loginpage", "browser", "_testname", "_otp")
    def __init__(self, username: str):
        self.username = username
        self.loginpage = "https://nan3.my.salesforce.com/"
        self.browser = Browser(enable_presenter_mode=True)
        self.browser.new_browser(headless=False,slowMo=timedelta(milliseconds=100))
        self._otp = pyotp.TOTP(os.getenv("TOPT", ""))
        try:
            self._testname = BuiltIn().get_variable_value("${TEST NAME}")
        except RobotNotRunningError:
            self._testname = "python"

    def _screenshotter(func: Callable[..., Any]):  # type: ignore
        # Underscore to prevent keyword creation instead of having to list everything in __all__ or using @not_keyword
        @wraps(func)
        def wrapper(*args: List[Any], **kwargs: Dict[str, Any]):
            instance = args[0]
            folder: str = instance._testname

            try:
                func(*args, **kwargs)
            except Exception:
                filename = Utils.get_unused_filename(Path(f"artifacts/{folder}/{func.__name__}_FAIL.png")).resolve().__str__()
                instance.browser.take_screenshot(filename=filename)
                raise
            
            filename = Utils.get_unused_filename(Path(f"artifacts/{folder}/{func.__name__}.png")).resolve().__str__()
            instance.browser.take_screenshot(filename=filename)
        return wrapper

    @_screenshotter  # type: ignore
    def login(self, password: str):
        # Basicauth
        self.browser.new_page()
        self.browser.go_to(self.loginpage)
        self.browser.fill_text('input[name="username"]', self.username)
        self.browser.fill_secret('input[name="pw"]', password)
        self.browser.click('input[name="Login"]')

        # OTP
        #wait for navi? url="/https:\/\/nan3.my.salesforce.com\/_ui\/identity\/verification\/.+?/i") 
        self.browser.wait_for_elements_state('//*[@id="tc"]', state=ElementState.stable)
        self.browser.fill_text('//*[@id="tc"]', self._otp.now())  # //*[@id="tc"]
        self.browser.click('//*[@id="save"]')  # //*[@id="save"]

        self.browser.wait_for_navigation(url="https://nan3.lightning.force.com/lightning/page/home")
        self.browser.wait_until_network_is_idle()

    @_screenshotter  # type: ignore
    def open_new_lead(self):
        self.browser.click('.oneAppNavContainer >> a[role="button"]:has-text("Leads Menu")')
        self.browser.click('.oneAppNavContainer >> one-app-nav-bar-item-dropdown >> text=New Lead')
        self.browser.wait_for_elements_state("css=.inlinePanel", state=ElementState.stable)
        self.browser.wait_until_network_is_idle()

    @_screenshotter  # type: ignore
    def selectoption(self, target: str, value: str):       
        self.browser.click(f'.inlinePanel >> lightning-combobox:has-text("{target.title()}")')
        self.browser.click(f'lightning-picklist >> lightning-base-combobox-item >> "{value.title()}"')

    @_screenshotter  # type: ignore
    def fill_name(self, firstname: str, lastname: str):
        self.browser.fill_text('.inlinePanel >> input[name="firstName"]', firstname.title())
        self.browser.fill_text('.inlinePanel >> input[name="lastName"]', lastname.title())  # MacTavish just has to be Mactavish from now on.

    @_screenshotter  # type: ignore
    def fill_company(self, company_name: str):
        self.browser.fill_text('.inlinePanel >> input[name="Company"]', company_name)

    @_screenshotter  # type: ignore
    def fill_email(self, email: str):
        self.browser.fill_text('.inlinePanel >> input[name="Email"]', email)

    @_screenshotter  # type: ignore
    def save_lead(self):
        self.browser.click('.inlinePanel >> button[name="SaveEdit"]')
        self.browser.wait_until_network_is_idle()

    @_screenshotter  # type: ignore
    def browse_to_leads(self):
        self.browser.click('.oneAppNavContainer >> a[title="Leads"]')
        self.browser.wait_until_network_is_idle()

    @_screenshotter  # type: ignore
    def remove_lead(self, name: str):
        self.browser.click(f'tr:has-text("{name}") >> a[role="button"]') # f'.uiScroller >> .forceRecordLayout >> tr:has-text("{name}") >> a[role="button"]'
        self.browser.click('a[role="menuitem"]:has-text("Delete")')
        self.browser.wait_for_elements_state('button[title="Delete"]', ElementState.stable)
        self.browser.click('button[title="Delete"]')
        self.browser.wait_for_elements_state(f'tr:has-text("{name}") >> a[role="button"]', ElementState.detached)
        self.browser.wait_until_network_is_idle()

    def __exit__(self):
        self.browser.close_browser()

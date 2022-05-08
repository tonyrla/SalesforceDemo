from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict, List, Optional, Tuple

def get_unused_filename(target_path: Path|str) -> Path:
    def get_count(part: Tuple[str,str,str]) -> int:
        return int(part[2].rpartition(".")[0])

    def get_new_filepath(path: Path, partition: Tuple[str,str,str]|None, fileindex: int = 1):
        if partition:
            return path.parent / str(partition[0] + "_" + str(fileindex) + path.suffix)
        else:
            return path.parent / (path.stem + "_1" + path.suffix)

    resolved_path = Path(target_path).resolve()
    if resolved_path.exists():
        count = 1
        try:
            part = resolved_path.name.rpartition("_")
            count = get_count(part)
            filename = get_new_filepath(path=resolved_path, partition = part, fileindex=count + 1)
        except ValueError:
            filename = get_new_filepath(path=resolved_path, partition=None)
            part = filename.name.rpartition("_")
        while filename.exists():
            count += 1
            filename = get_new_filepath(path=resolved_path, partition=part, fileindex=count)
    else:
        return resolved_path
    return filename


@dataclass(slots=True, frozen=True)
class LOCATORS:
    """
    SimpleNamespace can be initialized from a dict as well. 
    If for some odd reason locators need to be configurable on launch time, instead of hardcoding,
    or just to separate them from python / rfw

    ie.
        { "username_field" : "//input[@id=\"username\"]", subnamespace : {"tunnus":"JohnDoe"}} >> testi.json

        import json

        def convert_dict(json_port):
            return SimpleNamespace(**json_port)

        with open('testi.json') as f:
            login = json.load(f,object_hook=convert_dict)

        browser.fill_text(login.username_field, login.subnamespace.tunnus)
    """
    login = SimpleNamespace()
    login.username_field = '//input[@id="username"]'
    login.password_field = '//input[@id="password"]'
    login.login_button = '//input[@id="Login"]'
    login.topt_key = '//input[@id="tc"]'
    login.topt_login_button = '//input[@id="save"]'

    mainpage = SimpleNamespace()
    mainpage.leads_menu = '.oneAppNavContainer >> a[role="button"]:has-text("Leads Menu")'
    mainpage.leads_menu_new_lead = '.oneAppNavContainer >> one-app-nav-bar-item-dropdown >> text=New Lead'
    mainpage.leads_button = '.oneAppNavContainer >> a[title="Leads"]'

    newlead_modal = SimpleNamespace()
    newlead_modal.panel = 'css=.inlinePanel'
    newlead_modal.first_name = '.inlinePanel >> input[name="firstName"]'
    newlead_modal.last_name = '.inlinePanel >> input[name="lastName"]'
    newlead_modal.company = '.inlinePanel >> input[name="Company"]'
    newlead_modal.email = '.inlinePanel >> input[name="Email"]'
    newlead_modal.save_button = '.inlinePanel >> button[name="SaveEdit"]'
    newlead_modal.selectoption_title = '.inlinePanel >> lightning-combobox:has-text("{}")'
    newlead_modal.selectoption_value = 'lightning-picklist >> lightning-base-combobox-item >> "{}"'
    
    leads = SimpleNamespace()
    leads.menu_delete_button = 'a[role="menuitem"]:has-text("Delete")'
    leads.popup_delete_button = 'button[title="Delete"]'
    leads.named_row_menubutton = 'tr:has-text("{}") >> a[role="button"]'

    testi = SimpleNamespace()
    testi.testi_a = 'tr:has-text("{}") >> a[role="button"]'
    testi.testi_b = 'tr:has-text("{NAME}") >> a[role="button"]'
    testi.testi_c = 'Onko tämä {} ensimmäinen, {} vai {}?'
    

    @staticmethod
    def replace_placeholder(locator: str, *values: Any, **kwargs: Any) -> str:
        """
        LOCATORS.replace_placeholder('Onko tämä {} eka, {} vai {}?', "kohde","toka","kolmas")
        LOCATORS.replace_placeholder('Hei {NAME}!', NAME="maailma")
        """
        if len(values)>0:
            try:
                count = 0
                while locator.index("{}"):
                    locator = locator.replace('{}', values[count],1)
                    count = count if len(values)-1 <= count else count + 1
            except ValueError:
                return locator
        else:
            for key, value in kwargs.items():
                placeholder = "{"+key+"}"
                locator = locator.replace(placeholder, value)
        return locator

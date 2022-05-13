*** Settings ***
Library              src.salesforce.Salesforce  username=rintala.tony-vttz@force.com
Library              OperatingSystem

Suite Setup          Clear Artifacts

*** Variables ***
${FIRSTNAME}=          Tony
${LASTNAME}=           Rintala
${COMPANY}=            Siwa
${EMAIL}=              tony.rintala@hok.fi
${LEADSTATUS}=         Qualified
${SALUTATION}=         Mr.


*** Test Cases ***
Create Lead
    Login              $PASSWORD
    Open New Lead
    SelectOption       Lead Status  ${LEADSTATUS}
    SelectOption       Salutation  ${SALUTATION}
    Fill Name          ${FIRSTNAME}  ${LASTNAME}
    Fill Company       ${COMPANY}
    Fill Email         ${EMAIL}
    Save Lead

Remove Lead
    Login              $PASSWORD
    Browse To Leads
    Remove Lead        ${FIRSTNAME} ${LASTNAME}  ${COMPANY}  ${EMAIL}

*** Keywords ***
Clear Artifacts
    Empty Directory    ./Artifacts/
    Empty Directory    ./browser/

# No suite-wide login here because library scope is left as "Test" to achieve the fancy artifacts structure without library gymnastics
# I'd preferred to use Playwright python library, instead of RFW-Browser, but the scope doesn't allow non-async due to async event loop

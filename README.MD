# Requirements for Demo
``` 
python -m pip install requirements.txt 
rfbrowser init
```
If you do not have nodejs installed, rfbrowser init will provide you with instructions.

Environment variable TOTP with your TOTP secret.

## Running the robot
* Ensure you have your TOTP secret string set to environment variables
``` python -m robot.run -L Trace --variable PASSWORD:YourPasswordGoesHere --variable USERNAME:YourUsernamegoeshere .\tests\CreateAndRemoveLead.robot ```

## Testing locators
``` npx playwright open https://nan3.my.salesforce.com/ ``` 
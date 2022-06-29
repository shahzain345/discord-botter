import twocaptcha
import httpx
from .utility import Utility, MPrint
console = MPrint()


class Captcha:
    def __init__(self):
        self._client = httpx.Client()
        self._utils = Utility()
        self.api = self._utils.config["captcha"]["api"]
        self.key = self._utils.config["captcha"]["key"]

    def getBalance(self):
        if self.api == "2captcha.com":
            captcha = twocaptcha.TwoCaptcha(self.key)
            return captcha.balance()

    def getCaptcha(self):
        if self.api == "2captcha.com":
            captcha = twocaptcha.TwoCaptcha(self.key)
            token = captcha.hcaptcha(
                "4c672d35-0701-42b2-88c3-78380b0db560", "https://discord.com")["code"]
            console.s_print(f"Got hCaptcha: {token[:32]}")
            return token
        elif self.api == "anti-captcha.com" or self.api == "capmonster.cloud":
            taskId = self._client.post(f"https://api.{self.api}/createTask", json={"clientKey": self.key, "task": {"type": "HCaptchaTaskProxyless", "websiteURL": "https://discord.com/",
                                                                                                                   "websiteKey": "4c672d35-0701-42b2-88c3-78380b0db560", "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Safari/605.1.15"}}, timeout=30).json()
            if taskId.get("errorId") > 0:
                console.f_print(
                    f"Captcha(createTask) - {taskId.get('errorDescription')}")
                return None
            taskId = taskId.get("taskId")

            while not solvedCaptcha:
                captchaData = self._client.post(f"https://api.{self.api}/getTaskResult", json={
                    "clientKey": self.key, "taskId": taskId}, timeout=30).json()
                if captchaData["errorId"] > 0:
                    console.f_print(
                        f"Captcha(getTaskResult) - {captchaData['errorDescription']}")
                    return None
                if captchaData.get("status") == "ready":
                    solvedCaptcha = captchaData.get(
                        "solution").get("gRecaptchaResponse")
                    console.s_print(f"Got hCaptcha: {solvedCaptcha[:32]}")
                    return solvedCaptcha

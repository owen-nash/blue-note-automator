import os
import json

# Your raw cookie string
raw_cookie = """LOGIN_INFO=AFmmF2swRgIhAMIC6pz3TLP0bbma510LXFTk5b5Hwe8nqCE4gxHBBAHBAiEAp536v1epobpXD1XZ5I57jcLvG0hNuS3olb_15xmu_iI:QUQ3MjNmelQ3aTB3bU5IRlhBNFRDdEZtVXp5YlY2aVpxam0zYjdmQjU2TG02WXQ3TTNkRHFaUFY0S3JSd29jRGY5Uk1Qck5wLWN2eWVJalJkNUowejVKOFZvTFUxYjRLOHZraHRWSXJZeGU2b3FLOGpzcUFOSmJLUmtQbEw2bHdOektOTndTcHVxZll4SzZaR0xIX0FJdjREZzlfYTRiSC13; VISITOR_INFO1_LIVE=9sDHPs1HJqo; VISITOR_PRIVACY_METADATA=CgJVUxIEGgAgFA%3D%3D; __Secure-1PSIDTS=sidts-CjUBBj1CYuT8JLRcFoLkxY4bt1Piyz3YUtcABfr8xLbS2ZR1ka8FFomqa3WSZyhKQAnKNXZxxBAA; __Secure-3PSIDTS=sidts-CjUBBj1CYuT8JLRcFoLkxY4bt1Piyz3YUtcABfr8xLbS2ZR1ka8FFomqa3WSZyhKQAnKNXZxxBAA; HSID=Av5NphYwDZyFio4cA; SSID=ARrmRVkSvOwmTzDlr; APISID=dY_bZLhxclfp7DSn/AtfiN1rPvLfA6df7V; SAPISID=-9-2jENk0hvKtVZs/A1Zlxgg8a3h363kII; __Secure-1PAPISID=-9-2jENk0hvKtVZs/A1Zlxgg8a3h363kII; __Secure-3PAPISID=-9-2jENk0hvKtVZs/A1Zlxgg8a3h363kII; __Secure-BUCKET=CMIB; YSC=YnKpDQO36g0; SID=g.a0008whQ4jHXhz-tVUNMzW7PVop2dEfLbA2dDmBi4GXRxlUWejIjpOJRvvQEvcGONOoRGs8kngACgYKAegSARMSFQHGX2MinLXD0TZ9RJudnPbG50at1BoVAUF8yKrAI6rcOWb-xSIdGSBkKnMQ0076; __Secure-1PSID=g.a0008whQ4jHXhz-tVUNMzW7PVop2dEfLbA2dDmBi4GXRxlUWejIjsxl4n3a6Z97dW2Ww1zmyfgACgYKAdcSARMSFQHGX2MiU6pgUefnwee4bUHgAAnipRoVAUF8yKrXbjgE51dbBjvIM4Lpa8aI0076; __Secure-3PSID=g.a0008whQ4jHXhz-tVUNMzW7PVop2dEfLbA2dDmBi4GXRxlUWejIjuSovAxTuFy5_gcmG1zKzeQACgYKAZoSARMSFQHGX2MimdX-okg7Qpu5LoAbd9vOoRoVAUF8yKruuymrQXeBZujT75ZjuEV_0076; __Secure-YNID=17.YT=LhPNRBd93JQXWD6WWzwKQTk-IYv3vY9ur8ChfsA6BSK35IgQE_VrbkpHYKWpiZrQ7X9mdXRLeHPtDYVilUSHPqlRqG4gYcSy4YjFAFpfjI_WyaBJeYq_xnZK_FdcpKz_jozaa6TVUd0SpXXQ93Q-8wp95nJVqEJ67VSkslnswx2ezP5erWjnLgFhQ-Ddm80RnlxCAhXxPWaagQZw9M0HoNhnWLogaRxt-AXx6Srh3noWBrbANgeIDJESrb4XqbT7lXodykKh-yu4wbRN80e-G5aE8WtQIWyoynhe0LTbk4qf_QHBQOlv0uVN0owGre6B17V-AmYndtEoWT_VN8VesQ; __Secure-ROLLOUT_TOKEN=CKaJjfT6q6L4YhCa1o6aicuRAxiG56vCloyUAw%3D%3D; _gcl_au=1.1.1755121254.1777229153; PREF=f6=40000080&f4=4000000&tz=America.Detroit&f7=100&repeat=NONE; SIDCC=AKEyXzW4SWpADuaGCnXoh_ZvcWnDQOWkz30pRZA2x1nOKtmg3YH0M-dbPpliZt57I3qJaN9b; __Secure-1PSIDCC=AKEyXzX_07caBN9usIih-_urZfbnGfEA0FQVnSrb0ROmssRfs_TzbGeUOS4putR87F5dsx_uwQ; __Secure-3PSIDCC=AKEyXzV-9j1I9g_vVVS22TSzCUFbGqH0SIsBbNVjtH4mUjfUAP7E4WjIs4d_sWQa5lHsEC_7qg"""

# Netscape format for spotdl (yt-dlp)
def save_cookies():
    cookie_path = "/home/ownash/blue-note-automator/yt_cookies.txt"
    with open(cookie_path, "w") as f:
        f.write("# Netscape HTTP Cookie File\n")
        # For simplicity, we'll try to use the raw string with --cookie-string in spotdl if possible,
        # but a file is better.
        # Actually, spotdl can take a raw string or a file.
        # Let's just store the raw string for now as it's what we have.
        f.write(raw_cookie)
    print(f"Cookies saved to {cookie_path}")

if __name__ == "__main__":
    save_cookies()

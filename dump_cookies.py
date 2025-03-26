import browsercookie
import json

cj = browsercookie.chrome()
target_domain = "bestbuy.com"
cookies_dict = {cookie.name: cookie.value for cookie in cj if target_domain in cookie.domain}
with open('bestbuy_cookies.json', 'w') as f:
    json.dump(cookies_dict, f, indent=4)

cj = browsercookie.chrome()
target_domain = "amazon.com"
cookies_dict = {cookie.name: cookie.value for cookie in cj if target_domain in cookie.domain}
with open('amazon_cookies.json', 'w') as f:
    json.dump(cookies_dict, f, indent=4)
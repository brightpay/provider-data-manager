import requests

def make_request(url, api_key=None, params=None, method='GET', data=None, headers=None, add_auth_header=False, add_xtoken_header=False):
        default_headers = {
            'Content-Type': 'application/json',
            'accept': 'application/json, text/plain, */*',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'
        }
        
        if add_auth_header and headers:
            headers['authorization'] = f'Bearer {api_key}'
        elif add_auth_header:
            default_headers['authorization'] = f'Bearer {api_key}'

        if add_xtoken_header and headers:
            headers['Xauthtoken'] = api_key
        elif add_xtoken_header:
            default_headers['Xauthtoken'] = api_key
        
        if headers:
            default_headers.update(headers)

        print(f"Making {method} request to {url}")
        print(f"Request headers: {default_headers}")
        
        if method == 'GET':
            response = requests.get(url, headers=default_headers, params=params)
        elif method == 'POST':
            response = requests.post(url, headers=default_headers, json=data)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        print(f"Response status code: {response.status_code}")
        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            print(f"Request to {url} failed with status code {response.status_code}")
            print(f"Response content: {response.content.decode()}")
            raise e
        
        return response.json()
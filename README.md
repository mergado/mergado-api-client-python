# Mergado API Python Client

- [Mergado Apps Docs](http://mergado.github.io/docs/)
- [API docs](http://docs.mergado.apiary.io/)

## Usage

```python

from mergadoapiclient import client

# Prepare config with a OAuth2 credentials.
credentials = {
    'client_id': '<client ID>',
    'client_secret': '<client secret key>',
    'grant_type': 'client_credentials',
    'token_uri': 'https://app.mergado.com/oauth2/token/',  # optional
    'api_uri': 'https://api.mergado.com/',  # optional
    'storage_class': 'yourapp.models.TokenStorage',  # optional
}

# Build API client instance.
api = client.build(credentials)

# Get an Eshop with ID = 1.
api.get('shops/1')
```

import requests
import pytest

url = 'http://127.0.0.1:8081'

#@pytest.mark.parametrize()
def test_GETRequest_StatusPagePresent():
    response = requests.get(f'{url}/status')
    assert response.status_code == 200
    assert response.content is not None

def test_POSTRequest_CheckHeaderInserted():
    data = {'some': 'data'}
    response = requests.post(f'{url}', json=data)
    assert response.status_code == 200
    assert 'x-my-jwt' in response.headers
import requests

users_camila = []

with open('usuarios_camila.txt', 'r') as f:
    users_camila = f.readlines()

for user in users_camila:
    response = requests.get(f'https://instagram.com/{user.strip()}')
    if (response.status_code == 404):
        print(user)
    
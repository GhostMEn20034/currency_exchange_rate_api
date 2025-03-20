# Currency Exchange Rate API

# Features Implemented:

- [x] Users
    - [x] User Signup
- [x] Balance
    - [x] Ability to view balance
- [x] Currency Exchange
    - [x] Ability to request exchange rate of specific currency to UAH (Ukrainian Hryvnia)
    - [x] Ability to see the history of exchange rate requests

# Setup

**Note that the setup assumes you are using any Linux distribution**

### 1. Clone the project:
```shell
git clone https://github.com/GhostMEn20034/currency_exchange_rate_api.git
```
### 2. Change permissions for `init-database.sh`:
```shell
chmod 755 init-database.sh
```
### 3. Create a `.env` file, using the following command:
```shell
touch .env
```
### 4. Open the file created above in whatever editor you want
### 5. Insert the next variables (Don't forget to remove comments):
```shell
SECRET_KEY=secret_key # Django secret key, you can generate it on https://djecrety.ir/
DEBUG=1 # Or 0, 1 required for Swagger Docs
JWT_SIGNING_KEY=sign_key # Key used to sign JWT tokens, you can generate it on https://jwtsecret.com/generate 
ALLOWED_HOSTS=localhost,127.0.0.1,[::1]
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
SQL_ENGINE=django.db.backends.postgresql
SQL_DATABASE=your_db 
SQL_USER=your_db_user
SQL_PASSWORD=your_db_user_password
SQL_HOST=db
SQL_PORT=5432
SUPER_USER_PWD=your_postgres_user_passsword
EXCHANGE_RATE_API_KEY=api_key # API key for ExchangeRate-API, you can get one on: https://www.exchangerate-api.com/
```
Example to copy:
```shell
SECRET_KEY=^yrtqrr)%k3!3x8bed6$$m$tx+(-g=m7)8htmyrmae%54&m_wf
DEBUG=1
JWT_SIGNING_KEY=cb2d9b1f5e642b8737584ab96b5aa378f168d168d8f7df6c13bfe6facc3083d4982c536856ba4418cc0ba5af53646198d46d2ffc2110f1ad0cbc0444ad6a45061c94cbb1b4bddbce622e37dc2f0cda2bcb83b40779506077fda40fda44ad571a6dede4bf8cac2f31436f7184ca5a6d080925674f7c275ac0e6c92df2c0b5c69b
ALLOWED_HOSTS=localhost,127.0.0.1,[::1]
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
SQL_ENGINE=django.db.backends.postgresql
SQL_DATABASE=exchange_rate_api
SQL_USER=exchange_rate_api_usr
SQL_PASSWORD=xxxx1234
SQL_HOST=db
SQL_PORT=5432
SUPER_USER_PWD=xxxx4321
EXCHANGE_RATE_API_KEY=your_api_key
```
# Running the App In Development Mode
### 1. Make sure you are in the root project directory and the `.env` file is populated.
### 2. Use the following command to run the app:
```shell
docker compose -f docker-compose-dev.yml up -d --build
```
### 3. Go to [localhost:8000/docs](http://localhost:8000/docs) to see interactive documentation
### 4. To be able to send requests to protected routes (Require authentication) inside the swagger ui, you need to get access token using `/api/v1/auth/token/` route, and paste it in authorization menu (Top Right Corner of the screen)
# Running the App In Production Mode
### 1. Make sure you are in the root project directory and the `.env` file is populated.
### 2. Use the following command to run the app:
```shell
docker compose -f docker-compose-prod.yml up -d --build
```
### 3. [localhost/](http://localhost/) is a base url (Swagger UI is disabled in production mode)
# Running integration tests
### 1. Make sure you are in the root project directory.
### 2. Create env file with the name `.env.test`:
```shell
touch .env.test
```
### 3. Open the file in any editor and paste variables:
```shell
SECRET_KEY=^yrtqrr)%k3!3x8bed6$$m$tx+(-g=m7)8htmyrmae%54&m_wf
DEBUG=1
JWT_SIGNING_KEY=cb2d9b1f5e642b8737584ab96b5aa378f168d168d8f7df6c13bfe6facc3083d4982c536856ba4418cc0ba5af53646198d46d2ffc2110f1ad0cbc0444ad6a45061c94cbb1b4bddbce622e37dc2f0cda2bcb83b40779506077fda40fda44ad571a6dede4bf8cac2f31436f7184ca5a6d080925674f7c275ac0e6c92df2c0b5c69b
ALLOWED_HOSTS=localhost,127.0.0.1,[::1]
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
SQL_ENGINE=django.db.backends.postgresql
SQL_DATABASE=exchange_rate_api
SQL_USER=exchange_rate_api_usr
SQL_PASSWORD=xxxx1234
SQL_HOST=db
SQL_PORT=5432
SUPER_USER_PWD=xxxx4321
```
### 4. Use the following command to run integration tests:
```shell
 docker compose -f docker-compose-test.yml --env-file .env.test up --build
```
### 5. After tests are completed, press `Ctrl + C` to shut down test containers
### 6. Delete Compose Project by the command:
```shell
docker compose -f docker-compose-test.yml down
```
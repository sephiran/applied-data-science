# Dockerfile
FROM python:3.9

# install requirements
COPY database-operations/docker/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# copy csv data
COPY . .
COPY ./data/airbnb_rental_prices_combined.csv /app/data/airbnb_rental_prices_combined.csv

# set working directory
WORKDIR /app

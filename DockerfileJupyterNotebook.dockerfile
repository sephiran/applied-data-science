# Dockerfile
FROM jupyter/base-notebook:latest

# install requirements
USER root
RUN apt-get update
RUN apt-get install -y gdal-data
RUN apt-get install -y gdal-bin
RUN apt-get install -y libgdal-dev
RUN apt-get install -y python3-gdal
RUN apt-get install -y g++

USER jovyan
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt -U

COPY airbnb-scraping /home/jovyan/jupyter_data/airbnb-scraping/
COPY data /home/jovyan/jupyter_data/data/
COPY database-operations /home/jovyan/jupyter_data/database-operations/
COPY eda /home/jovyan/jupyter_data/eda/
COPY nlp /home/jovyan/jupyter_data/nlp/
COPY rental-prices /home/jovyan/jupyter_data/rental-prices/
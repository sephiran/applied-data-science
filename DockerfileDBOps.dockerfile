# Dockerfile
FROM python:3.9

# install requirements
RUN pip install --no-cache-dir psycopg2-binary sqlalchemy pandas -U

COPY data /home/jovyan/jupyter_data/data/
COPY database-operations/dbops.py /home/jovyan/jupyter_data/database-operations/

CMD ["python", "/home/jovyan/jupyter_data/database-operations/dbops.py"] 
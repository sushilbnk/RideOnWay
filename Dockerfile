FROM python:3
RUN pip install django==3.2
RUN pip install whitenoise
Run pip install mysqlclient
COPY . .
RUN python3 manage.py migrate
CMD ["python3","manage.py","runserver","0.0.0.0:8000"]

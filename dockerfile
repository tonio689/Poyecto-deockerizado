FROM python:3.8  
ENV PYTHONBUFFERED=1 
WORKDIR /app 


COPY requirments.txt /app/requirments.txt  

RUN pip install -r requirments.txt 
COPY . /app   

CMD python3 manage.py runserver 0.0.0.0:80


FROM python

WORKDIR /app

EXPOSE 81 

COPY Pipfile Pipfile.lock ./


RUN pip install pipenv
RUN pipenv requirements > requirements.txt
RUN pip install -r requirements.txt

COPY . ./

CMD ["python", "app.py"]

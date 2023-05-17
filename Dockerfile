FROM python

WORKDIR /app

EXPOSE 81 

COPY requirements.txt ./

RUN pip install pipenv
RUN pip install -r requirements.txt

COPY . ./

CMD ["python", "app.py"]

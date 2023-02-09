FROM python:3.9.12
WORKDIR /app
COPY ./ /app/
RUN pip install --trusted-host mirrors.aliyun.com -i http://mirrors.aliyun.com/pypi/simple/ -r requirements.txt
EXPOSE 5000
#RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt
CMD ["python", "/app/ReedCalendar.py"]

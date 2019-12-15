
FROM python:3.6.9

COPY requirements.txt ./
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# RUN cd zatt && python3 setup.py install
# RUN ["chmod", "+x", "run_zatt_servers.sh"]
# RUN nohup bash -c "./run_zatt_servers.sh &" 

CMD ["python3", "./server.py"]
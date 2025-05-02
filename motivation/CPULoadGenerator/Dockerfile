FROM registry.cn-hangzhou.aliyuncs.com/tobirexxy/registry:centos9

RUN pip install redis -i https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip install matplotlib -i  https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip install psutil -i  https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip install twisted -i  https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip install click -i https://pypi.tuna.tsinghua.edu.cn/simple

RUN pip install numpy 
RUN  git clone https://github.com/SheepHuan/CPULoadGenerator.git --branch centos9-python3

RUN  cd CPULoadGenerator && virtualenv --python=python3.9 ./venv && . venv/bin/activate 

COPY ./worker.py /CPULoadGenerator/worker.py
COPY ./rediswq.py /CPULoadGenerator/rediswq.py
COPY ./topo_explorer.py /CPULoadGenerator/topo_explorer.py

CMD cd CPULoadGenerator && virtualenv --python=python3.9 ./venv && . venv/bin/activate && pip install numpy && pip install twisted && pip install psutil && pip install matplotlib &&  pip install click && python ./topo_explorer.py

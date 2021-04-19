from func import *
from metrics import *
from params import *
import os, subprocess


# original conf file copy
init_config = ""

# readline_all.py
f = open("init_config.conf", 'r')
while True:
    line = f.readline()
    if not line: break
    init_config += line
f.close()


config_list = [init_config for _ in range(count_file)]

for i in range(count_file):
    params_dict = {}
    params_dict = determine_dict(params_aof,params_rdb, params_activedefrag, 
                                params_etc, params_dict)
    # print(f"i={i}\n params_dict={params_dict}\n")
    config_list[i] = config_generator(config_list[i], random_choice(params_dict))
    # config_list[i] += "\nlogfile "+"'./logfile/logfile"+"%s'" %index_size(i)
    

# conf file generate step
for i in range(count_file):
    index = range(range_start, range_end)
    file_generator("config" + str(index[i]), './configfile/',config_list[i], "conf")

result_external = []  
result_internal = []


for i in range(range_start, range_end):
    #redis 서버 실행
    os.system("/home/jieun/redis-5.0.2/src/redis-server "+"configfile/config"+str(i)+".conf")

    # memtier_benchmark 실행
    cmd = ['/home/jieun/memtier_benchmark/memtier_benchmark', '--request=1000000', '--clients=1', '--thread=1', '--data-size=128', '--key-minimum=10000000', '--key-maximum=99999999', '--ratio=1:0']
    fd_popen = subprocess.Popen(cmd, stdout=subprocess.PIPE).stdout  

    external_data = []
    for j in range(13):
        data = fd_popen.readline() 
        if j >= 9:
            external_data.append(data)

    external_list = ExternalMetrics_IntoList(external_data)
    result_external.append(external_list)

    # # 캐시 비우기
    cmd = ['sudo', 'echo', '3', '>', '/proc/sys/vm/drop_caches']
    fd_popen = subprocess.Popen(cmd, stdout=subprocess.PIPE).stdout  

    # "redis-cli info" excute
    cmd = ['/home/jieun/redis-5.0.2/src/redis-cli', 'info'] 
    fd_popen = subprocess.Popen(cmd, stdout=subprocess.PIPE).stdout  
    data = fd_popen.readlines() 

    internal_dict = InternalMetrics_IntoDict(data)
    internal_list = []

    for metric in internal_metrics_list:
        if metric in internal_dict:
            internal_list.append(internal_dict[metric])
        else:
            internal_list.append("")
    
    result_internal.append(internal_list)
    

    ResultMetrics_GeneratorFile(result_internal, internal_metrics_list, "result_internal_"+str(instance_count))
    print(f"---saving on result_internal_{str(instance_count)}")
    ResultMetrics_GeneratorFile(result_external, external_metrics_list, "result_external_"+str(instance_count))
    print(f"---saving on result_external_{str(instance_count)}")

    # redis 서버 종료 
    os.system("/home/jieun/redis-5.0.2/src/redis-cli shutdown")
    os.system("rm -rf /home/jieun/redis-logs/appendonly.aof")
    os.system("rm -rf /home/jieun/redis-logs/dump.rdb")
    
# ResultMetrics_GeneratorFile(result_internal, internal_metrics_list, "result_internal_"+str(instance_count))
# ResultMetrics_GeneratorFile(result_external, external_name, "result_external_"+str(instance_count))

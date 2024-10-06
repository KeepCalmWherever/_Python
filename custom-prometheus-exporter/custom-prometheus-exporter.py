from prometheus_client import start_http_server, Gauge, Histogram
from pathlib import Path
from multiprocessing import Process
import requests, time, yaml

class custom_prometheus_exporter:
    def __init__ (self):
        self.endpoint_status = Gauge('endpoint_status', 'endpoint http status', ['endpoint_name'])
        self.endpoint_latency = Histogram('endpoint_latency', 'endpoint http latency', ['endpoint_name'])
    def start_exporter(self,configuration):
        def check_endpoint(check_endpoint,check_endpoint_timeout):
            endpoint_info = {}
            endpoint_request_start = time.perf_counter()
            try:
                endpoint_status = requests.get(url=check_endpoint, timeout=check_endpoint_timeout)
                endpoint_info['endpoint_code'] = endpoint_status.status_code
            except requests.exceptions.Timeout:
                endpoint_info['endpoint_code'] = 408
            endpoint_request_time = time.perf_counter() - endpoint_request_start
            endpoint_info['endpoint_name'] = check_endpoint
            endpoint_info['endpoint_latency'] = endpoint_request_time
            return endpoint_info
        def insert_metrics(endpoint_info):
            self.endpoint_status.labels(
                endpoint_name=endpoint_info['endpoint_name'],
            ).set(endpoint_info['endpoint_code'])
            self.endpoint_latency.labels(
                endpoint_name=endpoint_info['endpoint_name'],
            ).observe(endpoint_info['endpoint_latency'])
        def init_processes(configuration):
            while True:
                processess = []
                for endpoint in configuration['endpoints']:
                    processess.append(
                        Process(
                            target=insert_metrics(endpoint_info=check_endpoint(check_endpoint=endpoint,check_endpoint_timeout=configuration['endpoint_timeout']))
                        )
                    )
                for process in processess:
                    process.start()
                for process in processess:
                    process.join()
                time.sleep(configuration['scape_interval'])
        start_http_server(configuration['exporter_port'], configuration['exporter_address'])
        print(f"Started web server {configuration['exporter_address']}:{configuration['exporter_port']}")
        init_processes(configuration)

if __name__ == "__main__":
    try:
        custom_prometheus_exporter = custom_prometheus_exporter()
        custom_prometheus_exporter.start_exporter(yaml.safe_load(Path('configuration.yml').read_text()))
    except Exception as error:
        print("An exception occurred:", error)

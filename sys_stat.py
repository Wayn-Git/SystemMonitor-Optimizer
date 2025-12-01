import psutil

class SysStat:

    def get_stats(self):
        return {
            "cpu": self._cpu_stats(),
            "ram": self._ram_stats(),
            "disk": self._disk_stats()
        }

    def _cpu_stats(self):
        return {
            "usage": psutil.cpu_percent(interval=1),
            "per_core": psutil.cpu_percent(interval=None, percpu=True),
            "frequency": psutil.cpu_freq().current
        }

    def _ram_stats(self):
        mem = psutil.virtual_memory()
        return {
            "total": mem.total / (1024**3),
            "used": mem.used / (1024**3),
            "available": mem.available / (1024**3),
            "percent": mem.percent
        }
    
    def _disk_stats(self):
        pass

    def _processes(self):
        pass

    def _temp(self):
        pass


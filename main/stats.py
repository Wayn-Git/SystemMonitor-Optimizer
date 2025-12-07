import psutil
import pprint

class SysStat:

    def get_stats(self):
        return {
            "cpu": self._cpu_stats(),
            "ram": self._ram_stats(),
            "disk": self._disk_stats(),
            "processes": self._processes(),
            "temp": self._temp()
        }

    def _cpu_stats(self):
        return {
            "usage": psutil.cpu_percent(interval=None),
            "per_core": psutil.cpu_percent(interval=None, percpu=True),
            "frequency": psutil.cpu_freq().current
        }

    def _ram_stats(self):
        mem = psutil.virtual_memory()
        return {
            "total": round(mem.total / (1024**3),2),
            "used": mem.used / (1024**3),
            "available": mem.available / (1024**3),
            "percent": mem.percent
        }
    
    def _disk_stats(self):
        disk = psutil.disk_usage('/')
        return {
            "total": disk.total / (1024**3),
            "used": disk.used / (1024**3),
            "free": disk.free / (1024**3),
            "percent": disk.percent
        }

    def _processes(self):
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        # Sort by CPU usage and return top 5
        return sorted(processes, key=lambda x: x['cpu_percent'] or 0, reverse=True)[:5]

    def _temp(self):
        try:
            temps = psutil.sensors_temperatures()
            if not temps:
                return {"status": "No temperature sensors found"}
            
            temp_data = {}
            for name, entries in temps.items():
                temp_data[name] = [{"label": entry.label, "current": entry.current} 
                                   for entry in entries]
            return temp_data
        except AttributeError:
            return {"status": "Temperature monitoring not supported on this platform"}

    def display(self):
        pprint.pprint(self.get_stats())

# Remove these lines or use them for testing only:
# if __name__ == "__main__":
#     sys = SysStat()
#     sys.display()  # ✅ Correct method name
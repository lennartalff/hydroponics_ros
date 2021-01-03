import os
import concurrent.futures

OWI_BASE_DIR = "/sys/bus/w1/devices"


class ds18b20(object):
    def __init__(self):
        pass

    def read_worker(self, name):
        file_path = os.path.join(OWI_BASE_DIR, name, "temperature")
        try:
            with open(file_path) as f:
                data = f.readline().rstrip()
        except IOError:
            return None

        try:
            temperature = int(data) / 1000.0
        except ValueError:
            return None

        return temperature

    def read_temperatures(self, rom_ids):
        names = names_from_ids(rom_ids)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(self.read_worker, name) for name in names
            ]

        temperatures = [f.result() for f in futures]
        return temperatures


def check_existence(self, ids):
    names = names_from_ids(ids)
    exists = []
    for name in names:
        path = os.path.join(OWI_BASE_DIR, name)
        exists.append(os.path.isdir(path))
    return 


def ids_from_names(names):
    ids = []
    for name in names:
        name = name.replace("-", "")
        t = [int(name[i:i + 2], 16) for i in range(0, len(name), 2)]
        ids.append(t)
    return ids


def names_from_ids(ids):
    names = []
    for id in ids:
        family_code = "{:02x}".format(id[0])
        address = "".join(["{:02x}".format(i) for i in id[1:]])
        names.append("{}-{}".format(family_code, address))
    return names

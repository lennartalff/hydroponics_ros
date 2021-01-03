from influxdb import InfluxDBClient

layout = dict(
    water_temperature=dict(tags=tuple(), fields=("value", )),
    air_temperature=dict(tags=("index", ), fields=("value", )),
    pressure=dict(tags=("index", ), fields=("value", )),
    humidity=dict(tags=("index", ), fields=("value", )),
    led_temperature=dict(tags=tuple(), fields=("min", "max", "avg")),
    ph=dict(tags=("index", ), fields=("value", )),
    ec=dict(tags=("index", "type"), fields=("value", )),
)

durations = ["1h", "3h", "1d", "3d", "7d", "30d"]
sample_groups = ["", "10s", "1m", "5m", "10m", "60m"]


def create_databases(client, name):
    for i, duration in enumerate(durations):
        db_name = "{}_{}".format(name, duration)
        client.create_database(db_name)
        rp_name = "rp_{}".format(duration)
        client.create_retention_policy(name=rp_name,
                                       duration=duration,
                                       replication=1,
                                       database=db_name,
                                       default=True)
        if not i:
            continue
        for measurement in layout:
            select_fields = [
                "mean({}) as {}".format(field, field)
                for field in layout[measurement]["fields"]
            ]
            select_fields = ",".join(select_fields)
            db_previous = "{}_{}".format(name, durations[i - 1])
            select_clause = ("SELECT {} "
                             "INTO {}..{} "
                             "FROM {}..{} "
                             "GROUP BY time({}),*".format(
                                 select_fields, db_name, measurement,
                                 db_previous, measurement, sample_groups[i]))
            cq_name = "cq_{}_{}".format(measurement, sample_groups[i])
            client.create_continuous_query(
                name=cq_name,
                select=select_clause,
                database=db_name,
            )


def delete_databases(client, name):
    for duration in durations:
        db_name = "{}_{}".format(name, duration)
        client.drop_database(db_name)


class Database(object):
    def __init__(self, name):
        self.db_name = "{}_{}".format(name, durations[0])
        self.client = InfluxDBClient(database=self.db_name)

    def _write(self, data):
        return self.client.write_points(points=data,
                                        protocol="line",
                                        database=self.db_name,
                                        time_precision="ms")

    def insert_ph(self, index, value, stamp):
        data = [
            "ph,index={} value={} {}".format(index, value, int(stamp * 1000.0))
        ]
        return self._write(data)

    def insert_ec(self, index, type, value, stamp):
        data = [
            "ec,index={},type={} value={} {}".format(index, type, value,
                                                     int(stamp * 1000.0))
        ]
        return self._write(data)

    def insert_water_temperature(self, value, stamp):
        data = [
            "water_temperature value={} {}".format(value, int(stamp * 1000.0))
        ]
        return self._write(data)

    def insert_air_temperature(self, index, value, stamp):
        data = [
            "air_temperature,index={} value={} {}".format(
                index, value, int(stamp * 1000.0))
        ]
        return self._write(data)

    def insert_humidity(self, index, value, stamp):
        data = [
            "humidity,index={} value={} {}".format(index, value,
                                                   int(stamp * 1000.0))
        ]
        return self._write(data)

    def insert_pressure(self, index, value, stamp):
        data = [
            "pressure,index={} value={} {}".format(index, value,
                                                   int(stamp * 1000.0))
        ]
        return self._write(data)

    def insert_led_temperature(self, min_val, max_val, avg_val, stamp):
        data = [
            "led_temperature min={},max={},avg={} {}".format(
                min_val, max_val, avg_val, int(stamp * 1000.0))
        ]
        return self._write(data)


def main():
    client = InfluxDBClient()
    delete_databases(client, "hydro")
    create_databases(client, "hydro")


if __name__ == "__main__":
    main()

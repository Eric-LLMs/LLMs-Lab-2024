
class MockedDB:
    def __init__(self):
        self.data = [
            {"name": "Economy Plan", "price": 50, "data": 10, "requirement": None},
            {"name": "Travel Plan", "price": 180, "data": 100, "requirement": None},
            {"name": "Unlimited Plan", "price": 300, "data": 1000, "requirement": None},
            {"name": "Campus Plan", "price": 150, "data": 200, "requirement": "Student"},
        ]

    def retrieve(self, **kwargs):
        records = []
        for r in self.data:
            select = True
            if r["requirement"]:
                if "status" not in kwargs or kwargs["status"] != r["requirement"]:
                    continue
            for k, v in kwargs.items():
                if k == "sort":
                    continue
                if k == "data" and v["value"] == "unlimited":
                    if r[k] != 1000:
                        select = False
                        break
                if "operator" in v:
                    if not eval(str(r[k])+v["operator"]+str(v["value"])):
                        select = False
                        break
                elif str(r[k]) != str(v):
                    select = False
                    break
            if select:
                records.append(r)
        if len(records) <= 1:
            return records
        key = "price"
        reverse = False
        if "sort" in kwargs:
            key = kwargs["sort"]["value"]
            reverse = kwargs["sort"]["ordering"] == "descend"
        return sorted(records, key=lambda x: x[key], reverse=reverse)

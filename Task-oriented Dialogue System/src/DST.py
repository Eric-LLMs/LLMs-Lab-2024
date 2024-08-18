
class DST:
    def __init__(self):
        pass

    def update(self, state, nlu_semantics):
        if "name" in nlu_semantics:
            state.clear()
        if "sort" in nlu_semantics:
            slot = nlu_semantics["sort"]["value"]
            if slot in state and state[slot]["operator"] == "==":
                del state[slot]
        for k, v in nlu_semantics.items():
            state[k] = v
        return state
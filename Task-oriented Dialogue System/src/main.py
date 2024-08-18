from DialogManager import DialogManager
from BussinessRequirement import BussinessRequirement

if __name__ == '__main__':
    br = BussinessRequirement()
    dm = DialogManager(br.prompt_templates)  # Two rounds of dialogue
    print("# Round 1")
    response = dm.run("300 is too expensive, do you have anything under 200 yuan?")
    print("===response===")
    print(response)

    print("# Round 2")
    response = dm.run("Which plan has the most data?")
    print("===response===")
    print(response)
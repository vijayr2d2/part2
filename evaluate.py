import random
import pickle
import json

def createFiles():
    for i in range(900):
        if i < 10:
            file = open("0000{}.txt".format(i), 'a')
            file.close()
        elif i < 100:
            file = open("000{}.txt".format(i), 'a')
            file.close()
        else:
            file = open("00{}.txt".format(i), 'a')
            file.close()
    
    f = open('gt_new.txt', "r")
    lines = f.readlines()
    f.close()
    last = ""
    f = open('test.txt', 'a')
    for line in lines:
        parsed = line.split(";")
        classnum = parsed[5]
        classnum = int(classnum[0:2])
        objnum = 1
        if classnum < 6:
            objnum = 0
        elif classnum > 6 and classnum < 11:
            objnum = 0
        elif classnum > 14 and classnum < 17:
            objnum = 0
        elif classnum > 42:
            objnum = 1
        elif classnum == 17:
            objnum = 2
        else:
            objnum = 3

        x1 = int(parsed[1])
        y1 = int(parsed[2])
        x2 = int(parsed[3])
        y2 = int(parsed[4])

        # print(last)
        if parsed[0] != last:
            f.close()
            name = parsed[0][0:6] + 'txt' 
            f = open(name, 'a')
        if objnum != -1:
            f.write("{} {} {} {} {}\n".format(objnum, x1, y1, x2, y2))
        last = parsed[0]
    f.close()

def calcmAP(filename):
    tp = [0, 0, 0]
    fp = [0, 0, 0]
    fplist0 = []
    fplist1 = []
    fplist2 = []
    missed0 = []
    missed1 = []
    missed2 = []
    misclass = [0, 0, 0]

    f = open(filename, 'r')
    data = json.load(f)
    f.close()
    for frame in data["output"]["frames"]:
        framenum = frame["frame_number"][0:6] + "txt"
        f = open(framenum, 'r')
        lines = f.readlines()
        for sign in frame["signs"]:
            intersection = 0
            coords = sign["coordinates"]
            coords = [coords[0], coords[1], coords[0] + coords[2], coords[1] + coords[3]]
            for line in lines:
                parsed = line.split(" ")
                coords2 = [int(parsed[1]), int(parsed[2]), int(parsed[3]), int(parsed[4])]
                intersection = calcIOU(coords, coords2)
                if sign["class"] == "RedRoundSign":
                    if intersection >= .5:
                        if int(parsed[0]) == 0:
                            tp[0] += 1
                        else:
                            misclass[0] += 1
                            fplist0.append(frame["frame_number"])
                            fp[0] += 1
                            missed0.append(frame["frame_number"])
                        break
                elif sign["class"] == "pn":
                    if intersection >= .5:
                        if int(parsed[0]) == 1:
                            tp[1] += 1
                        else:
                            misclass[1] += 1
                            fplist0.append(frame["frame_number"])
                            fp[1] += 1
                            missed1.append(frame["frame_number"])
                        break
                elif sign["class"] == "pne":
                    if intersection >= .5:
                        if int(parsed[0]) == 2:
                            tp[2] += 1
                        else:
                            misclass[2] += 1
                            fplist0.append(frame["frame_number"])
                            fp[2] += 1
                            missed2.append(frame["frame_number"])
                        break
            if intersection < .5:
                if sign["class"] == "RedRoundSign":
                    fplist0.append(frame["frame_number"])
                    fp[0] += 1
                elif sign["class"] == "pn":
                    fplist1.append(frame["frame_number"])
                    fp[1] += 1
                elif sign["class"] == "pne":
                    fplist2.append(frame["frame_number"])
                    fp[2] += 1
    print("RedRoundSign")
    print("{} true positives, {} false positives, {} false negatives".format(tp[0], fp[0], 557 - tp[0]))
    print("pn")
    print("{} true positives, {} false positives, {} false negatives".format(tp[1], fp[1], 17 - tp[1]))
    print("pne")
    print("{} true positives, {} false positives, {} false negatives".format(tp[2], fp[2], 29 - tp[2]))
    print("{} misclassifications for redroundsign".format(misclass[0]))
    print(missed0)
    print("{} misclassifications for pn".format(misclass[1]))
    print(missed1)
    print("{} misclassifications for pne".format(misclass[2]))
    print(missed2)


    #shows where false positives are
    # print(fplist0)
    # print(fplist1)
    # print(fplist2)

def calcIOU(coords, coords2):
    x1 = max(coords[0], coords2[0])
    y1 = max(coords[1], coords2[1])
    x2 = min(coords[2], coords2[2])
    y2 = min(coords[3], coords2[3])
    commonarea = 0
    if x2 - x1 > 0 and y2 - y1 > 0:
        commonarea = (x2 - x1)*(y2 - y1)
    totalarea = (coords[2] - coords[0]) * (coords[3] - coords[1]) + (coords2[2] - coords2[0]) * (coords2[3] - coords2[1]) - commonarea
    return commonarea / totalarea


if __name__ == '__main__':
    createFiles() # only call if annotation files are not created yet
    calcmAP("GTSDB.json")

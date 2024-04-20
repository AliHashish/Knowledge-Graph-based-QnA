import json
import re

import inflect
# import pandas as pd
import spacy

from kwQnA._complex import ComplexFunc
from kwQnA._getentitypair import GetEntity


class QuestionAnswer:
    """docstring for QuestionAnswer."""

    def __init__(self):
        super(QuestionAnswer, self).__init__()
        self.complex = ComplexFunc()
        self.nlp = spacy.load('en_core_web_sm')
        self.p = inflect.engine()

    def findanswer(self, question, c):
        try:
            p = self.complex.question_pairs(question)
        except:
            return "Not Applicable"
        # print(p)

        if p == [] or p is None:
            return "Not Applicable"

        pair = p[0]

        f = open("extra/database.json","r", encoding="utf8")
        listData = f.readlines()

        relQ = []
        loaded = json.loads(listData[0])
        relationQ = self.nlp(pair[1])


        for i in relationQ:
            relationQ = i.lemma_
            relQ.append(relationQ)

        subjectQ = pair[0]
        objectQ = pair[3]
        subList = set()
        timeQ = str(pair[4])
        placeQ = str(pair[5])

        relationQ = " ".join(relQ)

        if pair[6] == 'who':
            for i in loaded:
                relationS = [relation for relation in self.nlp(loaded[str(i)]["relation"])]
                # relationSSS = " ".join([relation.lemma_ for relation in self.nlp(loaded[str(i)]["relation"])])
                relationSSS = " ".join([i.lemma_ for i in relationS])

                relationS = [i.lemma_ for i in relationS]
                relationS = relationS[0]

                if relationS == relationQ:
                    objectS = loaded[str(i)]["target"]
                    objectS = re.sub('-', ' ', objectS)
                    objectQ = re.sub('-', ' ', objectQ)
                    # remove extra spaces using regex
                    objectS = re.sub(' +', ' ', objectS)
                    objectQ = re.sub(' +', ' ', objectQ)

                    try: 
                        # by7awel bs mn plural le single
                        if self.p.singular_noun(objectS):
                            objectS = self.p.singular_noun(objectS)
                        if self.p.singular_noun(objectQ):
                            objectQ = self.p.singular_noun(objectQ)
                    except:
                        pass

                    timeS = ""
                    placeS = ""
                    if str(pair[4]) != "":
                        timeS = [str(loaded[str(i)]["time"])]
                    if str(pair[5]) != "":
                        placeS = [str(loaded[str(i)]["place"])]
                    if pair[0] in ('who'):
                        if objectS in objectQ or objectQ in objectS:    # el egaba fl object 3ady
                            answer_subj = loaded[str(i)]["source"]
                            subList.add(answer_subj)
                        elif objectQ in  " ".join(timeS):                     # et2kd en el egaba msh fl time
                            answer_subj = loaded[str(i)]["source"]
                            subList.add(answer_subj)
                        elif objectQ in  " ".join(placeS):                  # et2kd en el egaba msh fl place
                            answer_subj = loaded[str(i)]["source"]
                            subList.add(answer_subj)
                    else:               # check for the subject
                        subjectS = loaded[str(i)]["source"]
                        if subjectS in subjectQ or subjectQ in subjectS:
                            answer_subj = loaded[str(i)]["target"]
                            subList.add(answer_subj)

                elif str(relationSSS) == str(relationQ):
                    objectS = loaded[str(i)]["target"]
                    objectS = re.sub('-', ' ', objectS)

                    if objectS in objectQ or objectQ in objectS:
                        if str(pair[4]) != "":
                            timeS = [str(loaded[str(i)]["time"])]
                            if timeQ in " ".join(timeS):
                                answer_subj = loaded[str(i)]["source"]
                                subList.add(answer_subj)
                        else:
                            answer_subj = loaded[str(i)]["source"]
                            subList.add(answer_subj)


            answer_subj = ", ".join(subList)
            if answer_subj == "":
                return "None"
            return answer_subj

        elif pair[3] == 'what':
            subjectQ = pair[0]
            # subList = set()       # mt3rfa bara, msh lazem n3mlha hena tany
            for i in loaded:
                subjectS = loaded[str(i)]["source"]
                
                if subjectQ in subjectS or subjectS in subjectQ:
                    relationS = [relation.lemma_ for relation in self.nlp(loaded[str(i)]["relation"])]
                    relationS = " ".join(relationS)

                    if relationQ == relationS:
                        if str(pair[5]) != "":
                            placeS = [str(place) for place in self.nlp(loaded[str(i)]["place"])]
                            if placeQ in " ".join(placeS):
                                if str(pair[4]) != "":
                                    timeS = [str(time) for time in self.nlp(loaded[str(i)]["time"])]
                                    if timeQ in " ".join(timeS):
                                        answer_subj = loaded[str(i)]["target"]
                                        subList.add(answer_subj)
                                else:
                                    answer_subj = loaded[str(i)]["target"]
                                    subList.add(answer_subj)
                        else:
                            if str(pair[4]) != "":
                                timeS = [str(time) for time in self.nlp(loaded[str(i)]["time"])]
                                if timeQ in " ".join(timeS):
                                    answer_subj = loaded[str(i)]["target"]
                                    subList.add(answer_subj)
                            else:
                                answer_subj = loaded[str(i)]["target"]
                                subList.add(answer_subj)

            answer_obj = ", ".join(subList)
            if answer_obj == "":
                return "None"
            return answer_obj

        elif pair[4] == 'when':
            subjectQ = pair[0]
            for i in loaded:
                subjectS = loaded[str(i)]["source"]
                if subjectQ in subjectS or subjectS in subjectQ:
                    relationS = [relation.lemma_ for relation in self.nlp(loaded[str(i)]["relation"])]



                    relationS = " ".join(relationS)

                    if relationQ == relationS:
                        if str(pair[5]) != "":
                            placeS = [str(place) for place in self.nlp(loaded[str(i)]["place"])]
                            if placeQ in " ".join(placeS):
                                if loaded[str(i)]["time"] != '':
                                    answer_obj = loaded[str(i)]["time"]
                                    subList.add(answer_obj)
                                # return None     # lw el makan mwgood fl placeS, bs el time fady, return None, l2ny kda ma3rafsh el wa2t asln
                                # bs msh hn3ml return b2a, e7na bs msh hn-append 7aga fl egaba
                        else:
                            if loaded[str(i)]["time"] != '':
                                answer_obj = loaded[str(i)]["time"]
                                subList.add(answer_obj)
            answer_obj = ", ".join(subList)
            if answer_obj == "":
                return "None"
            return answer_obj

        elif pair[5] == 'where':
            subjectQ = pair[0]
            for i in loaded:
                subjectS = loaded[str(i)]["source"]
                if subjectQ in subjectS or subjectS in subjectQ:
                    relationS = [relation.lemma_ for relation in self.nlp(loaded[str(i)]["relation"])]
                    relationS = relationS[0]

                    if relationQ == relationS:
                        if str(pair[4]) != "":
                            timeS = [str(time) for time in self.nlp(loaded[str(i)]["time"])]
                            if timeQ in " ".join(timeS):
                                answer_obj = loaded[str(i)]["place"]
                                if answer_obj not in (" ",""):
                                    subList.add(answer_obj)
                            
                        
                        answer_obj = loaded[str(i)]["place"]
                        if answer_obj not in (" ",""):
                            subList.add(answer_obj)
            answer_obj = ", ".join(subList)
            if answer_obj == "":
                return "None"
            return answer_obj
        elif pair[6] == 'many':
            subjectQ = pair[0]
            for i in loaded:
                subjectS = loaded[str(i)]["source"]
                if subjectQ in subjectS or subjectS in subjectQ:
                    relationS = [relation.lemma_ for relation in self.nlp(loaded[str(i)]["relation"])]
                    relationS = relationS[0]

                    if True or relationQ == relationS:
                        if loaded[str(i)]["target"] in objectQ or objectQ in loaded[str(i)]["target"]:
                            answer_obj = loaded[str(i)]["quantity"]
                            subList.add(answer_obj)
            answer_obj = ", ".join(subList)
            if answer_obj == "":
                return "None"
            return answer_obj
        return "None"

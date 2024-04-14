# import re
import spacy


class ComplexFunc:
    # """docstring for Tenses."""

    def __init__(self):
        self.ent_pairs = list()
        self.nlp = spacy.load('en_core_web_sm')

    def get_time_place_from_sent(self,sentence):
        xdate =[]
        xplace =[]
        for i in sentence.ents:
            if i.label_ in ('DATE'):
                xdate.append(str(i))

            if i.label_ in ('GPE'):     # organizations w asamy el 7agat el m3roofa w kda
                xplace.append(str(i))

        return xdate, xplace

    def find_obj(self, sentence, place, time):
        object_list = []
        buffer_obj = None
        root_word = ""
        for word in sentence:
            # """OBJECT FINDING loop"""
            if word.dep_ in ('ROOT'):
                root_word = str(word).lower()
            root_condition = (root_word in ("am", "is", "are") and word.dep_ in ('attr'))
            if word.dep_ in ('obj', 'dobj', 'pobj') or root_condition:
                buffer_obj = word
                # if str(word) in place and word.nbor(-1).dep_ in ('prep') and str(word.nbor(-1)) == "of":
                #     pass
                #     # """ INDIA should be in place list + "of" "India" is there then it will come here """
                # else:
                if not (str(word) in place and word.nbor(-1).dep_ in ('prep') and str(word.nbor(-1)) == "of"):
                    if word.dep_ in ('dobj') or (str(word) not in " ".join(time) and str(word) not in " ".join(place)):
                        # """ INDIA should not be in place list + INDIA should not be in time list """
                        # """ice-cream and mangoes"""
                        for child in word.subtree:
                            child_root_condition = (root_word in ("am", "is", "are") and child.dep_ in ('attr'))
                            if (child.dep_ in ('conj', 'dobj', 'pobj', 'obj') or child_root_condition) and (child.dep_ in ('dobj') or (str(child) not in " ".join(time)) and str(child) not in " ".join(place)):
                                if [i for i in child.lefts]:
                                    if child.dep_ in ('dobj', 'obj','pobj') or child_root_condition:
                                        child_with_comp = ""
                                        for subtree_element in child.subtree:
                                            child_with_comp = child_with_comp + " " + str(subtree_element) if child_with_comp != "" else str(subtree_element)
                                        object_list.append(str(child_with_comp))
                                    # if child.nbor(-1).dep_ in ('nummod') and (child.dep_ in ('dobj', 'obj','pobj') or child_root_condition):
                                    #     child = str(child.nbor(-1)) + " " + str(child)
                                    #     object_list.append(str(child))

                                    # elif child.nbor(-1).dep_ in ('punct'):
                                    #     if child.nbor(-2).dep_ in ('compound'):
                                    #         #ice-cream
                                    #         child = str(child.nbor(-2)) + str(child.nbor(-1)) + str(child)
                                    #         object_list.append(str(child))
                                    #     elif child.nbor(-2).dep_ in ('amod'):
                                    #         #social-distancing
                                    #         child = str(child.nbor(-2)) + str(child.nbor(-1)) + str(child)
                                    #         object_list.append(str(child))

                                    # elif child.nbor(-1).dep_ in ('compound'):
                                    #     # print(child)
                                    #     child_with_comp = ""
                                    #     for i in child.subtree:
                                    #         if i.dep_ in ('compound', 'nummod','quantmod') or str(i) == str(child):
                                    #             if child_with_comp == "":
                                    #                 child_with_comp = str(i)
                                    #             else:
                                    #                 child_with_comp = child_with_comp +" "+ str(i)
                                    #         elif i.dep_ in ('cc'):
                                    #             break
                                    #     # child = child_with_comp + " " + str(child)
                                    #     # ice cream
                                    #     object_list.append(str(child_with_comp))

                                    # elif child.nbor(-1).dep_ in ('det'):
                                    #     # The Taj Mahal
                                    #     object_list.append(str(child))

                                elif [i for i in child.rights]:
                                    if str(child.text) not in object_list:
                                        object_list.append(str(child.text))

                                    for a in child.children:
                                        if a.dep_ in ('conj'):
                                            if a.nbor(-1).dep_ in ('punct'):
                                                pass
                                            else:
                                                object_list.extend( [ str(a.text) ] )

                                else:
                                    # icecream
                                    if str(child) not in object_list:
                                        object_list.append(str(child))

                    elif str(word) in " ".join(place) and str(word.nbor(-1)) != "of" and object_list == []:
                        object_list.append(str(word))
                    elif str(word) in " ".join(time) and object_list == []:
                        object_list.append(str(word))

        return object_list, buffer_obj

    def find_subj(self, sentence):
        subject_list = []
        # """ SUBJECT FINDING loop"""
        dep_word = [word.dep_ for word in sentence]
        word_dep_count_subj = [dep_word.index(word) for word in dep_word if word in ('nsubj', 'subj', 'nsubjpass')]
        if word_dep_count_subj:
            word_dep_count_subj = word_dep_count_subj[0] + 1
        else:
            word_dep_count_subj = 1

        subject_final = ""
        for word in sentence:
            # print(word.dep_, word)
            if word_dep_count_subj > 0:
                # in prime minister it gives compound and then nmod
                if word.dep_ in ('compound') or word.dep_ in ('nmod') or word.dep_ in ('amod') or word.dep_ in ('poss') or word.dep_ in ('case') or word.dep_ in ('nummod'):
                    if subject_final == "":
                        subject_final = str(word)
                        word_dep_count_subj = word_dep_count_subj - 1
                    elif word.dep_ in ('case'):
                        subject_final = subject_final+ "" +str(word)
                        word_dep_count_subj = word_dep_count_subj - 1
                    else:
                        subject_final = subject_final+ " " +str(word)
                        word_dep_count_subj = word_dep_count_subj - 1
                elif word.dep_ in ('nsubj', 'subj', 'nsubjpass'):
                    if subject_final == "":
                        subject_final = str(word)
                        subject_list.extend([str(a.text) for a in word.subtree if a.dep_ in ('conj')])
                        word_dep_count_subj = word_dep_count_subj - 1
                        break
                    else:
                        subject_final = subject_final+" "+str(word)
                        subject_list.extend([str(a.text) for a in word.subtree if a.dep_ in ('conj')])
                        word_dep_count_subj = word_dep_count_subj - 1
                        break
                else:
                    pass

        subject_list.append(subject_final)
        return subject_list

    def find_relation(self, buffer_obj):
        aux_relation = ""
        # RELATION FINDING loop
        relation = [w for w in buffer_obj.ancestors if w.dep_ =='ROOT']

        if relation:
            relation = relation[0]
            sp_relation = relation
            if relation.nbor(1).pos_ in ('VERB'):
                if relation.nbor(2).dep_ in ('xcomp'):
                    relation = ' '.join((str(relation), str(relation.nbor(1)), str(relation.nbor(2))))
                else:
                    relation = str(relation)
                    if str(sp_relation.nbor(2)) != 'and':
                        if sp_relation.nbor(1).dep_ in ('xcomp'):
                            aux_relation = str(sp_relation.nbor(1))
                        else:
                            aux_relation = str(sp_relation.nbor(2))
            elif relation.nbor(1).pos_ in ('ADP', 'PART') and relation.nbor(1).dep_ in ('aux') and str(relation.nbor(1)) == 'to':
                # print(relation.nbor(1), relation.nbor(1).pos_ )
                # print(relation)
                relation = " ".join((str(relation), str(relation.nbor(1))))
                if str(sp_relation.nbor(2)) != 'and':
                    aux_relation = str(sp_relation.nbor(2))
            elif relation.nbor(1).dep_ in ('prep') and str(relation.nbor(1)) == 'to' and (relation.nbor(1)).dep_ not in ('obj','dobj','pobj','det'):
                # print(relation.nbor(1), relation.nbor(1).pos_ )
                # print(relation)
                relation = " ".join((str(relation), str(relation.nbor(1))))
            else:
                relation = str(relation)
        else:
            relation = 'unknown'

        return relation, aux_relation

    def normal_sent(self, sentence):
        time, place = self.get_time_place_from_sent(sentence)

        subject_list, object_list = [], []

        aux_relation, child_with_comp = "", ""

        subject_list = self.find_subj(sentence)
        object_list, buffer_obj = self.find_obj(sentence, place, time)
        if not buffer_obj:
            return None
        relation, aux_relation = self.find_relation(buffer_obj)

        self.ent_pairs = []

        flag_time = False
        flag_place = False
        if time:
            flag_time = True
        if place:
            flag_place = True
        # if time:
        #     time = time[0]
        # else:
        #     time = ""

        # if place:
        #     place = place[0]
        # else:
        #     place = ""

        pa, pb=[], []
        for m in subject_list:
            pa.append([m])

        for n in object_list:
            pb.append([n])

        # print(pa, pb)
        if flag_time and flag_place:
            for m in range(0, len(pa)):
                for n in range(0, len(pb)):
                    for t in time:
                        for p in place:
                            self.ent_pairs.append([str(pa[m][0]).lower(), str(relation).lower(),str(aux_relation).lower(), str(pb[n][0]).lower(), str(t), str(p)])
        elif flag_time:
            for m in range(0, len(pa)):
                for n in range(0, len(pb)):
                    for t in time:
                        self.ent_pairs.append([str(pa[m][0]).lower(), str(relation).lower(),str(aux_relation).lower(), str(pb[n][0]).lower(), str(t), str("")])
        elif flag_place:
            for m in range(0, len(pa)):
                for n in range(0, len(pb)):
                    for p in place:
                        self.ent_pairs.append([str(pa[m][0]).lower(), str(relation).lower(),str(aux_relation).lower(), str(pb[n][0]).lower(), str(""), str(p)])
        else:
            for m in range(0, len(pa)):
                for n in range(0, len(pb)):
                    self.ent_pairs.append([str(pa[m][0]).lower(), str(relation).lower(),str(aux_relation).lower(), str(pb[n][0]).lower(), str(""), str("")])

        # print(self.ent_pairs)
        return self.ent_pairs

    def question_pairs(self, question__):

        questionNLPed = self.nlp(question__)
        
        root_condition = False
        root_word = ""
        for word in questionNLPed:
            if word.dep_ in ('ROOT'):
                root_word = str(word).lower()
            # root_condition = (root_word in ("am", "is", "are") and word.dep_ in ('attr'))

        maybe_object = ([i for i in questionNLPed if (i.dep_ in ('obj', 'pobj', 'dobj') or (root_word in ("am", "is", "are") and i.dep_ in ('attr')))])
        maybe_place, maybe_time = [], []
        aux_relation = ""
        maybe_time, maybe_place = self.get_time_place_from_sent(questionNLPed)
        object_list = []

        subject = ""

        for obj in questionNLPed:
            objectNEW = obj
            root_condition = (root_word in ("am", "is", "are") and obj.dep_ in ('attr'))
            # FOR WHO
            if (obj.dep_ in ('obj', 'dobj', 'pobj', 'xcomp') or root_condition) and str(obj).lower() != "what":
                buffer_obj = obj

                if obj.dep_ in ('xcomp') and obj.nbor(-1).dep_ in ('aux') and obj.nbor(-2).dep_ in ('ROOT'):
                    continue

                if str(obj).lower() in str(maybe_place).lower() and obj.nbor(-1).dep_ in ('prep') and str(obj.nbor(-1)) == "of":
                    pass
                else:
                    if str(obj).lower() not in str(maybe_time).lower() and str(obj).lower() not in str(maybe_place).lower():
                        for child in obj.subtree:
                            child_root_condition = (root_word in ("am", "is", "are") and child.dep_ in ('attr'))
                            if child.dep_ in ('conj', 'dobj', 'pobj', 'obj') or child_root_condition:
                                if [i for i in child.children]:        # momkn nb2a ngarab child.children badal .lefts, 3mlnaha fy 7aga tanya w zabatet
                                    if child.nbor(-1).dep_ in ('punct') and child.nbor(-2).dep_ in ('compound'):
                                        child = str(child.nbor(-2)) + str(child.nbor(-1)) + str(child)
                                        object_list.append(str(child))

                                    elif child.nbor(-1).dep_ in ('compound'):
                                        child_with_comp = ""
                                        for i in child.subtree:
                                            if i.dep_ in ('compound', 'nummod','quantmod'):
                                                if child_with_comp == "":
                                                    child_with_comp = str(i)
                                                else:
                                                    child_with_comp = child_with_comp +" "+ str(i)
                                            elif i.dep_ in ('cc'):
                                                break
                                        child = child_with_comp + " " + str(child)

                                        object_list.append(str(child))

                                    elif child.nbor(-1).dep_ in ('det'):
                                        object_list.append(str(child))

                                elif [i for i in child.rights]:
                                    if str(child.text) not in object_list:
                                        object_list.append(str(child.text))

                                    for a in child.children:
                                        if a.dep_ in ('conj'):
                                            if a.nbor(-1).dep_ in ('punct'):
                                                pass
                                            else:
                                                object_list.extend( [ str(a.text) ] )

                                else:
                                    if str(child) not in object_list:
                                        object_list.append(str(child))

                            elif obj.dep_ in ('xcomp'):
                                object_list.append(str(obj).lower())

                    elif str(obj).lower() in str(maybe_place).lower() and str(obj.nbor(-1)) != "of":
                        object_list.append(str(obj).lower())
                    else:
                        if str(obj).lower() in str(maybe_time).lower() and object_list == []:
                            object_list.append(str(obj).lower())


                obj = object_list[-1]
                relation = [w for w in objectNEW.ancestors if w.dep_ =='ROOT']
                if relation:
                    relation = relation[0]
                    sp_relation = relation
                    if relation.nbor(1).pos_ in ('ADP', 'PART', 'VERB'):
                        if relation.nbor(2).dep_ in ('xcomp'):
                            aux_relation = str(relation.nbor(2))
                            relation = str(relation)+" "+str(relation.nbor(1))
                        else:
                            relation = str(relation)

                    subject = [a for a in sp_relation.lefts if a.dep_ in ('subj', 'nsubj','nsubjpass')]  # identify subject nodes
                    if subject:
                        subject = subject[0]
                    else:
                        subject = 'unknown'
                else:
                    relation = 'unknown'

                self.ent_pairs = []
                
                if maybe_time and maybe_place:
                    self.ent_pairs.append([str(subject).lower(), str(relation).lower(),str(aux_relation).lower(), str(obj).lower(), str(maybe_time[0]).lower(), str(maybe_place[0]).lower()])
                elif maybe_time:
                    self.ent_pairs.append([str(subject).lower(), str(relation).lower(),str(aux_relation).lower(), str(obj).lower(), str(maybe_time[0]).lower(), str("").lower()])
                elif maybe_place:
                    self.ent_pairs.append([str(subject).lower(), str(relation).lower(),str(aux_relation).lower(), str(obj).lower(), str("").lower(), str(maybe_place[0]).lower()])
                else:
                    self.ent_pairs.append([str(subject).lower(), str(relation).lower(),str(aux_relation).lower(), str(obj).lower(), str("").lower(), str("").lower()])
                return self.ent_pairs

            elif str(obj).lower() == "what":
                relation = [w for w in objectNEW.ancestors if w.dep_ =='ROOT']
                if relation:
                    relation = relation[0]
                    sp_relation = relation
                    if relation.nbor(1).pos_ in ('ADP', 'PART', 'VERB'):
                        if relation.nbor(2).dep_ in ('xcomp'):
                            aux_relation = str(relation.nbor(2))
                            relation = str(relation)+" "+str(relation.nbor(1))
                        else:
                            relation = str(relation)

                    subject = self.find_subj(questionNLPed)
                    subject = subject[-1]

                else:
                    relation = 'unknown'

                self.ent_pairs = []
                if maybe_time and maybe_place:
                    self.ent_pairs.append([str(subject).lower(), str(relation).lower(),str(aux_relation).lower(), str(obj).lower(), str(maybe_time[0]).lower(), str(maybe_place[0]).lower()])
                elif maybe_time:
                    self.ent_pairs.append([str(subject).lower(), str(relation).lower(),str(aux_relation).lower(), str(obj).lower(), str(maybe_time[0]).lower(), str("").lower()])
                elif maybe_place:
                    self.ent_pairs.append([str(subject).lower(), str(relation).lower(),str(aux_relation).lower(), str(obj).lower(), str("").lower(), str(maybe_place[0]).lower()])
                else:
                    self.ent_pairs.append([str(subject).lower(), str(relation).lower(),str(aux_relation).lower(), str(obj).lower(), str("").lower(), str("").lower()])
                return self.ent_pairs

            elif obj.dep_ in ('advmod'):
                if str(obj).lower() == 'where':
                    relation = [w for w in obj.ancestors if w.dep_ =='ROOT']
                    if relation:
                        relation = relation[0]
                        sp_relation = relation
                        if relation.nbor(1).pos_ in ('ADP', 'PART', 'VERB'):
                            if relation.nbor(2).dep_ in ('xcomp'):
                                aux_relation = str(relation.nbor(2))
                                relation = str(relation)+" "+str(relation.nbor(1))
                            else:
                                relation = str(relation)
                                
                        subject = self.find_subj(questionNLPed)
                        subject = subject[-1]

                    else:
                        relation = 'unknown'

                    self.ent_pairs = []
                    if maybe_object:
                        if maybe_time and maybe_place:
                            self.ent_pairs.append([str(subject).lower(), str(relation).lower(),str(aux_relation).lower(), str(maybe_object[-1]).lower(), str(maybe_time[0]).lower(), str("where").lower()])
                        elif maybe_time:
                            self.ent_pairs.append([str(subject).lower(), str(relation).lower(),str(aux_relation).lower(), str(maybe_object[-1]).lower(), str(maybe_time[0]).lower(), str("where").lower()])
                        elif maybe_place:
                            self.ent_pairs.append([str(subject).lower(), str(relation).lower(),str(aux_relation).lower(), str(maybe_object[-1]).lower(), str("").lower(), str("where").lower()])
                        else:
                            self.ent_pairs.append([str(subject).lower(), str(relation).lower(),str(aux_relation).lower(), str(maybe_object[-1]).lower(), str("").lower(), str("where").lower()])
                    else:
                        if maybe_time and maybe_place:
                            self.ent_pairs.append([str(subject).lower(), str(relation).lower(),str(aux_relation).lower(), str("").lower(), str(maybe_time[0]).lower(), str("where").lower()])
                        elif maybe_time:
                            self.ent_pairs.append([str(subject).lower(), str(relation).lower(),str(aux_relation).lower(), str("").lower(), str(maybe_time[0]).lower(), str("where").lower()])
                        elif maybe_place:
                            self.ent_pairs.append([str(subject).lower(), str(relation).lower(),str(aux_relation).lower(), str("").lower(), str("").lower(), str("where").lower()])
                        else:
                            self.ent_pairs.append([str(subject).lower(), str(relation).lower(),str(aux_relation).lower(), str("").lower(), str("").lower(), str("where").lower()])


                    return self.ent_pairs

                elif str(obj).lower() == 'when':
                    relation = [w for w in obj.ancestors if w.dep_ =='ROOT']
                    if relation:
                        relation = relation[0]
                        sp_relation = relation
                        if relation.nbor(1).pos_ in ('ADP', 'PART', 'VERB'):
                            if relation.nbor(2).dep_ in ('xcomp'):
                                relation = ' '.join((str(relation), str(relation.nbor(1)), str(relation.nbor(2))))
                            else:
                                relation = ' '.join((str(relation), str(relation.nbor(1))))

                        for left_word in sp_relation.children:
                            if left_word.dep_ in ('subj', 'nsubj','nsubjpass'):
                                if [i for i in left_word.lefts]:
                                    for left_of_left_word in left_word.lefts:
                                        subject = str(left_of_left_word) + " " + str(left_word)
                                else:
                                    subject = str(left_word)
                        
                    else:
                        relation = 'unknown'

                    self.ent_pairs = []
                    if maybe_object:
                        if maybe_time and maybe_place:
                            self.ent_pairs.append([str(subject).lower(), str(relation).lower(),str(aux_relation).lower(), str(maybe_object[-1]).lower(), str("when").lower(), str(maybe_place[0]).lower()])
                        elif maybe_time:
                            self.ent_pairs.append([str(subject).lower(), str(relation).lower(),str(aux_relation).lower(), str(maybe_object[-1]).lower(), str("when").lower(), str("").lower()])
                        elif maybe_place:
                            self.ent_pairs.append([str(subject).lower(), str(relation).lower(),str(aux_relation).lower(), str(maybe_object[-1]).lower(), str("when").lower(), str(maybe_place[0]).lower()])
                        else:
                            self.ent_pairs.append([str(subject).lower(), str(relation).lower(),str(aux_relation).lower(), str(maybe_object[-1]).lower(), str("when").lower(), str("").lower()])
                    else:
                        if maybe_time and maybe_place:
                            self.ent_pairs.append([str(subject).lower(), str(relation).lower(),str(aux_relation).lower(), str("").lower(), str("when").lower(), str(maybe_place[0]).lower()])
                        elif maybe_time:
                            self.ent_pairs.append([str(subject).lower(), str(relation).lower(),str(aux_relation).lower(), str("").lower(), str("when").lower(), str("").lower()])
                        elif maybe_place:
                            self.ent_pairs.append([str(subject).lower(), str(relation).lower(),str(aux_relation).lower(), str("").lower(), str("when").lower(), str(maybe_place[0]).lower()])
                        else:
                            self.ent_pairs.append([str(subject).lower(), str(relation).lower(),str(aux_relation).lower(), str("").lower(), str("when").lower(), str("").lower()])


                    return self.ent_pairs

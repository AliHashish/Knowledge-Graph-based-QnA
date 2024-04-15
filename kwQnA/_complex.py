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
    
    def get_quantity_from_sent(self,sentence):
        quantity = []
        for word in sentence:
            if word.dep_ in ('pobj', 'dobj', 'obj', 'npadvmod', 'attr'):
                if [child for child in word.children if child.dep_ in ('nummod', 'amod', 'quantmod', 'mod')]:
                    child_with_comp = ""
                    for child in word.subtree:
                        child_with_comp = child_with_comp + " " + str(child) if child_with_comp != "" else str(child)
                    quantity.append(child_with_comp)        
        return quantity


    def find_obj(self, sentence, place, time):
        object_list = []
        buffer_obj = None
        root_word = ""
        for word in sentence:
            # """OBJECT FINDING loop"""
            if word.dep_ in ('ROOT'):
                root_word = str(word)
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
                                            if subtree_element.dep_ not in ('det'):
                                                child_with_comp = child_with_comp + " " + str(subtree_element) if child_with_comp != "" else str(subtree_element)
                                        object_list.append(str(child_with_comp))

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
        quantity = self.get_quantity_from_sent(sentence)

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
        flag_quantity = False
        if time:
            flag_time = True
        if place:
            flag_place = True
        if quantity:
            flag_quantity = True
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
        if flag_quantity:
            if flag_time and flag_place:
                for m in range(0, len(pa)):
                    for n in range(0, len(pb)):
                        for t in time:
                            for p in place:
                                for q in quantity:
                                    self.ent_pairs.append([str(pa[m][0]), str(relation),str(aux_relation), str(pb[n][0]), str(t), str(p), str(q)])
            elif flag_time:
                for m in range(0, len(pa)):
                    for n in range(0, len(pb)):
                        for t in time:
                            for q in quantity:
                                self.ent_pairs.append([str(pa[m][0]), str(relation),str(aux_relation), str(pb[n][0]), str(t), str(""), str(q)])
            elif flag_place:
                for m in range(0, len(pa)):
                    for n in range(0, len(pb)):
                        for p in place:
                            for q in quantity:
                                self.ent_pairs.append([str(pa[m][0]), str(relation),str(aux_relation), str(pb[n][0]), str(""), str(p), str(q)])
            else:
                for m in range(0, len(pa)):
                    for n in range(0, len(pb)):
                        for q in quantity:
                            self.ent_pairs.append([str(pa[m][0]), str(relation),str(aux_relation), str(pb[n][0]), str(""), str(""), str(q)])
        else:
            if flag_time and flag_place:
                for m in range(0, len(pa)):
                    for n in range(0, len(pb)):
                        for t in time:
                            for p in place:
                                self.ent_pairs.append([str(pa[m][0]), str(relation),str(aux_relation), str(pb[n][0]), str(t), str(p), str("")])
            elif flag_time:
                for m in range(0, len(pa)):
                    for n in range(0, len(pb)):
                        for t in time:
                            self.ent_pairs.append([str(pa[m][0]), str(relation),str(aux_relation), str(pb[n][0]), str(t), str(""), str("")])
            elif flag_place:
                for m in range(0, len(pa)):
                    for n in range(0, len(pb)):
                        for p in place:
                            self.ent_pairs.append([str(pa[m][0]), str(relation),str(aux_relation), str(pb[n][0]), str(""), str(p), str("")])
            else:
                for m in range(0, len(pa)):
                    for n in range(0, len(pb)):
                        self.ent_pairs.append([str(pa[m][0]), str(relation),str(aux_relation), str(pb[n][0]), str(""), str(""), str("")])
        # print(self.ent_pairs)
        return self.ent_pairs

    def question_pairs(self, question__):

        questionNLPed = self.nlp(question__)
        
        root_condition = False
        root_word = ""
        for word in questionNLPed:
            if word.dep_ in ('ROOT'):
                root_word = str(word)
            # root_condition = (root_word in ("am", "is", "are") and word.dep_ in ('attr'))

        maybe_object = ([i for i in questionNLPed if (i.dep_ in ('obj', 'pobj', 'dobj') or (root_word in ("am", "is", "are") and i.dep_ in ('attr')))])
        maybe_place, maybe_time = [], []
        aux_relation = ""
        maybe_time, maybe_place = self.get_time_place_from_sent(questionNLPed)
        object_list = []

        subject = ""

            
        for index, obj in enumerate(questionNLPed):
            objectNEW = obj
            root_condition = (root_word in ("am", "is", "are") and obj.dep_ in ('attr'))
            # FOR WHO
            if (obj.dep_ in ('obj', 'dobj', 'pobj', 'xcomp') or root_condition) and str(obj) != "what" and str(obj) != "how":
                buffer_obj = obj

                if obj.dep_ in ('xcomp') and obj.nbor(-1).dep_ in ('aux') and obj.nbor(-2).dep_ in ('ROOT'):
                    continue

                # if str(obj) in str(maybe_place) and obj.nbor(-1).dep_ in ('prep') and str(obj.nbor(-1)) == "of":
                #     pass
                # else:
                if not (str(obj) in str(maybe_place) and obj.nbor(-1).dep_ in ('prep') and str(obj.nbor(-1)) == "of"):
                    if obj.dep_ in ('dobj') or (str(obj) not in " ".join(maybe_time) and str(obj) not in " ".join(maybe_place)):
                        for child in obj.subtree:
                            child_root_condition = (root_word in ("am", "is", "are") and child.dep_ in ('attr'))
                            if child.dep_ in ('conj', 'dobj', 'pobj', 'obj') or child_root_condition:
                                if [i for i in child.children]:        # momkn nb2a ngarab child.children badal .lefts, 3mlnaha fy 7aga tanya w zabatet
                                    child_with_comp = ""
                                    for subtree_element in child.subtree:
                                        if subtree_element.dep_ not in ('det'):
                                            child_with_comp = child_with_comp + " " + str(subtree_element) if child_with_comp != "" else str(subtree_element) 
                                    object_list.append(str(child_with_comp))

                                

                                else:
                                    if str(child) not in object_list:
                                        object_list.append(str(child))

                            elif obj.dep_ in ('xcomp'):
                                object_list.append(str(obj))

                    elif str(obj) in str(maybe_place) and str(obj.nbor(-1)) != "of":
                        object_list.append(str(obj))
                    else:
                        if str(obj) in str(maybe_time) and object_list == []:
                            object_list.append(str(obj))

                print(str(questionNLPed))
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
                    self.ent_pairs.append([str(subject), str(relation),str(aux_relation), str(obj), str(maybe_time[0]), str(maybe_place[0]), str("")])
                elif maybe_time:
                    self.ent_pairs.append([str(subject), str(relation),str(aux_relation), str(obj), str(maybe_time[0]), str(""), str("")])
                elif maybe_place:
                    self.ent_pairs.append([str(subject), str(relation),str(aux_relation), str(obj), str(""), str(maybe_place[0]), str("")])
                else:
                    self.ent_pairs.append([str(subject), str(relation),str(aux_relation), str(obj), str(""), str(""), str("")])
                return self.ent_pairs

            elif str(obj) == "what":
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
                    self.ent_pairs.append([str(subject), str(relation),str(aux_relation), str(obj), str(maybe_time[0]), str(maybe_place[0]), str("")])
                elif maybe_time:
                    self.ent_pairs.append([str(subject), str(relation),str(aux_relation), str(obj), str(maybe_time[0]), str(""), str("")])
                elif maybe_place:
                    self.ent_pairs.append([str(subject), str(relation),str(aux_relation), str(obj), str(""), str(maybe_place[0]), str("")])
                else:
                    self.ent_pairs.append([str(subject), str(relation),str(aux_relation), str(obj), str(""), str(""), str("")])
                return self.ent_pairs

            elif obj.dep_ in ('advmod') and str(obj) != "how":
                if str(obj) == 'where':
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
                            self.ent_pairs.append([str(subject), str(relation),str(aux_relation), str(maybe_object[-1]), str(maybe_time[0]), str("where"), str("")])
                        elif maybe_time:
                            self.ent_pairs.append([str(subject), str(relation),str(aux_relation), str(maybe_object[-1]), str(maybe_time[0]), str("where"), str("")])
                        elif maybe_place:
                            self.ent_pairs.append([str(subject), str(relation),str(aux_relation), str(maybe_object[-1]), str(""), str("where"), str("")])
                        else:
                            self.ent_pairs.append([str(subject), str(relation),str(aux_relation), str(maybe_object[-1]), str(""), str("where"), str("")])
                    else:
                        if maybe_time and maybe_place:
                            self.ent_pairs.append([str(subject), str(relation),str(aux_relation), str(""), str(maybe_time[0]), str("where"), str("")])
                        elif maybe_time:
                            self.ent_pairs.append([str(subject), str(relation),str(aux_relation), str(""), str(maybe_time[0]), str("where"), str("")])
                        elif maybe_place:
                            self.ent_pairs.append([str(subject), str(relation),str(aux_relation), str(""), str(""), str("where"), str("")])
                        else:
                            self.ent_pairs.append([str(subject), str(relation),str(aux_relation), str(""), str(""), str("where"), str("")])


                    return self.ent_pairs

                elif str(obj) == 'when':
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
                            self.ent_pairs.append([str(subject), str(relation),str(aux_relation), str(maybe_object[-1]), str("when"), str(maybe_place[0]), str("")])
                        elif maybe_time:
                            self.ent_pairs.append([str(subject), str(relation),str(aux_relation), str(maybe_object[-1]), str("when"), str(""), str("")])
                        elif maybe_place:
                            self.ent_pairs.append([str(subject), str(relation),str(aux_relation), str(maybe_object[-1]), str("when"), str(maybe_place[0]), str("")])
                        else:
                            self.ent_pairs.append([str(subject), str(relation),str(aux_relation), str(maybe_object[-1]), str("when"), str(""), str("")])
                    else:
                        if maybe_time and maybe_place:
                            self.ent_pairs.append([str(subject), str(relation),str(aux_relation), str(""), str("when"), str(maybe_place[0]), str("")])
                        elif maybe_time:
                            self.ent_pairs.append([str(subject), str(relation),str(aux_relation), str(""), str("when"), str(""), str("")])
                        elif maybe_place:
                            self.ent_pairs.append([str(subject), str(relation),str(aux_relation), str(""), str("when"), str(maybe_place[0]), str("")])
                        else:
                            self.ent_pairs.append([str(subject), str(relation),str(aux_relation), str(""), str("when"), str(""), str("")])


                    return self.ent_pairs
            elif str(obj) == "how":
                if str(questionNLPed[index+1]) == "many":
                    # kda dh so2al how many
                    relation = [w for w in objectNEW.ancestors if w.dep_ =='ROOT']
                    if relation:
                        relation = relation[0]          # hna5od awl kelma bs mn el relation (should be enough y3ny)
                        objects = [w for w in questionNLPed if w.dep_ in ('dobj', 'obj', 'npadvmod', 'dative')]
                        if not objects:
                            objects = [w for w in questionNLPed if w.dep_ in ('nsubj', 'nsubjpass')]
                        if objects:
                            objects = objects[0]

                        subject = self.find_subj(questionNLPed)
                        subject = subject[-1]
                        subject = subject.split()
                        subject = subject[-1]
                    else:
                        relation = 'unknown'
                    
                    self.ent_pairs = []
                    self.ent_pairs.append([str(subject), str(relation),"", str(objects), "", "", "many"])
                    return self.ent_pairs
                    
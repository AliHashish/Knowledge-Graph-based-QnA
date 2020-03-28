import spacy

class change_nouns:
    """docstring for change_nouns."""

    def __init__(self):
        super(change_nouns, self).__init__()
        self.nlp = spacy.load('en_core_web_sm')

    def resolved(self, text):
        text = self.nlp(text)
        flag = True

        official_subject = "Unknown"

        sentences = []
        prev_subjs = []

        # checked_for_and , depend , pos_of_and_= self.check_for_multi_and_(sent)
        # print(checked_for_and)

        # sent1, sent2 = self.diff_sent_return(sent, depend, pos_of_and_)

        for sent in text.sents:
            prev_subj, compound_is, last_word = "", "", ""

            dep_word = [word.dep_ for word in sent]
            word_dep_count_subj = [dep_word.index(word) for word in dep_word if word in ('nsubj', 'subj', 'nsubjpass')]
            word_dep_count_subj = word_dep_count_subj[0] + 1

            for word in sent:
                if word_dep_count_subj > 0:
                    """ IN prime minister it gives compound and then nmod """
                    if word.dep_ in ('compound') or word.dep_ in ('nmod', 'amod'):
                        if compound_is == "":
                            compound_is = str(word)
                            word_dep_count_subj = word_dep_count_subj - 1
                        else:
                            compound_is = compound_is+ " " +str(word)
                            word_dep_count_subj = word_dep_count_subj - 1

                    elif word.dep_ in ('nsubj', 'subj', 'nsubjpass'):
                        pronoun = [i for i in word.subtree]

                        if compound_is == "":
                            if str(word) not in ('he','HE', 'He','she','SHE', 'She','it','IT', 'It'):
                                prev_subj = str(word)
                                word_dep_count_subj = word_dep_count_subj - 1
                                if str(pronoun[0]) not in ('his','His', 'her','Her', 'its', 'Its'):
                                    prev_subjs = [prev_subj]
                                    official_subject = prev_subjs[0]

                        else:
                            if str('poss') in [str(i.dep_) for i in word.subtree]:
                                prev_subj = compound_is
                                word_dep_count_subj = word_dep_count_subj - 1
                                prev_subjs = [prev_subj]
                                # official_subject = prev_subjs[0]
                            else:
                                prev_subj = compound_is+" "+str(word)
                                word_dep_count_subj = word_dep_count_subj - 1
                                prev_subjs = [prev_subj]
                                official_subject = prev_subjs[0]

                        # if str(word) in ('they'):
                            # subject_list.extend([str(a.text) for a in word.subtree if a.dep_ in ('conj')])
                        if str(word) in ('he','HE', 'He','she','SHE', 'She','it','IT', 'It'):
                            # print(prev_subjs)
                            new_word = prev_subjs[-1]
                            # print(new_word)
                            sentences.append(str(sent).replace(str(word), str(new_word)))
                            flag = False

                        if pronoun:
                            if len(pronoun) <= 2 and str(pronoun[0]) in ('his','His', 'her','Her', 'its', 'Its'):
                                print(official_subject)
                                new_word = str(official_subject)+"\'s"
                                # print(new_word)
                                sentences.append(str(sent).replace((str(pronoun[0])), str(new_word)))
                                flag = False
                            elif len(pronoun)>2 and str(pronoun[0]) in ('his','His', 'her','Her', 'its', 'Its'):
                                new_word = str(official_subject)+"\'s"
                                sentences.append(str(sent).replace(str(pronoun[0]), str(new_word)))
                                flag = False


                    elif word.dep_ in ('nsubj','subj','nsubjpass') and str(word) not in ('he','HE', 'He','she','SHE', 'She','it','IT', 'It'):
                        last_word = word
                    else:
                        pass

            if flag:
                sentences.append(str(sent))
            else:
                flag = True

        resolved_text = " ".join(sentences)
        return resolved_text

    def check_for_multi_and_(self, sentence):
        x = []
        count = 0
        for word in sentence:
            # print([i for i in word.subtree])
            count += 1
            if word.dep_ in ('cc'):
                x.append(count-1)
                # print([i for i in word.head.rights if i.dep_ in ('obj', 'dobj', 'pobj')])
                # print([i for i in word.head.rights if i.dep_ in ('nsubj', 'nsubjpass', 'subj')])
                # print([i for i in word.head.rights if i.dep_ in ('conj')])
        # print(x)

        depen = []
        for i in x:
            depen.append([word.dep_ for word in sentence[:i]])

        senten1, senten2 = "", ""
        list2 = ["nsubj", "ROOT", "dobj"]
        # , ["subj", "ROOT", "dobj"], ["subj", "ROOT", "pobj"], ["nsubj", "ROOT", "obj"], ["nsubj", "ROOT", "dobj"], ["nsubj", "ROOT", "pobj"], ["nsubjpass", "ROOT", "obj"], ["nsubjpass", "ROOT", "dobj"], ["nsubjpass", "ROOT", "pobj"]]

        for list1 in depen:
            check = all(item in list1 for item in list2)
            #
            # print(list1)

            if check:
                # print(depen, x)
                return True, depen, x
            else:
                pass

        return False, [], 0

    def diff_sent_return(self, sentence, depen, pos_of_and):
        newcount = -1
        senten1, senten2 = "", ""
        # , ["subj", "ROOT", "dobj"], ["subj", "ROOT", "pobj"], ["nsubj", "ROOT", "obj"], ["nsubj", "ROOT", "dobj"], ["nsubj", "ROOT", "pobj"], ["nsubjpass", "ROOT", "obj"], ["nsubjpass", "ROOT", "dobj"], ["nsubjpass", "ROOT", "pobj"]]
        list2 = ["nsubj", "ROOT", "dobj"]

        for i in depen:
            newcount += 1
            list1 = i
            check = all(item in list1 for item in list2)
            if check:
                lista = [str(w) for w in sentence]

                p1 = lista[:pos_of_and[newcount]]
                p2 = lista[pos_of_and[newcount]+1:]

                # print(p1, p2)

                senten1 = " ".join(p1)
                senten2 = " ".join(p2)

                senten1 = self.nlp(senten1)
                senten2 = self.nlp(senten2)

        return str(senten1), str(senten2)


if __name__ == "__main__":
    test = change_nouns()
    sentences = test.resolved("Manchester City Football Club is based in Manchester. It competes in the Premier League. It was known as Ardwick Association Football Club. Manchester City Football Club is referred as The Centurions and The Fourmidables. Its home ground is located in east Manchester. Its home ground is also known as CityofManchesterStadium.")
    print(sentences)
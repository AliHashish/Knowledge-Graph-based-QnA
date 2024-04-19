import regex as re
from pathlib import Path
import spacy
from spacy import displacy

class change_nouns:
    """docstring for change_nouns."""

    def __init__(self):
        super(change_nouns, self).__init__()
        self.nlp = spacy.load('en_core_web_sm')

    def resolved(self, text, questions_mlhash_lazma=[], title=""):
        flag = True

        official_subject = title if title else "Unknown"

        sentences = []
        prev_subjs = [title]



        text = self.nlp(text)
        
        # bnersem el data
        # svg = displacy.render(text, style="dep", jupyter=False)
        # output_path = Path("./docs/graph.svg" )
        # output_path.open("w", encoding="utf-8").write(svg)

        # # bnersem awl so2al mn el list of as2ela
        # question_mloosh_lazma = ""
        # for question in questions_mlhash_lazma:
        #     question_mloosh_lazma = question_mloosh_lazma + question.lower() + " "

        # svg = displacy.render(self.nlp(question_mloosh_lazma), style="dep", jupyter=False)
        # output_path = Path("./docs/question_graph.svg" )
        # output_path.open("w", encoding="utf-8").write(svg)


        for sent in text.sents:
            prev_subj, compound_is, last_word = "", "", ""

            dep_word = [word.dep_ for word in sent]     # hyraga3 kol kelma no3ha eih (subject, adjective, kda y3ny)
            word_dep_count_subj = [dep_word.index(word) for word in dep_word if word in ('nsubj', 'subj', 'nsubjpass')]
            # list of el indices beta3t el subject b kol anwa3o b2a

            # e7na shakeen fl 7eta dyh, hal yo2sod index wala length
            try:
                word_dep_count_subj = word_dep_count_subj[-1] + 1
            except IndexError:
                word_dep_count_subj = 1

            more_subjs = [word for word in dep_word if word in ('nsubj', 'subj', 'nsubjpass')]
            # 8albn htraga3 nafs elly el fo2 byraga3o, bs el kelma nafsaha bdl el index
            for word in sent:
                
                    
                if len(more_subjs) > 1:
                    if word.dep_ in more_subjs:
                        if word.dep_ in ['nsubjpass']:
                            break
                        elif word.dep_ in ('nsubj','subj'):
                            if word_dep_count_subj > 0:
                                # """ IN prime minister it gives compound and then nmod """
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
                                        if str(word) not in ('he', 'she', 'it'):
                                            prev_subj = str(word)
                                            if str(pronoun[0]) not in ('his','her', 'its'):
                                                prev_subjs = [prev_subj]
                                                official_subject = prev_subjs[0]
                                                word_dep_count_subj = word_dep_count_subj - 1

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
                                    if str(word) in ('he', 'she', 'it'):
                                        # print(prev_subjs)
                                        new_word = prev_subjs[-1]
                                        # sentences.append(str(sent).replace(str(word), str(new_word)))
                                        sentences.append(re.sub(r'\b' + str(word) + r'\b', str(new_word), str(sent)))
                                        
                                        flag = False

                                    if pronoun and str(pronoun[0]) in ('his','her', 'its'):
                                        new_word = str(official_subject)+"\'s"
                                        # sentences.append(str(sent).replace((str(pronoun[0])), str(new_word)))
                                        sentences.append(re.sub(r'\b' + str(pronoun[0]) + r'\b', str(new_word), str(sent)))
                                        flag = False


                                elif word.dep_ in ('nsubj','subj','nsubjpass') and str(word) not in ('he', 'she', 'it'):
                                    last_word = word
                                else:
                                    pass
                else:
                    if word_dep_count_subj > 0:
                        # """ IN prime minister it gives compound and then nmod """
                        if word.dep_ in ('compound') or word.dep_ in ('nmod', 'amod'):
                            # byshoof lw hya compound, el howa Leonardo DiCaprio mtlhn, fa 
                            # 3ayez y3amel el kelmetein 3la enohom 7aga wa7da
                            if compound_is == "":       # dyh awl kelma fl compound kda
                                compound_is = str(word)
                                word_dep_count_subj = word_dep_count_subj - 1
                            else:   # msh awl kelma, fa zawedha 3l mwgood w 5las
                                compound_is = compound_is+ " " +str(word)
                                word_dep_count_subj = word_dep_count_subj - 1

                        elif word.dep_ in ('nsubj', 'subj', 'nsubjpass'):
                            pronoun = [i for i in word.subtree]

                            if compound_is == "":
                                if str(word) not in ('he', 'she', 'it'):
                                    prev_subj = str(word)
                                    if str(pronoun[0]) not in ('his','her', 'its'):
                                        prev_subjs = [prev_subj]
                                        official_subject = prev_subjs[0]        # dh el subject bta3 el gomal el b3deeha y3ny
                                        word_dep_count_subj = word_dep_count_subj - 1

                            else:
                                if str('poss') in [str(i.dep_) for i in word.subtree]:  # poss: his, her, kda y3ny
                                    # babtedy abny el compound y3ny
                                    prev_subj = compound_is
                                    word_dep_count_subj = word_dep_count_subj - 1
                                    prev_subjs = [prev_subj]
                                    # official_subject = prev_subjs[0]
                                else:
                                    # bzawed Dicaprio 3la Leonardo w yb2a dh kda el subject
                                    # fl gomal el gya, hasheel he/she w a7ot el subject dh (2a5er subject 3mlto)
                                    prev_subj = compound_is+" "+str(word)
                                    word_dep_count_subj = word_dep_count_subj - 1
                                    prev_subjs = [prev_subj]
                                    official_subject = prev_subjs[0]

                            # if str(word) in ('they'):
                                # subject_list.extend([str(a.text) for a in word.subtree if a.dep_ in ('conj')])
                            if str(word) in ('he', 'she', 'it'):
                                # hasheel kelmet he/she, w ha7ot el subject Leonardo Dicaprio mthln
                                # print(prev_subjs)
                                new_word = prev_subjs[-1]
                                # print(new_word)
                                # sentences.append(str(sent).replace(str(word), str(new_word)))       # el replace el mfrood yt2kd enaha kelma kamla, msh goz2 mn kelma asln
                                sentences.append(re.sub(r'\b' + str(word) + r'\b', str(new_word), str(sent)))
                                flag = False    # 5ly el flag false 3lshan my3mlsh append tany ta7t

                            if pronoun and str(pronoun[0]) in ('his','her', 'its'):           # hysheel his w y7ot Leonardo DiCaprio's
                                # most likely ne2dar ndom el etnein ifs el gayeen fy 7aga wa7da. el mo3aq 3amel bracket zyada bs (mloosh lazma 8albn) (DONE)
                                # print(official_subject)
                                new_word = str(official_subject)+"\'s"
                                # print(new_word)
                                # sentences.append(str(sent).replace((str(pronoun[0])), str(new_word)))
                                sentences.append(re.sub(r'\b' + str(pronoun[0]) + r'\b', str(new_word), str(sent)))
                                flag = False
                                


                        elif word.dep_ in ('nsubj','subj','nsubjpass') and str(word) not in ('he', 'she', 'it'):
                            last_word = word
                        else:
                            pass


            if flag:
                sentences.append(str(sent))     # 3mlnalha append fy 7eta tanya, fa msh hn3ml hena tany
            else:
                flag = True

        resolved_text = " ".join(sentences)
        # print(resolved_text)
        return resolved_text

    def check_for_multi_and_(self, sentence):
        x = []
        count = 0
        for word in sentence:
            # print([i for i in word.subtree])
            count += 1
            if word.dep_ in ('cc'):
                x.append(count-1)

        depen = []
        for i in x:
            depen.append([word.dep_ for word in sentence[:i]])

        senten1, senten2 = "", ""
        list2 = ["nsubj", "ROOT", "dobj"]
        # , ["subj", "ROOT", "dobj"], ["subj", "ROOT", "pobj"], ["nsubj", "ROOT", "obj"], ["nsubj", "ROOT", "dobj"], ["nsubj", "ROOT", "pobj"], ["nsubjpass", "ROOT", "obj"], ["nsubjpass", "ROOT", "dobj"], ["nsubjpass", "ROOT", "pobj"]]

        for list1 in depen:
            check = all(item in list1 for item in list2)

            if check:
                return True, depen, x

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


                senten1 = " ".join(p1)
                senten2 = " ".join(p2)

                senten1 = self.nlp(senten1)
                senten2 = self.nlp(senten2)

        return str(senten1), str(senten2)


if __name__ == "__main__":
    test = change_nouns()
    sentences = test.resolved("The Normans (Norman: Nourmands; French: Normands; Latin: Normanni) were the people who in the 10th and 11th centuries gave their name to Normandy, a region in France. They were descended from Norse (\"Norman\" comes from \"Norseman\") raiders and pirates from Denmark, Iceland and Norway who, under their leader Rollo, agreed to swear fealty to King Charles III of West Francia. Through generations of assimilation and mixing with the native Frankish and Roman-Gaulish populations, their descendants would gradually merge with the Carolingian-based cultures of West Francia. The distinct cultural and ethnic identity of the Normans emerged initially in the first half of the 10th century, and it continued to evolve over the succeeding centuries.")
    print(sentences)

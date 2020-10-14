def getPOSTag(colType, posTag):
    if colType == 'NOUN+VERB':
        verbPOSTags = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
        nounPOSTags = ['NN', 'NNS']
        if posTag in verbPOSTags:
            return 'VERB'
        elif posTag in nounPOSTags:
            return 'NOUN'

    elif colType == 'NOUN+NOUN':
        return 'NOUN'

    elif colType == 'NOUN+PREP' or colType == 'PREP+NOUN':
        nounPOSTags = ['NN', 'NNS']
        prepPOSTags = ['IN', 'RP']
        if posTag in nounPOSTags:
            return 'NOUN'
        elif posTag in prepPOSTags:
            return 'PREP'

    elif colType == 'ADJ+NOUN':
        nounPOSTags = ['NN', 'NNS']
        adjPOSTags = ['JJ', 'JJR', 'JJS', 'VBG', 'VBN', 'RB', 'RBR', 'RBS']
        if posTag in nounPOSTags:
            return 'NOUN'
        elif posTag in adjPOSTags:
            return 'ADJ'

    elif colType == 'DET+NOUN':
        nounPOSTags = ['NN', 'NNS']
        detPOSTags = ['DT', 'WDT', 'WP', 'PDT', 'PRP$', 'WP$']
        if posTag in nounPOSTags:
            return 'NOUN'
        elif posTag in detPOSTags:
            return 'DET'

    elif colType == 'VERB+NOUN':
        verbPOSTags = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
        nounPOSTags = ['NN', 'NNS', 'NNP', 'NNPS']
        if posTag in verbPOSTags:
            return 'VERB'
        elif posTag in nounPOSTags:
            return 'NOUN'

    elif colType == 'VERB+ADJ':
        verbPOSTags = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
        adjPOSTags = ['JJ', 'JJR', 'JJS']
        if posTag in verbPOSTags:
            return 'VERB'
        elif posTag in adjPOSTags:
            return 'ADJ'

    elif colType == 'VERB+PREP':
        verbPOSTags = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
        prepPOSTags = ['IN', 'RP']
        if posTag in verbPOSTags:
            return 'VERB'
        elif posTag in prepPOSTags:
            return 'PREP'

    elif colType == 'VERB+VERB':
        return 'VERB'

    elif colType == 'ADV+VERB':
        verbPOSTags = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
        advPOSTags = ['RB', 'RBR', 'RBS', 'RP', 'WRB']
        if posTag in verbPOSTags:
            return 'VERB'
        elif posTag in advPOSTags:
            return 'ADV'

    elif colType == 'ADV+toVERB':
        advPOSTags = ['RB', 'RBR', 'RBS', 'WRB']
        verbPOSTags = ['VB']
        if posTag in advPOSTags:
            return 'ADV'
        elif posTag in verbPOSTags:
            return 'toVERB'

    elif colType == 'ADJ+toVERB':
        adjPOSTags = ['JJ', 'JJR', 'JJS']
        verbPOSTags = ['VB']
        if posTag in verbPOSTags:
            return 'toVERB'
        elif posTag in adjPOSTags:
            return 'ADJ'

    elif colType == 'ADJ+PREP':
        adjPOSTags = ['JJ', 'JJR', 'JJS', 'VBG', 'VBN']
        prepPOSTags = ['IN', 'RP']
        if posTag in adjPOSTags:
            return 'ADJ'
        elif posTag in prepPOSTags:
            return 'PREP'

    elif colType == 'ADV+ADJ':
        adjPOSTags = ['JJ', 'JJR', 'JJS']
        advPOSTags = ['RB', 'RBR', 'RBS', 'WRB']
        if posTag in adjPOSTags:
            return 'ADJ'
        elif posTag in advPOSTags:
            return 'ADV'

def getHeadPOSDepRelDepPOS(colType):
    filterRelDepHeadWordPOSTags = []
    if colType == 'NOUN+VERB':
        headWordPOSTags = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
        dependencyRelations = ['nsubj']
        dependentPOSTags = ['NN', 'NNS']
        filterRelDepHeadWordPOSTags.append((headWordPOSTags, dependencyRelations, dependentPOSTags))

        headWordPOSTags = ['NN', 'NNS']
        dependencyRelations = ['acl']
        dependentPOSTags = ['VBG']
        filterRelDepHeadWordPOSTags.append((headWordPOSTags, dependencyRelations, dependentPOSTags))

    elif colType == 'NOUN+NOUN':
        headWordPOSTags = ['NN', 'NNS', 'NNP', 'NNPS', 'VBG']
        dependencyRelations = ['compound', 'conj', 'poss', 'nmod', 'amod', 'npadvmod']
        dependentPOSTags = ['NN', 'NNS', 'NNP', 'NNPS', 'VBG']
        filterRelDepHeadWordPOSTags.append((headWordPOSTags, dependencyRelations, dependentPOSTags))

    elif colType == 'NOUN+PREP':
        headWordPOSTags = ['NN', 'NNS']
        dependencyRelations = ['prep']
        dependentPOSTags = ['IN', 'RP']
        filterRelDepHeadWordPOSTags.append((headWordPOSTags, dependencyRelations, dependentPOSTags))

    elif colType == 'PREP+NOUN':
        headWordPOSTags = ['IN', 'RP']
        dependencyRelations = ['pobj']
        dependentPOSTags = ['NN', 'NNS']
        filterRelDepHeadWordPOSTags.append((headWordPOSTags, dependencyRelations, dependentPOSTags))

    elif colType == 'ADJ+NOUN':
        headWordPOSTags = ['NN', 'NNS']
        dependencyRelations = ['amod', 'nmod', 'compound', 'advmod']
        dependentPOSTags = ['JJ', 'JJR', 'JJS', 'VBG', 'VBN', 'RB', 'RBR', 'RBS']
        filterRelDepHeadWordPOSTags.append((headWordPOSTags, dependencyRelations, dependentPOSTags))

    elif colType == 'DET+NOUN':
        headWordPOSTags = ['NN', 'NNS']
        dependencyRelations = ['num', 'det', 'predet', 'nmod']
        dependentPOSTags = ['DT', 'WDT', 'WP', 'PDT', 'PRP$', 'WP$']
        filterRelDepHeadWordPOSTags.append((headWordPOSTags, dependencyRelations, dependentPOSTags))

    elif colType == 'VERB+NOUN':
        headWordPOSTags = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
        dependencyRelations = ['attr', 'dobj', 'dative', 'oprd', 'ccomp', 'nsubjpass']
        dependentPOSTags = ['NN', 'NNS', 'NNP', 'NNPS']
        filterRelDepHeadWordPOSTags.append((headWordPOSTags, dependencyRelations, dependentPOSTags))

        headWordPOSTags = ['NN', 'NNS', 'NNP', 'NNPS']
        dependencyRelations = ['acl', 'relcl', 'advcl']
        dependentPOSTags = ['VB', 'VBN']
        filterRelDepHeadWordPOSTags.append((headWordPOSTags, dependencyRelations, dependentPOSTags))

        headWordPOSTags = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
        dependencyRelations = ['pobj']
        dependentPOSTags = ['NN', 'NNS']
        filterRelDepHeadWordPOSTags.append((headWordPOSTags, dependencyRelations, dependentPOSTags))

    elif colType == 'VERB+ADJ':
        headWordPOSTags = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
        dependencyRelations = ['acomp', 'oprd', 'ccomp', 'amod']
        dependentPOSTags = ['JJ', 'JJR', 'JJS']
        filterRelDepHeadWordPOSTags.append((headWordPOSTags, dependencyRelations, dependentPOSTags))

        headWordPOSTags = ['JJ', 'JJR', 'JJS']
        dependencyRelations = ['auxpass']
        dependentPOSTags = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
        filterRelDepHeadWordPOSTags.append((headWordPOSTags, dependencyRelations, dependentPOSTags))

    elif colType == 'VERB+PREP':
        headWordPOSTags = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
        dependencyRelations = ['agent', 'prep', 'dative']
        dependentPOSTags = ['IN', 'RP']
        filterRelDepHeadWordPOSTags.append((headWordPOSTags, dependencyRelations, dependentPOSTags))

    elif colType == 'VERB+VERB':
        headWordPOSTags = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ', 'MD']
        dependencyRelations = ['xcomp', 'ccomp', 'aux']
        dependentPOSTags = ['VB', 'VBG', 'MD']
        filterRelDepHeadWordPOSTags.append((headWordPOSTags, dependencyRelations, dependentPOSTags))

    elif colType == 'ADV+VERB':  # 'VERB+ADV':
        headWordPOSTags = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
        dependencyRelations = ['advmod', 'expl', 'npadvmod', 'prt', 'neg']
        dependentPOSTags = ['RB', 'RBR', 'RBS', 'RP', 'WRB']
        filterRelDepHeadWordPOSTags.append((headWordPOSTags, dependencyRelations, dependentPOSTags))

    elif colType == 'ADV+toVERB':
        headWordPOSTags = ['RB', 'RBR', 'RBS', 'WRB']
        dependencyRelations = ['xcomp']
        dependentPOSTags = ['VB']
        filterRelDepHeadWordPOSTags.append((headWordPOSTags, dependencyRelations, dependentPOSTags))

    elif colType == 'ADJ+toVERB':
        headWordPOSTags = ['JJ', 'JJR', 'JJS']
        dependencyRelations = ['xcomp']
        dependentPOSTags = ['VB']
        filterRelDepHeadWordPOSTags.append((headWordPOSTags, dependencyRelations, dependentPOSTags))

    elif colType == 'ADJ+PREP':
        headWordPOSTags = ['JJ', 'JJR', 'JJS', 'VBG', 'VBN']
        dependencyRelations = ['prep']
        dependentPOSTags = ['IN', 'RP']
        filterRelDepHeadWordPOSTags.append((headWordPOSTags, dependencyRelations, dependentPOSTags))

    elif colType == 'ADV+ADJ':
        headWordPOSTags = ['JJ', 'JJR', 'JJS']
        dependencyRelations = ['advmod', 'npadvmod', 'neg']
        dependentPOSTags = ['RB', 'RBR', 'RBS', 'WRB']
        filterRelDepHeadWordPOSTags.append((headWordPOSTags, dependencyRelations, dependentPOSTags))

    return filterRelDepHeadWordPOSTags

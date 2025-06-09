def generer_mention(moyenne):
    if moyenne >= 16:
        return "Très bien"
    elif moyenne >= 14:
        return "Bien"
    elif moyenne >= 12:
        return "Assez bien"
    elif moyenne >= 10:
        return "Passable"
    else:
        return "Insuffisant"

def generer_appreciation(moyenne):
    if moyenne >= 16:
        return "Excellent travail, continue ainsi."
    elif moyenne >= 14:
        return "Très bon ensemble, peut viser l'excellence."
    elif moyenne >= 12:
        return "Bon travail, encore des efforts à fournir."
    elif moyenne >= 10:
        return "Résultats acceptables, attention à maintenir le cap."
    else:
        return "Travail insuffisant, redoubler d'effort."

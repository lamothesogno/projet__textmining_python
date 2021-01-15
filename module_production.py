# -*- coding: utf-8 -*-
"""
Created on Thu Jan 14 18:16:07 2021

@author: vince
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Jan 14 15:34:15 2021

@author: vince
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 08/05/2020

@author: Vincent Sogno et Dorian Lamothe
"""

################################## Déclaration des classes ##################################

import datetime as dt
import pandas
import praw
from sklearn.feature_extraction.text import TfidfVectorizer
import matplotlib.pyplot as plt
#On importe toutes nos library au début, datetime pour des dates plus maniable. Pandas pour les dataFrame
#praw pour l'API reddit, sklearn pour calculer automatiquement le tfidf et matplotlib pour afficher des plots.

class Corpus():
    
    def __init__(self,name, listemot):
        self.name = name
        self.collection = {}
        self.id2doc = {}
        self.ndoc = 0
        self.naut = 0
        self.corpusentier = []
        self.listemot = listemot
        self.date = {}
        #Dans la fonction init pas grand chose de particulier, on viens prendre en entré
        #la liste de mot qu'a entré l'utilisateur. J'ai également rajouté quelques champs mots,
        #corpusentier et date dont on verra l'utilité plus tard.
    def add_doc(self, doc):
        
        self.collection[self.ndoc] = doc
        self.id2doc[self.ndoc] = doc.get_title()
        self.date[self.ndoc] = doc.get_date()
        #add_doc avait été créé en TD
        #On recupere chaque element de doc qui nous interesse
        #On incremente la clef des dictionnaires avec ndoc
        #On y a ajouter la recuperation de la date pour pouvoir faire des traitements dessus
        self.ndoc += 1  
        
    def nettoyer_texte(self,texte):
        textemin = texte.lower()
        textemin = textemin.replace("\n"," ")
        textemin = textemin.replace("."," ")
        textemin = textemin.replace("-"," ")
        textemin = textemin.replace(","," ")
        textemin = textemin.replace("?"," ")
        textemin = textemin.replace("!"," ")
        return textemin
        #La fonction nettoyer texte srt à simplifier le texte et enlevé la ponctuation afin que tout soit pareil.
        #Elle renvoie une version epuré du texte d'entré
        
    def corpusentcrea(self,annee,mois,jour):
        #Cette fonction a pour but de regrouper les differents posts en une liste de deux corpus de texte.
        #La premiere partie sera celle avant la date indiqué par l'utilisateur.
        #La deuxieme partie  sera celle apres la date entré par l'utilisateur.
        if (self.corpusentier == []):
            #Comme on peut executer plusieurs fois la fonction 
            #On vient d'abord verifier que corpusentier est vide aifn d'éviter de perdre du temps
            corpus1 = ""
            corpus2 = ""
            #On initialise nos deux corpus
            temps1=dt.datetime(annee,mois,jour)
            #On crée temps1 la variable qui contient la date qu'a entré l'utilisateur
            #On récupère les parametre de la methode avec les parametre qu'on a mis en entré de la méthode corpusentcrea
            for i in range(len(self.collection)):
                #On boucle sur la collection
                txt = self.collection[i].get_text()
                #On récupère le texte de la collection dans txt
                txt = Corpus.nettoyer_texte(self,txt)
                #On nettoie txt de ses majuscules, traits d'union, points d'interrogation, virgule, etc 
                if self.date[i] < temps1:
                    #Si le post date d'avant la date indiqué par l'utilisateur
                    corpus1 += (txt)
                    #On l'ajoute au 1er corpus
                else:
                    #Sinon
                    corpus2 += (txt)
                    #On l'ajoute au deuxieme corpus
            self.corpusentier.append(corpus1)
            self.corpusentier.append(corpus2)
            #Une fois que tous les documents ont été repartis on les ajoute à la liste corpusentier.
            
    def stats(self,annee,mois,jour):
        Corpus.corpusentcrea(self,annee,mois,jour)
        #On apelle d'abord corpusentcrea pour créer notre corpus 
        mots = self.corpusentier[0].split(' ') + self.corpusentier[1].split(' ')
        #On crée ensuite la variable mot qui prends tous les mots utilisés dans les deux corpus en entrée.
        data = pandas.DataFrame(mots)
        #On les rentre dans un dtaaframe pour pouvoir les compter
        compte = data[0].value_counts()
        #On crée la chaîne à retourner
        chaine = ""
        #Et ensuite on les compte
        for i in range(len(compte)):
            for j in self.listemot:
                #On boucle sur le compte et sur la liste de mot que l'utilisateur à entrer
                if compte.index[i] == j:
                    #Si l'index du compte (contenant les mots) est egal au mot de la liste utilisateur
                    chaine = chaine + "Mot recherché : " + str(compte.index[i]) + " Nombres d'apparition : " + str(compte[i]) + " Fréquence d'apparition : " + str(compte[i]/len(mots))+"\n"
                    #On renvoie le mot recherché, son nombre d'apparition et sa fréquence d'apparition
        return chaine
                    
    def tfidf(self,annee,mois,jour):
        Corpus.corpusentcrea(self,annee,mois,jour)
        #On apelle notre methode coorpusentcrea pour creer le corpus si on ne l'a pas encore fait.
        vectorizer = TfidfVectorizer()
        vectors = vectorizer.fit_transform([self.corpusentier[0],self.corpusentier[1]])
        feature_names = vectorizer.get_feature_names()
        dense = vectors.todense()
        denselist = dense.tolist()
        #Cette suite de commande permet de calculer le tfidf via la methode TfidfVectorizer de sklearn.
        #Je comprends globalement c equ'elle fait, regorupement de mot, attribution d'un score, transformation en liste
        #Mais je ne sais pas exactement quelle commande fait quoi.
        #Nous l'avons trouver sur un site:“https://towardsdatascience.com/natural-language-processing-feature-engineering-using-tf-idf-e8b9d00e7e76” 
        df = pandas.DataFrame(denselist, columns=feature_names)
        df.index = ("avant","apres")
        #print(df)
        #On met ensuite nos resultats dans un dataframe
        listescore=[]
        for i in range(len(df.iloc[0,])):
            for j in range(len(self.listemot)):
                #On boucle sur les colonnes du dataframe et sur la liste d emot entré par l'utilisateur
                if df.columns[i] == self.listemot[j]: 
                    
                    #Si le nom des colonne du data frame et un mot de la liste de mot sont les meme
                    #On affiche les informations de la colonne
                    listescore.append([df.iloc[0,i],df.iloc[1,i],self.listemot[j]])
                    #On cree un tuple avec le score du mot dans les post avant la date entre par l'utilisateur
                    #Et le mot de l'utilisatuer associé
        return listescore
        #On retourne enfin notre liste de score afin de pouvoir construire des plot et des chaine de caractere avec.
        


class Document():
    
    # On construit notre classe document
    def __init__(self, date, title, author, text, url):
        self.date = date
        self.title = title
        self.author = author
        self.text = text
        self.url = url
    
    # On recupere authors, title, date, source et text avec les getters suivant
    
    def get_author(self):
        return self.author

    def get_title(self):
        return self.title
    
    def get_date(self):
        return self.date
    
    def get_source(self):
        return self.source
        
    def get_text(self):
        return self.text
    
class RedditDocument(Document):
    #La classe RedditDocument herite de la classe Document
    def __init__(self, nbcom,date,title,author,text,url):
        self.nbcom = nbcom
        #On ajoute le nbcom par rapport à document
        super().__init__(date,title,author,text,url)
        #Puis avec la fonction super on recupere les attributs de Document
    
    def getnbcom(self):
        return self.nbcom
        #On recupere le nombre de commentaire
    
    def setnbcom(self, nbcome):
        self.nbcom = nbcome
        #On peut definir le nombre de commentaire
    
    def __str__(self):
        return "RedditDocument " + self.getType() + " : " + self.title + " ,nombre de commentaire:" + self.nbcom
        #La fonction __str__ renvoie une chaine quand  onprint(RedditDocument)
    
class ArxivDocument(Document):
    #La classe ArxivDocument herite de la classe Document
    def __init__(self, coauteur,date,title,author,text,url):
        self.coauteur = coauteur
        #On ajoute une variable co auteur
        super().__init__(date,title,author,text,url)
        #Puis avec la fonction super on recupere les attirbuts de Document
    def __str__(self):
        return "RedditDocument " + self.getType() + " : " + self.title + " ,Co-auteurs:" + self.coauteur
         #On y ajout eune fonction str
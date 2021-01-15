# -*- coding: utf-8 -*-
"""
Created on Wed Jan 13 14:14:49 2021

@author: lamot
"""


from tkinter.messagebox import *

try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk

try:
    import ttk
    py3 = False
except ImportError:
    import tkinter.ttk as ttk
    py3 = True

import os
os.chdir("C:/Users/lamot/OneDrive/Bureau/M1 Info/Projet_Python")

import urllib   
import xmltodict 
import praw
import module_production as tmp
import datetime as dt
import matplotlib.pyplot as plt

######################### FONCTIONS INTERFACE

def getElement():
    
    #Fonction associée au bouton exécuter 
    
    #Recupere les valeurs entrées dans le formulaire de saisie
    
    subreddit_name = Entrysub.get()
    arxvis_name = Entrykw.get()
    nb_doc_red = Entry_nb_doc.get()
    nb_doc_arx = Entry_nb_doc_arx.get()
    motcle = KW_entry.get().lower()
    date = date_entry.get()
    stats = check_stats_var.get()
    tfidf = check_tfidf_var.get()
    

    #CONSTRUCTION DU CORPUS
        
    if nb_doc_red != 0 and subreddit_name =="" :
        tk.messagebox.showerror(title="Erreur - Nom du subreddit",message="Vous n'avez pas spécifié le nom du subreddit !")
    
    elif nb_doc_arx != 0 and arxvis_name =="" :
        tk.messagebox.showerror(title="Erreur - Mot-clé ArxVis",message="Vous n'avez pas spécifié le mot-clé ArxVis !")
    
    elif nb_doc_arx == 0 and arxvis_name !="" :
        tk.messagebox.showerror(title="Erreur - Nombre de documents ArxVis",message="Vous n'avez pas spécifié le nombre de documents ArxVis !")

    elif nb_doc_red == 0 and subreddit_name !="" :
        tk.messagebox.showerror(title="Erreur - Nombre de documents Reddit",message="Vous n'avez pas spécifié le nombre de documents Reddit !")
        
    elif nb_doc_red == 0 and nb_doc_arx==0 and subreddit_name=="" and arxvis_name=="" :
        tk.messagebox.showerror(title="Erreur - Documents",message="Vous n'avez pas spécifié la source et le nombre de documents !")
        
    elif motcle == "" :
        tk.messagebox.showerror(title="Erreur - Mot-Clé",message="Vous n'avez pas renseigné de mot-clé !")
    
    elif date == "" :
        tk.messagebox.showerror(title="Erreur - Date",message="Vous n'avez pas renseigné la date !")
        
    elif stats==0 and tfidf==0 :
        tk.messagebox.showerror(title="Erreur - Choix d'analyse",message="Vous n'avez pas soécifié d'analyse souhaitée !")
    
    
    #On a vérifié l'ensemble des conditions nécessaires. On passe à la création du corpus
    
    
    else:
        
        listemot = motcle.split(" ")
        corpus = tmp.Corpus(name="Corpus",listemot=listemot)
        annee = int(date.split("/")[2])
        mois = int(date.split("/")[1])
        jour = int(date.split("/")[0])
        
        if nb_doc_arx != 0 :
            url = 'http://export.arxiv.org/api/query?search_query=all:' + str(arxvis_name) + '&start=0&max_results='+ str(nb_doc_arx)
            data =  urllib.request.urlopen(url).read().decode()
            docs = xmltodict.parse(data)['feed']['entry']
            
            for i in docs:
                datet = dt.datetime.strptime(i['published'], '%Y-%m-%dT%H:%M:%SZ')
                try:
                    author = [aut['name'] for aut in i['author']][0]
                except:
                    author = i['author']['name']
                txt = i['title']+ ". " + i['summary']
                txt = txt.replace('\n', ' ')
                txt = txt.replace('\r', ' ')
                doc = tmp.Document(datet,
                                   i['title'],
                                   author,
                                   txt,
                                   i['id']
                                   )
                corpus.add_doc(doc=doc)
                  
        
        if nb_doc_red != 0 :
            reddit = praw.Reddit(client_id='27Z9eTriLffuOg', client_secret='sAgpmMo_ZYuRnOTrIWq1pJBEYgs', user_agent='td1')
            hot_posts = reddit.subreddit(subreddit_name).hot(limit=nb_doc_red)
            
            for post in hot_posts:
                datet = dt.datetime.fromtimestamp(post.created)
                txt = post.title + ". "+ post.selftext
                txt = txt.replace('\n', ' ')
                txt = txt.replace('\r', ' ')
                doc = tmp.Document(datet,
                                   post.title,
                                   post.author_fullname,
                                   txt,
                                   post.url)
                corpus.add_doc(doc=doc)
        
        if stats==1:
        
            statswindow = tk.Tk()
            
            statswindow.geometry("700x500") 
      
            statswindow.title("Interface de résultat - Stats") 
            statswindow.config(background="#41B77F")
            titre_stats = tk.Label(statswindow, text ='Fréquence des mots demandés',bg='#41B77F',font=("HP Simplified", 14))
            titre_stats.place(relx = 0.5, 
                              rely = 0.1,
                              anchor = 'center')
            
            test_stats = tk.Label(statswindow,text=corpus.stats(annee,mois,jour),bg='#41B77F',font=("HP Simplified", 10))
            test_stats.place(relx = 0.5, 
                              rely = 0.5,
                             anchor = 'center')    
            
            statswindow.mainloop()
        
        if tfidf == 1:
            
            # Création interface TFxIDF
            
            tfidfwindow = tk.Tk()
            tfidfwindow.geometry("700x500")
            tfidfwindow.title("Interface de résultat - TFxIDF")
            tfidfwindow.config(background="#41B77F")
            
            titre_tfidf = tk.Label(tfidfwindow, text ='TFxIDF',bg='#41B77F',font=("HP Simplified", 14))
            titre_tfidf.place(relx = 0.5, 
                              rely = 0.1,
                              anchor = 'center')            
            
            # Utilisation fonction TFxIDF de la classe Corpus et nouvelle variable pour adapter l'affichage
            
            listescores = corpus.tfidf(annee, mois, jour)

            chainescore=""
            for i in range(len(listescores)):
                plt.plot([1,2], (listescores[i][0],listescores[i][1]), label = listescores[i][2])
                chainescore = chainescore + "Mot choisi : " + str(listescores[i][2]) + " \n Score avant la date précisé : " + str(listescores[i][0])+ "\n Score après la date précisé : " + str(listescores[i][1]) + "\n"
            
            # Récupération des plots dans l'IDE
                
            plt.legend()
            plt.show()
            
            # Affichage résultats
            
            test_tfidf = tk.Label(tfidfwindow,text=chainescore,bg='#41B77F',font=("HP Simplified", 10))
            test_tfidf.place(relx = 0.5, 
                              rely = 0.5,
                             anchor = 'center')    
            
            tfidfwindow.mainloop()
            

################################## INTERFACE DE SAISIE #######################################
    
root = tk.Tk()

root.geometry("340x605")
root.config(background="#41B77F")
root.title("Interface Projet Python")

# LABEL TITRE

Label_titre = tk.Label(root, text ='Outil de text mining',bg='#41B77F',font=("HP Simplified", 20))
Label_titre.place(relx = 0.5, 
                   rely = 0.05,
                   anchor = 'center')

# LABEL & INPUT SUBREDDIT

titre_red = tk.Label(root,
                   text="Reddit",
                   bg = '#41B77F',
                   font=("HP Simplified", 14))
titre_red.place(relx = 0.5,
                 rely = 0.12,
                 anchor= 'center')

nomsub = tk.Label(root,
                   text="Nom du SubReddit",
                   bg = '#41B77F',
                   font=("HP Simplified", 12))
nomsub.place(relx = 0.5,
                 rely = 0.17,
                 anchor= 'center')

Entrysub = tk.Entry(root)
Entrysub.place(relx = 0.5,
                 rely = 0.2,
                 anchor= 'center')

nbdoc = tk.Label(root,
                   text="Nombre de documents",
                   bg = '#41B77F',
                   font=("HP Simplified", 12))
nbdoc.place(relx = 0.5,
                 rely = 0.25,
                 anchor= 'center')

Entry_nb_doc = tk.Scale(root, orient='horizontal', from_=0, to=1000, 
                        resolution=1, tickinterval=200, length=250,bg='#41B77F',bd=0)      
Entry_nb_doc.place(relx=0.5,rely=0.32, bordermode='ignore',anchor='center')

# LABEL & INPUT ARXVIS

titre_arx = tk.Label(root,
                   text="Arxvis",
                   bg = '#41B77F',
                   font=("HP Simplified", 14))
titre_arx.place(relx = 0.5,
                 rely = 0.42,
                 anchor= 'center')

arxvis_kw = tk.Label(root,
                   text="Mot-clé Arxvis",
                   bg = '#41B77F',
                   font=("HP Simplified", 12))
arxvis_kw.place(relx = 0.5,
                 rely = 0.47,
                 anchor= 'center')

Entrykw = tk.Entry(root)
Entrykw.place(relx = 0.5,
                 rely = 0.5,
                 anchor= 'center')

nbdoc_arx = tk.Label(root,
                   text="Nombre de documents",
                   bg = '#41B77F',
                   font=("HP Simplified", 12))
nbdoc_arx.place(relx = 0.5,
                 rely = 0.55,
                 anchor= 'center')

Entry_nb_doc_arx = tk.Scale(root, orient='horizontal', from_=0, to=1000, 
                        resolution=1, tickinterval=200, length=250,bg='#41B77F',bd=0)      
Entry_nb_doc_arx.place(relx=0.5,rely=0.62, bordermode='ignore',anchor='center')

#Analyse des mots

analyse_mot = tk.Label(root,
                   text="Analyse des mots (séparés par des espaces)",
                   bg = '#41B77F',
                   font=("HP Simplified", 14))

analyse_mot.place(relx = 0.5,
                 rely = 0.72,
                 anchor= 'center')

KW_entry = tk.Entry(root)
KW_entry.place(relx = 0.5,
                 rely = 0.75,
                 anchor= 'center')

#Date

date_label = tk.Label(root,
                   text="Date pivot (sous la forme JJ/MM/AAAA)",
                   bg = '#41B77F',
                   font=("HP Simplified", 14))

date_label.place(relx = 0.5,
                 rely = 0.82,
                 anchor= 'center')

date_entry = tk.Entry(root)
date_entry.place(relx = 0.5,
                 rely = 0.85,
                 anchor= 'center')

#Analyse(s) souhaitée(s)

check_stats_var = tk.IntVar()
check_tfidf_var = tk.IntVar()

check_stats = tk.Checkbutton(root,onvalue = 1, offvalue = 0,text = "Statistiques",bg='#41B77F',var=check_stats_var)
check_tfidf = tk.Checkbutton(root,onvalue=1,offvalue=0,text="TFxIDF",bg='#41B77F',var=check_tfidf_var)
check_stats.place(relx=0.2, rely=0.88, bordermode='ignore')
check_tfidf.place(relx=0.6, rely=0.88, bordermode='ignore')

#Bouton exécuter

execute = tk.Button(root,text="Analyser",bg="white",command=(lambda:getElement()))
execute.place(relx=0.42,rely=0.95,bordermode='ignore')

root.mainloop()
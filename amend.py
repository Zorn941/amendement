from PyPDF2 import PdfReader, PdfWriter, PdfMerger
import os

def recupere_amend(texte):
    ligne=texte.partition('\n')
    ligne=ligne[0].partition('° ')
    ligne=ligne[2].replace(" ","")
    return ligne

def recupere_page(texte): # Renvoi la page et le nombre de pages de l'amendement
    ligne=texte.partition('\n')
    li=ligne[0].partition('/')
    #print(li)
    if str.isnumeric(li[0]):
        page=li[0]
        nombre=li[2]
        nombre=nombre[0]
    else:
        li=ligne[len(ligne)-1].partition('/')
        if str.isnumeric(li[0]):
            page=li[0]
            nombre=li[2]
            nombre=nombre[0]
        else:
            page,nombre=-1,-1
            print(li)
    return int(page),int(nombre)

def position(texte):
    ligne=texte.partition('\n')
    li=ligne[0].partition('/')
    position=li[2]
    position=position[1:]
    position=position.partition(' N°')
    position=position[0]
    return position

def origine(texte):
    tab_texte=texte.split('\n')
    #print(tab_texte)
    i=0
    redacteurs=""
    while i<len(tab_texte)-1:
        if "présenté par" in tab_texte[i]:
            j=i
            while j<len(tab_texte)-1:
                if "----------" in tab_texte[j]:
                    redacteurs=tab_texte[i+1:j]
                    break
                else:
                    j+=1
            break
        else:
            i+=1
    if redacteurs=="":
        qui="Echec"
    else:
        qui=redacteurs
    return qui

def strip_amend(texte):
    tab_texte=texte.partition("\n")
    #print(tab_texte)
    # print("Cela donne ceci:\n {}".format(tab_texte[0]))
    # Dans tous les cas
    page,npage=recupere_page(texte)
    noamendement=recupere_amend(tab_texte[0])
    auteurs=origine(texte)
    if (auteurs=="Echec" and npage==2 and page==2):
        print("Page 2 de l'amendement précédent")
    else: # C'est une première page
        pos=position(texte)
        datedep=tab_texte[2]
        print("Les auteurs: {}".format(auteurs))
    """print("Amendement n°{}, en date du {}, position:{}, lieu dépôt:{}, origine:{},".format(noamendement,date,position,lieu_depot,origine_deposant))"""
    
    




fich="LPM_amendement_RH_seancepublique.pdf"
pdf=PdfReader(fich)
nouveau=PdfMerger()
j=1
for i in pdf.pages:
    strip_amend(i.extract_text())
    j+=1
    if j==10:
        break



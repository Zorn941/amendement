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
        if "Gouvernement" in redacteurs[0]:
            qui="Gouvernement"
        else:
            qui="Parlementaires"
    ou=tab_texte[1]
    return redacteurs,qui, ou

def contenu(texte):
    redaction=""
    expose=""
    i=1
    j=i
    # Cherche les marqueurs de début de REDACTION et de début d'EXPOSE
    trouve_redac=False
    while ("----------" not in texte[i] and i<len(texte)-1):
        i+=1
    if "----------" in texte[i]:
        trouve_redac=True
        j=i
    else:
        j=0
        trouve_redac=False
    trouve_expo=False
    while ("EXPOSÉ SOMMAIRE" not in texte[j] and j<len(texte)-1):
        j+=1
    if "EXPOSÉ SOMMAIRE" in texte[j]:
        trouve_expo=True
    else:
        trouve_expo=False
    # Tire les conséquences en terme de texte des marqueurs trouvés ou non
    if trouve_redac and trouve_expo:
        redaction=texte[i+1:j-1]
        expose=texte[j+1:len(texte)]
        print("Rédaction complète")
    elif (not trouve_expo and not trouve_redac):
        print("Aucun marqueur")
        expose=texte[1:len(texte)]
        redaction=""
    elif (trouve_expo and not trouve_redac):
        print("Cas expo vrai et redac faux")
        if j!=1:
            redaction=texte[1:j-1]
        else:
            redaction=""
        expose=texte[j+1:len(texte)]
    elif (not trouve_expo and trouve_redac):
        redaction=texte[i:len(texte)]
        expose=""
    return redaction, expose

def dossier(texte):
    dos=""
    i=3
    while "Commission" not in texte[i] and i<5: # Les noms de loi ne font pas plus de 3 lignes
        i+=1
    for j in texte[3:i]:
        dos=dos+" "+j
    return dos

def strip_amend(texte):
    tab_texte=texte.split("\n")
    print(tab_texte)
    # print("Cela donne ceci:\n {}".format(tab_texte[0]))
    # Dans tous les cas
    page,npage=recupere_page(texte)
    noamendement=recupere_amend(tab_texte[0])
    redac,exp=contenu(tab_texte)
    print(redac)
    print(exp)
    if (npage==2 and page==2):
        print("Page 2 de l'amendement précédent")
        datedep=""
        pos=""
        auteurs=""
        entite=""
        lieu_depot=""
        loi=""
    else: # C'est une première page
        print("Page 1")
        auteurs, entite, lieu_depot=origine(texte)
        pos=position(texte)
        datedep=tab_texte[2]
        loi=dossier(tab_texte)
    return noamendement,page,npage,lieu_depot,entite,auteurs, datedep, pos,loi ,redac,exp
    
fich="LPM_amendement_RH_seancepublique.pdf"
pdf=PdfReader(fich)
npages=len(pdf.pages)
print(npages)
j=0
for i in pdf.pages:
    k=strip_amend(i.extract_text())
    j+=1
    if j==208:
        print(k)
        for r in k:
            print(r)

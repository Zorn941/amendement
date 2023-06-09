from PyPDF2 import PdfReader
import os,sys

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
    if trouve_redac and trouve_expo: # Deux marqueurs sur la même page
        redaction=texte[i+1:j-1]
        expose=texte[j+1:len(texte)]
    elif (not trouve_expo and not trouve_redac): # Aucun marqueur trouvé
        expose=texte[1:len(texte)]
        redaction="" 
    elif (trouve_expo and not trouve_redac): # Marque de l'exposé sommaire trouvé mais pas celle de la rédaction
        if j!=1:
            redaction=texte[1:j-1]
        else:
            redaction=""
        expose=texte[j+1:len(texte)]
    elif (not trouve_expo and trouve_redac): # Marque de l'exposé non trouvée mais celle de la rédaciton oui
        redaction=texte[i:len(texte)]
        expose=""
    redaction=t_convert(redaction)
    # Il faut retirer la mention de la page si elle apparait pour redaction et exposé sommaire
    expose=t_convert(expose)
    if "2/2" in redaction:
        redaction=redaction.replace("2/2","")
    if "----------" in redaction:
        redaction=redaction[0:10].replace("-","")+redaction[11:]
    if "2/2" in expose:
        expose=expose.replace("2/2","")
    return redaction, expose

def dossier(ttexte): # Version avec Sénat en paramètre à faire
    dos=""
    i=0
    trouve=False
    while ("ASSEMBLÉE NATIONALE" not in ttexte[i] and i<len(ttexte)-1):
        i+=1
    if i==len(ttexte):
        dos=""
    else:
        j=i
        while ("Commission" not in ttexte[j] and j<len(ttexte)-1):
            j+=1
        if j==len(ttexte):
            dos=""
        else:
            if i<j:
                dos=ttexte[i+1:j]
                if ("2023" in dos[0]): # Peu élégant à corriger
                    dos.pop(0)
                    dos=t_convert(dos)
                else:
                    dos=t_convert(dos)
            else:
                dos=""
    return dos

def depose_le(ttexte):
    # Recherche une ligne contenant un mois puis isole le jour et l'année
    mois={"janvier","février","mars","avril","mai","juin","juillet","août","septembre","octobre","novembre","décembre"}
    date_depot=""
    trouve=False
    for i in ttexte:
        l=i.split(" ")
        for j in l:
            if j in mois:
                date_depot=l[l.index(j)-1]+" "+j+" "+l[l.index(j)+1]
                trouve=True
        if trouve:
            break
    print(date_depot)
    return date_depot

def strip_amend(texte):
    tab_texte=texte.split("\n")
    # Dans tous les cas
    page,npage=recupere_page(texte)
    noamendement=recupere_amend(tab_texte[0])
    redac,exp=contenu(tab_texte)
    if (npage==2 and page==2): # C'est une page 2
        datedep=""
        pos=""
        auteurs=""
        entite=""
        lieu_depot=""
        loi=""
    else: # C'est une première page
        auteurs, entite, lieu_depot=origine(texte)
        pos=position(texte)
        datedep=depose_le(tab_texte)
        loi=dossier(tab_texte)
    return noamendement,page,npage,lieu_depot,entite,auteurs, datedep, pos,loi ,redac,exp

def t_convert(stripped):
    conv=""
    for i in stripped:
        conv=conv+i+" "
    conv=conv[:-1]
    return conv
    

def conversion(stripped):
    conv=""
    for i in stripped:
        conv=conv+str(i)+";"
    conv=conv[:-1]
    return conv

f=open("digest_"+sys.argv[1][:-4]+".csv","w")
fich=sys.argv[1]
pdf=PdfReader(fich)
npages=len(pdf.pages)
las_red=""
las_exp=""
last=[]
for i in pdf.pages:
    k=list(strip_amend(i.extract_text()))
    if k[0]=="209":
        print(i.extract_text())
        print(k)
    if last==[]:
        last=k
        las_red=t_convert(k[9])
        las_exp=t_convert(k[10])
    elif last[0]==k[0]:
        las_red=las_red+t_convert(k[9])
        las_exp=las_exp+t_convert(k[10])
        last[9]=las_red
        last[10]=las_exp
        f.write(conversion(last)+"\n")
    else:
        if k[1]!=2:
            f.write(conversion(k)+"\n")
            last=k

f.close()
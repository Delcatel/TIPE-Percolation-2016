from tkinter import *
from math import hypot, pi
#from PIL import Image, ImageTk
import random as r
from copy import deepcopy
import matplotlib    #sinon interfère avec tkinter
matplotlib.use('TkAgg')

from numpy import arange, sin, pi, zeros, linspace, arcsin, array
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
# implement the default mpl key bindings
from matplotlib.backend_bases import key_press_handler
from pylab import setp
from matplotlib.figure import Figure

def genere(p):      #probabilité de chaque site d'être occupé
    a = r.random()
    if a<p:
        return 1
    else:
        return 0
        
def lattice (n,p):   #matrice
    A=zeros((n,n), dtype=int)
    for i in range (n):
        for j in range (n):
            A[i,j]= genere(p)
    return A
    
def estdanslamatrice(site,n):       #test
    return 0<=site[0]<n and 0<=site[1]<n

def avancee (site,n,lattice, struct):          #renvoie les nouveaux sites qu'on peut atteindre
    (i,j)=(site[0],site[1])
    avance=[]
    if struct == "triangulaire":
        if i%2:
            propagation = [(i-1,j),(i+1,j), (i,j-1),(i,j+1),(i-1,j-1),(i+1,j-1)]
        else:
            propagation = [(i-1,j),(i+1,j), (i,j-1),(i,j+1),(i-1,j+1),(i+1,j+1)]
    elif struct == "carré":
        propagation=[(i-1,j),(i+1,j), (i,j-1),(i,j+1)]
    for k in propagation :
        if estdanslamatrice(k,n) and lattice[k]==1:
            avance.append(k)
    return avance

    
def incendie (lattice,n, struct):         #teste si le graphe est connexe
    if depart.get() == "Ligne supérieure":
        positions = [(0,k) for k in range (n)]
    elif depart.get() == "Site centrale":
        positions = [(n//2, n//2)]
    elif depart.get() == "Disque centrale":
        positions = []
        for i in range(-n//50, n//50+1):
            for j in range(-n//50, n//50+1):
                if hypot(i, j) <= n//50:
                    positions.append((i+n//2, j+n//2))
    
    for site in positions:
        lattice[site]=-2
    while positions!=[]:
        suivants=[]
        for site in positions:
            suivant=avancee(site, n, lattice, struct)
            for sitesuivant in suivant:           #reduire taille de suivants
                lattice[sitesuivant]=-2
            suivants+=suivant
        positions=suivants


def burnt(lattice,n):
    nb_en_feu = 0
    nb_survivants = 0
    for i in range (n):
        for j in range (n):
            if lattice[(i,j)]==-2:
                nb_en_feu+=1
            elif lattice[(i,j)]==1:
                lattice[(i,j)]=0
                nb_survivants+=1
    return nb_en_feu, nb_survivants
    
#feu: -2
#sans: 0

def voisins(M, n, current):
    voisins = []
    for site in current:
        (i,j) = (site[0],site[1])
        if i%2:
            propagation = [(i-1,j),(i+1,j), (i,j-1),(i,j+1),(i-1,j-1),(i+1,j-1)]
        else:
            propagation = [(i-1,j),(i+1,j), (i,j-1),(i,j+1),(i-1,j+1),(i+1,j+1)]
        for site in propagation:
            if estdanslamatrice(site,n) and M[site] == 0 and site not in voisins:
                voisins.append(site)
    return voisins

def marquage(M, n, current, marque):    # dans la matrice M, on marque les composantes connexes des éléments de la liste position par des i
    nb_marques = 0
    while current != []:
        for site in current:
            M[site] = marque
            nb_marques += 1
        current = voisins(M, n, current)

    return nb_marques
            
def correlation(M, n):
    border = []
    nb_dans_amas = 0
    marque = 0 #sites dans des amas centrales marqués à partir de 1
    chemin_inf = 0
    taille_amas = [0]


    for k in range(n):
        if M[n-1, k] == -2:
            chemin_inf = 1
            break;

    for k in range(n-1):
        ajout = [(k+1, 0), (k, n-1), (n-1, k+1)]
        for element in ajout:
            if M[element] == 0:
                marquage(M, n, [element], -1)   #sites dans amas qui touchent un bord marqués -1
                #méthode plus sur d'énormes graphes car tableau trop longs à parcourir:
                #border.append(element)
    #marquage(M, n, border, -2)

    for L in range(1, n-1):  #parcourt M[1:-1,1:-1]: M privé de ses 4 bords
        for C in range(1, n-1):
            if M[L, C] == 0:
                marque += 1
                taille = marquage(M, n, [(L, C)], marque) #taille de l'amas
                nb_dans_amas += taille
                taille_amas.append(taille) #taille_amas[k] = taille du k-iemes amas
    taille_amas[0] = marque # marque est le nb d'amas ie len(taille_amas)+1
    
    return (taille_amas, nb_dans_amas, chemin_inf)
    
#feu -2 , libre -1, encerclé: >0

def image_thermique(taille_amas, M, n, p):
    if taille_amas[1:]:
        max_amas = max(taille_amas[1:])
    else:
            max_amas = 1
    for ligne in range(n):
        for col in range(n):
            valeur = M[ligne, col]
            if valeur >= 0:
                M[ligne, col] = max_amas*4/3-taille_amas[valeur]
            elif valeur == -2:
                M[ligne, col] = max_amas*4/3
            elif valeur ==-1:
                M[ligne, col] = 0
    #ax = fig.add_axes([0.15, 0.05, 0.7, 0.7])
    if foret_brule.get():
        ax_thermique = fig.add_subplot(122)
    else:
        ax_thermique = fig.add_subplot(111)
    #ax.set_title('Feu de forêt de structure triangulaire %iX%i à p = %.2f' % (n, n, p)) #afficher avec 2 décimales
    ax_thermique.matshow(M)
    canvas.show()   #affiche les modifications
    #fig.savefig('Test')

def image_foret_brule(M, n, p):
    C = []
    if depart.get() == "Ligne supérieure":
        condition = lambda i, j: 1
    else:
        condition = lambda i, j: hypot(i-n//2, j-n//2) <= n//2   # bordure circulaire de la forêt
    for i in range(n):
        C.append([])
        for j in range(n):
            if M[i, j] == 1 and condition(i, j):
                C[-1].append((0, 50, 0))
            elif M[i, j] == -2 and condition(i, j):
                C[-1].append((50, 0, 0))
            else:
                C[-1].append((1, 1, 1))
    
    if foret_thermique.get():
        ax_brule = fig.add_subplot(121)
    else:
        ax_brule = fig.add_subplot(111)
        
    ax_brule.imshow(C)
    canvas.show()

def f(n, p, struct):
    M = lattice(n,p)
    incendie(M, n, struct)
    fig.clf()
    if foret_brule.get():
        image_foret_brule(M, n, p)
    
    nb_en_feu, nb_survivants = burnt(M, n)  #prop d'arbres en feu
    tableau_amas, nb_encercle, chemin_inf = correlation(M, n)
    if foret_thermique.get():
        image_thermique(tableau_amas, M, n, p)
    prop_encercle = nb_encercle/(n**2)    #proba d'être encerclé
    prop_libre = 1-(nb_encercle+nb_en_feu)/(n**2)     #proba d'être libre
    
    global resultats, li_resultats
    resultats.pack_forget()
    resultats = LabelFrame(fr_param, text="Résultats", padx=5, pady=5)
    resultats.pack(padx=10, pady=30)
    
    li_resultats = [nb_en_feu+nb_survivants, nb_en_feu, nb_survivants, nb_en_feu/(nb_en_feu+nb_survivants), prop_encercle, prop_libre, chemin_inf]
    if not mode_graphique:
        for indice, res in enumerate(li_resultats[:-1]):
            if type(res) == int:
                label = Label(resultats, text=li_parametres[indice]+': '+str(li_resultats[indice]))
            else:
                label = Label(resultats, text=li_parametres[indice]+': %.3f' % li_resultats[indice])
            label.pack()
        if chemin_inf:
            chemin = "Oui"
        else:
            chemin = "Non"
        label_chemin = Label(resultats, text="Percolation de l'incendie: %s" % chemin)
        label_chemin.pack()

#image = Image.open("/home/delcatel/Documents/Programming/TIPE/MP/Images/foret_en_feu_100_050.xbm")
#photo = ImageTk.PhotoImage(image)

#photo = PhotoImage(file="/home/delcatel/Documents/Programming/TIPE/MP/Images/foret_en_feu_100_050.gif")

#w.photo = photo #keep reference of the image so that Python doesn't clear its variable space

mode_graphique = 0  # n'affiche pas les résultats de chaque simulation
li_resultats = []
li_parametres = ["Nombres d'arbres", "Nombres d'arbres incendiés", "Nombres d'arbres survivants", "Proportion d'arbres incendiés", "Superficie relative encerclée", "Superficie relative non-encerclée", "Percolation de l'incendie"]
courbes_activees = [0 for k in range(len(li_parametres))]
lines = []  # contient la liste des courbes du graphes (vsibles ou non)

def hello():
    print("Désolé, cette commande est en chantier.")

def save():
    #fig.savefig("triangulaire_%i_%.2f.png" % (int(taille.get()), float(prop.get())))
    file = open('resultats_%s_%s' % (taille.get(), prop.get()), 'a')   # for appending
    for line in li_resultats:
        file.write(line+'\n')
    file.write('\n')
    file.close()

def simulation():
    print("Simulation en cours:", "n =",taille.get(), "; p =", prop.get(), "; forêt:", struct.get())
    f(int(taille.get()), float(prop.get()), struct.get())
    for indice, res in enumerate(li_resultats):
        if type(res) == int:
            print(li_parametres[indice]+': '+str(res))
        else:
            print(li_parametres[indice]+': %.3f' % res)
    print('\n')

root = Tk()

### Frame de gauche

frame = Frame(root)
frame.pack(side=LEFT)
resultats = LabelFrame(frame)
fr_param = Frame(frame)
fr_progression = LabelFrame(fr_param)

def actualiser_graphe():
    global lines
    if mode_graphique and lines:   # si mode_graphique == 1 mais lines = [] alors le tracer du premier graphe est en cours
        for indice, activee in enumerate(courbes_activees):
            setp(lines[indice], visible = bool(activee.get()))
        canvas.show()
                

def tracer():
    global fr_param, abs, min_abs, max_abs, nb_simul, fonction, struct, param_cst, courbes_activees, fr_progression, foret_brule, foret_thermique
    global taille, prop, mode_graphique, lines
    mode_graphique = 1  #   ne pas afficher les réultats des chaque simulation dans la console et la GUI et actualise les courbes visibles quand on coche
    nb_sim = int(nb_simul.get())
    if abs.get() == "Proportion":
        m = float(min_abs.get())
        M = float(max_abs.get())
        taille = param_cst
    elif abs.get() == "Taille":
        m = int(min_abs.get())
        M = int(max_abs.get())
        prop = param_cst
    
    if fonction.get() == "Linéaire":    # liste centrée en 0 de longueur 1 (entre -0.5 et 0.5)
        X = linspace(-0.5, 0.5, int(nb_sim))
    elif fonction.get() == "Arcsin":
        X = arcsin(linspace(-1, 1, int(nb_sim)))/pi
    elif fonction.get() == "Cubique":
        X = [((2*k/(float(nb_sim)-1)-1)**3)/2 for k in range(nb_sim)]
    elif fonction.get() == "Quintique":
        X = [((2*k/(float(nb_sim)-1)-1)**5)/2 for k in range(nb_sim)]
    elif fonction.get() == "Septique":
        X = [((2*k/(float(nb_sim)-1)-1)**7)/2 for k in range(nb_sim)]
    X = array(X)*(M-m) + (m+M)/2
    if abs.get() == "Taille":
        X = list(X)
        X[-1] = int(X[-1])
        long_X = len(X)
        for indice in range(1, len(X)):
            X[long_X-indice-1] = int(X[long_X-indice-1])
            if X[long_X-indice-1] == X[long_X-indice]:
                X.pop(long_X-indice)
    
    Y = [[] for indice in range(len(li_parametres))]
    
    fr_progression.destroy()
    fr_progression = LabelFrame(fr_param, text="  Progression:  ", padx=5, pady=5)
    fr_progression.pack(padx=10, pady=10)
    lab_progression = Label(fr_progression, text="   0 %   ")
    lab_progression.pack()
    lab_prog_nb = Label(fr_progression, text="  (sur %i simulations) " % nb_sim)
    lab_prog_nb.pack()
    fr_progression.update()
    
    long_X = len(X)
    avancement = 0  # en dizaines de pourcents
    val_foret_brule = foret_brule.get()
    val_foret_thermique = foret_thermique.get()
    foret_brule.set(0)
    foret_thermique.set(0)
    
    for indice_x, x in enumerate(X):
        test = int((indice_x+1)*10/long_X)-avancement # condition d'affichage tous les 10 %
        if test:
            avancement += 1
            lab_progression.config(text="   {}0 %   ".format(avancement))
            fr_progression.update()
            foret_brule.set(val_foret_brule)
            foret_thermique.set(val_foret_thermique)

        if abs.get() == "Proportion":
            f(int(taille.get()), x, struct.get())
        elif abs.get() == "Taille":
            f(x, float(prop.get()), struct.get())
        for indice_res, res in enumerate(li_resultats):  #   une ligne par paramètre
            Y[indice_res].append(res)
        
        if test:
            foret_brule.set(0)
            foret_thermique.set(0)
            if graphe_partiel.get() == 1:   # affichage des graphes partiels
                fig.clf()
                ax_nb = fig.add_subplot(111)
                ax_prop = ax_nb.twinx()
                ax_nb.set_xlim(m, x)
                ax_prop.set_xlim(m, x)
                lines = []  # contient la liste des courbes du graphes (vsibles ou non), réinitialise la liste en global
                for indice_par, param in enumerate(li_parametres):
                    if indice_par < 3:
                        lines.append(ax_nb.plot(X[:indice_x+1], Y[indice_par], visible=bool(courbes_activees[indice_par].get())))
                    else:
                        lines.append(ax_prop.plot(X[:indice_x+1], Y[indice_par], ls='-.', visible=bool(courbes_activees[indice_par].get())))
                canvas.show()
            
    
    fig.clf()
    ax_nb = fig.add_subplot(111)
    ax_prop = ax_nb.twinx()
    ax_nb.set_xlim(m, M)
    ax_prop.set_xlim(m, M)
    lines = []  # contient la liste des courbes du graphes (vsibles ou non), réinitialise la liste en global
    for indice, param in enumerate(li_parametres):
        if indice < 3:
            lines.append(ax_nb.plot(X, Y[indice], visible=bool(courbes_activees[indice].get())))
        else:
            lines.append(ax_prop.plot(X, Y[indice], ls='-.', visible=bool(courbes_activees[indice].get())))
    canvas.show()
    
        

def graphique():
    global fr_param, abs, min_abs, max_abs, nb_simul, fonction, ord, struct, param_cst, depart, foret_brule, foret_thermique, graphe_partiel
    global courbes_activees
    
    fr_param.destroy()
    fr_param = Frame(frame)
    fr_param.pack(side=TOP)  
    
    frame_struct = LabelFrame(fr_param, text="Structure de la forêt", padx=5, pady=5)
    frame_struct.pack(padx=10, pady=10)
    struct = StringVar()
    struct.set("triangulaire") # initialize
    Radiobutton(frame_struct, text=" triangulaire", variable=struct, value="triangulaire").pack(anchor=W)
    Radiobutton(frame_struct, text=" carré", variable=struct, value="carré").pack(anchor=W)
    
    lab_depart = Label(fr_param, text="  Départ de feu:  ")
    lab_depart.pack()
    depart = StringVar()
    depart.set("Ligne supérieure") # default value
    Op_depart = OptionMenu(fr_param, depart, "Ligne supérieure", "Site centrale", "Disque centrale")
    Op_depart.pack()
    
    lab_abs = LabelFrame(fr_param, text="En abscisse", padx=5, pady=5)
    lab_abs.pack(padx=10, pady=10)
    lab_param_abs = Label(lab_abs, text="   Paramètre:   ")
    lab_param_abs.pack()
    abs = StringVar()
    abs.set("Proportion") # default value
    Op_abs = OptionMenu(lab_abs, abs, "Proportion", "Taille")
    Op_abs.pack()
    lab_min = Label(lab_abs, text="   Min:   ")
    lab_min.pack()
    min_abs = Entry(lab_abs)
    min_abs.pack()
    lab_max = Label(lab_abs, text="   Max:   ")
    lab_max.pack()
    max_abs = Entry(lab_abs)
    max_abs.pack()
    lab_nb_simul = Label(lab_abs, text="   Nombre de simulations:   ")
    lab_nb_simul.pack()
    nb_simul = Entry(lab_abs)
    nb_simul.pack()
    lab_fonction = Label(lab_abs, text="   Fonction:   ")
    lab_fonction.pack()
    fonction = StringVar()
    fonction.set("Linéaire") # default value
    Op_fonction = OptionMenu(lab_abs, fonction, "Linéaire", "Arcsin", "Cubique", "Quintique", "Septique")
    Op_fonction.pack()
    lab_param_cst = Label(lab_abs, text="   Valeur du paramètre constant:   ")
    lab_param_cst.pack()
    param_cst = Entry(lab_abs)
    param_cst.pack()
    
    foret_brule = IntVar()
    cb_foret_brule = Checkbutton(fr_param, text="  Forêt incendiée", variable=foret_brule) #1 si activé, 0 sinon
    cb_foret_brule.pack()
    foret_thermique = IntVar()
    cb_foret_thermique = Checkbutton(fr_param, text=" Vision thermique", variable=foret_thermique) #1 si activé, 0 sinon
    cb_foret_thermique.pack()
    graphe_partiel = IntVar()
    cb_graphe_partiel = Checkbutton(fr_param, text="   Graphe partiel", variable=graphe_partiel) #1 si activé, 0 sinon
    cb_graphe_partiel.pack()
    
    bu_tracer = Button(fr_param, text='Tracer', command=tracer, fg="red")
    bu_tracer.pack()
    
    lab_ord = LabelFrame(fr_param, text="En Ordonnée", padx=5, pady=5)
    lab_ord.pack(padx=10, pady=10)
    lab_param_ord = Label(lab_ord, text="   Paramètres:   ")
    lab_param_ord.pack()
    #ord = StringVar()
    #ord.set("Superficie relative encerclée") # default value
    #Op_ord = OptionMenu(lab_ord, ord, "Nombres d'arbres", "Nombres d'arbres incendiés", "Nombres d'arbres survivants", "Proportion d'arbres incendiés", "Superficie relative encerclée", "Superficie relative non-encerclée", "Percolation de l'incendie")
    #Op_ord.pack()
    
    for indice in range(len(courbes_activees)):
        courbes_activees[indice] = IntVar()
        courbes_activees[indice].set(0)

    ch_bu = []
    for indice, param in enumerate(li_parametres):
        ch_bu.append(Checkbutton(lab_ord, text=' '+param, variable=courbes_activees[indice], command=actualiser_graphe))
        ch_bu[-1].pack(anchor=W)    # anchor=W: aligne à gauche les cases à cochées

def parametre_unique():
    global fr_param, taille, prop, struct, depart, foret_brule, foret_thermique, mode_graphique # nécessaire pour modifier la variable locale et non la copie locale
    mode_graphique = 0
    
    fr_param.destroy()
    fr_param = Frame(frame)
    fr_param.pack(side=TOP)
    titre = Label(fr_param, text="  Paramètres de la simulation:  ")
    titre.pack()
    frame_struct = LabelFrame(fr_param, text="Structure de la forêt", padx=5, pady=5)
    frame_struct.pack(padx=10, pady=10)
    struct = StringVar()
    struct.set("triangulaire") # initialize
    Radiobutton(frame_struct, text="triangulaire", variable=struct, value="triangulaire").pack(anchor=W)
    Radiobutton(frame_struct, text="carré", variable=struct, value="carré").pack(anchor=W)
    
    frame_taille = LabelFrame(fr_param, text="Taille du graphe", padx=5, pady=5)
    frame_taille.pack(padx=10, pady=10)
    taille = Entry(frame_taille)
    taille.pack()
    
    proportion = Label(fr_param, text="  Proportion d'arbres:  ")
    proportion.pack()
    prop = Scale(fr_param, from_=0, to=1, orient=HORIZONTAL, resolution=-1)    #p.get() pour obtenir la valeur
    prop.pack()
    
    lab_depart = Label(fr_param, text="  Départ de feu:  ")
    lab_depart.pack()
    depart = StringVar()
    depart.set("Ligne supérieure") # default value
    Op_depart = OptionMenu(fr_param, depart, "Ligne supérieure", "Site centrale", "Disque centrale")
    Op_depart.pack()
    
    foret_brule = IntVar()
    cb_foret_brule = Checkbutton(fr_param, text="  Forêt incendiée", variable=foret_brule) #1 si activé, 0 sinon
    cb_foret_brule.pack()
    foret_thermique = IntVar()
    cb_foret_thermique = Checkbutton(fr_param, text=" Vision thermique", variable=foret_thermique) #1 si activé, 0 sinon
    cb_foret_thermique.pack()
    #disposition = IntVar()
    #cb_disp = Checkbutton(frame, text=" Haute définition", variable=disposition) #1 si activé, 0 sinon
    #cb_disp.pack()
    
    bu_lancer = Button(fr_param, text='lancer', command=simulation, fg="red")
    bu_lancer.pack()

menubar = Menu(frame)

# create a pulldown menu, and add it to the menu bar
filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="Open", command=hello)
filemenu.add_command(label="Save", command=save)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=root.quit)
menubar.add_cascade(label="Fichier", menu=filemenu)

# create more pulldown menus
editmenu = Menu(menubar, tearoff=0)
#editmenu.add_command(label="relancer", command=hello)
editmenu.add_command(label="Graphique", command=graphique)
editmenu.add_command(label="Simulatoire", command=parametre_unique)
menubar.add_cascade(label="Mode", menu=editmenu)

helpmenu = Menu(menubar, tearoff=0)
helpmenu.add_command(label="A propos", command=hello)
menubar.add_cascade(label="Aide", menu=helpmenu)

# display the menu
root.config(menu=menubar)

parametre_unique()

#forme = IntVar()
#c = Checkbutton(frame, text="arbres arrondis", variable=forme) #1 si activé, 0 sinon
#c.pack()

#bu_foret_init = Button(frame, text='Forêt initiale', command=actualiser_init)
#bu_foret_init.pack()
#bu_foret_brule = Button(frame, text='Forêt brûlée', command=actualiser_brule)
#bu_foret_brule.pack()
#bu_foret_thermique = Button(frame, text='Vision thermique', command=actualiser_thermique)
#bu_foret_thermique.pack()

### Frame de droite

frameright = Frame(root)
frameright.pack(side=RIGHT)

root.wm_title("TIPE de Vincent et Philippe: Percolation des feux de forêts")
fig = Figure(figsize=(8, 4.5), dpi=150)

# a tk.DrawingArea
canvas = FigureCanvasTkAgg(fig, master=frameright)
canvas.show()
canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)

toolbar = NavigationToolbar2TkAgg(canvas, frameright)
toolbar.update()
canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)

def on_key_event(event):
    print('you pressed %s'%event.key)
    key_press_handler(event, canvas, toolbar)

canvas.mpl_connect('key_press_event', on_key_event)

root.mainloop()
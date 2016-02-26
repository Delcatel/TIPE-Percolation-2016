from tkinter import *
#from PIL import Image, ImageTk
import pylab as plt #sinon interfère avec tkinter
import random as r
import matplotlib
matplotlib.use('TkAgg')

from numpy import arange, sin, pi
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
# implement the default mpl key bindings
from matplotlib.backend_bases import key_press_handler


from matplotlib.figure import Figure

def genere(p):      #probabilité de chaque site d'être occupé
    a = r.random()
    if a<p:
        return 1
    else:
        return 0
        
def lattice (n,p):   #matrice
    A=plt.zeros((n,n), dtype=int)
    for i in range (n):
        for j in range (n):
            A[i,j]= genere(p)
    return A
    
def estdanslamatrice(site,n):       #test
    return 0<=site[0]<n and 0<=site[1]<n

def avancee (site,n,lattice):          #renvoie les nouveaux sites qu'on peut atteindre
    (i,j)=(site[0],site[1])
    avance=[]
    if i%2:
        propagation = [(i-1,j),(i+1,j), (i,j-1),(i,j+1),(i-1,j-1),(i+1,j-1)]
    else:
        propagation = [(i-1,j),(i+1,j), (i,j-1),(i,j+1),(i-1,j+1),(i+1,j+1)]
    for k in propagation :
        if estdanslamatrice(k,n) and lattice[k]==1:
            avance.append(k)
    return avance

    
def incendie (lattice,n):         #teste si le graphe est connexe
    positions=[(0,k) for k in range (n)]
    for site in positions:
        lattice[site]=-2
    while positions!=[]:
        suivants=[]
        for site in positions:
            suivant=avancee(site,n,lattice)
            for sitesuivant in suivant:           #reduire taille de suivants
                lattice[sitesuivant]=-2
            suivants+=suivant
        positions=suivants


def burnt(lattice,n):
    arbresenfeu=0
    for i in range (n):
        for j in range (n):
            if lattice[(i,j)]==-2:
                arbresenfeu+=1
            elif lattice[(i,j)]==1:
                lattice[(i,j)]=0
    return arbresenfeu/(n**2)
    
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

def image(taille_amas, M, n, p):
    max_amas = max(taille_amas[1:])
    for ligne in range(n):
        for col in range(n):
            valeur = M[ligne, col]
            if valeur >= 0:
                M[ligne, col] = max_amas*4/3-taille_amas[valeur]
            elif valeur == -2:
                M[ligne, col] = max_amas*4/3
            elif valeur ==-1:
                M[ligne, col] = 0
    fig = plt.figure()
    #ax = fig.add_axes([0.15, 0.05, 0.7, 0.7])
    ax = fig.add_subplot(111)
    ax.set_title('Feu de forêt de structure triangulaire %iX%i à p = %.2f' % (n, n, p)) #afficher avec 2 décimales
    ax.matshow(M)
    #fig.savefig('Test')

def fonction(n, p):
    M = lattice(n,p)
    incendie(M, n)
    propfeu=burnt(M, n)  #prop d'arbres en feu
    (a, b, traverse) = correlation(M, n)
    image(a, M, n, p)
    encercle=b/(n**2)    #prop d'être encerclé
    libres = 1-encercle-propfeu     #prop d'être libre
    return propfeu, encercle, libres, traverse

root = Tk()

#image = Image.open("/home/delcatel/Documents/Programming/TIPE/MP/Images/foret_en_feu_100_050.xbm")
#photo = ImageTk.PhotoImage(image)

#photo = PhotoImage(file="/home/delcatel/Documents/Programming/TIPE/MP/Images/foret_en_feu_100_050.gif")

frame = Frame(root)
frame.pack()

label = Label(root, text="  Percolation des feux de forêts  ")
#w.photo = photo #keep reference of the image so that Python doesn't clear its variable space
label.pack()

def hello():
    print("hello!")

def simulation():
    fonction(int(n.get()), float(p.get()))

menubar = Menu(root)

# create a pulldown menu, and add it to the menu bar
filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="Open", command=hello)
filemenu.add_command(label="Save", command=hello)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=root.quit)
menubar.add_cascade(label="File", menu=filemenu)

# create more pulldown menus
editmenu = Menu(menubar, tearoff=0)
editmenu.add_command(label="relancer", command=hello)
editmenu.add_command(label="interrompre", command=hello)
editmenu.add_command(label="Pause", command=hello)
menubar.add_cascade(label="Exécuter", menu=editmenu)

helpmenu = Menu(menubar, tearoff=0)
helpmenu.add_command(label="About", command=hello)
menubar.add_cascade(label="Help", menu=helpmenu)

# display the menu
root.config(menu=menubar)

taille = LabelFrame(root, text="Taille du graphe", padx=5, pady=5)
taille.pack(padx=10, pady=10)
n = Entry(taille)
n.pack()

p = Scale(root, from_=0, to=1, orient=HORIZONTAL, resolution=-1)    #p.get() pour obtenir la valeur
p.pack()

button = Button(root, text='lancer', command=simulation)
button.pack()

root.wm_title("Embedding in TK")


f = Figure(figsize=(5,4), dpi=100)
a = f.add_subplot(111)
t = arange(0.0,3.0,0.01)
s = sin(2*pi*t)

a.plot(t,s)


# a tk.DrawingArea
canvas = FigureCanvasTkAgg(f, master=root)
canvas.show()
canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)

toolbar = NavigationToolbar2TkAgg( canvas, root )
toolbar.update()
canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)

def on_key_event(event):
    print('you pressed %s'%event.key)
    key_press_handler(event, canvas, toolbar)

canvas.mpl_connect('key_press_event', on_key_event)


root.mainloop()
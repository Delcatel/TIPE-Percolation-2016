from pylab import *
import random as r


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
    fig = figure()
    #ax = fig.add_axes([0.15, 0.05, 0.7, 0.7])
    ax = fig.add_subplot(111)
    ax.set_title('Feu de forêt de structure triangulaire %iX%i à p = %.2f' % (n, n, p)) #afficher avec 2 décimales
    ax.matshow(M)
    #fig.savefig('Test')

def f(n, p):
    M = lattice(n,p)
    incendie(M, n)
    propfeu=burnt(M, n)  #prop d'arbres en feu
    (a, b, traverse) = correlation(M, n)
    image(a, M, n, p)
    encercle=b/(n**2)    #prop d'être encerclé
    libres = 1-encercle-propfeu     #prop d'être libre
    return propfeu, encercle, libres, traverse

def foret_carre(M, n, p):   #pas plus rapide qu'avec des cercles ou polygones en triangulaire ou non
    fig = figure()
    ax = fig.add_subplot(111)
    ax.set_title('Forêt de structure triangulaire %iX%i à p = %.2f' % (n, n, p)) #afficher avec 2 décimales
    for lin in range(n):
        for col in range(n):
            if M[lin, col] == 1:
                ax.add_patch(Rectangle( (col,lin), width=1, height=1, color='green'))
    ax.autoscale_view()
    ax.figure.canvas.draw()

def foret_triangulaire_cercle(M, n, p):
    fig = figure()
    ax = fig.add_subplot(111)
    ax.set_title('Forêt de structure triangulaire %iX%i à p = %.2f' % (n, n, p)) #afficher avec 2 décimales
    for lin in range(n):
        for col in range(n):
            if M[lin, col] == 1:
                ax.add_patch(Circle((col+(lin%2)/2, lin), radius=0.4, color='green'))
    ax.set_xlim(-0.5, n)
    ax.set_ylim(-0.5, n-0.5)
    ax.figure.canvas.draw()

def foret_brule_cercle(M, n, p):
    fig = figure(facecolor='white')
    ax = fig.add_subplot(111)
    ax.set_title('Forêt de structure triangulaire %iX%i à p = %.2f' % (n, n, p)) #afficher avec 2 décimales
    for lin in range(n):
        for col in range(n):
            if M[lin, col] == 1:
                ax.add_patch(Circle((col+(lin%2)/2, lin), radius=0.4, color='green'))
            if M[lin, col] == -2:
                ax.add_patch(Circle((col+(lin%2)/2, lin), radius=0.4, color=(0.5, 0, 0)))
    ax.set_xlim(-0.5, n)
    ax.set_ylim(-0.5, n-0.5)
    savefig('Test', format='gif', facecolor=fig.get_facecolor(), transparent=True)
    ax.figure.canvas.draw()

def foret_brule_polygone(M, n, p):
    fig = figure(facecolor='white')
    ax = fig.add_subplot(111)
    ax.set_title('Forêt de structure triangulaire %iX%i à p = %.2f' % (n, n, p)) #afficher avec 2 décimales
    for lin in range(n):
        for col in range(n):
            if M[lin, col] == 1:
                ax.add_patch(matplotlib.patches.CirclePolygon((col+(lin%2)/2, lin), radius=0.4, resolution=6, color='green'))
            if M[lin, col] == -2:
                ax.add_patch(matplotlib.patches.CirclePolygon((col+(lin%2)/2, lin), radius=0.4, resolution=6, color=(0.5, 0, 0)))
    ax.set_xlim(-0.5, n)
    ax.set_ylim(-0.5, n-0.5)
    savefig(ax.get_title()+'.png', facecolor=fig.get_facecolor(), transparent=True)
    ax.figure.canvas.draw()

def g(n, p):
    M = lattice(n,p)
    incendie(M, n)
    foret_brule_cercle(M, n, p)

    
#matshow
# Design d'iteration - formulaire de devis guide

## 1. Objet

Cette iteration vise a transformer l'ecran `Nouveau devis` en un vrai formulaire metier exploitable par un utilisateur interne, avec validation stricte, listes guidees, declenchement du calcul, et affichage detaille du resultat.

Elle s'appuie sur le socle deja disponible :

- moteur de calcul ;
- persistance SQLite ;
- historique des devis ;
- administration des regles ;
- interface desktop a onglets.

## 2. But fonctionnel

Permettre a un utilisateur de produire un devis approximatif complet directement depuis l'interface, sans manipulation technique ni saisie libre excessive.

## 3. Perimetre de l'iteration

### Inclus

- enrichissement du formulaire `Nouveau devis` ;
- ajout de listes deroulantes guidees ;
- validation stricte des champs avant calcul ;
- chargement des valeurs de reference depuis la base avec repli sur des valeurs par defaut ;
- execution du calcul depuis l'interface ;
- enregistrement automatique du devis apres calcul ;
- affichage du resultat detaille dans l'onglet `Resultat`.

### Exclu

- export PDF ;
- impression ;
- assistant multi-etapes ;
- edition avancee d'un devis deja calcule ;
- synchronisation temps reel entre administration et formulaire ;
- personnalisation graphique poussee.

## 4. Experience utilisateur cible

L'utilisateur ouvre l'application, reste dans l'onglet `Nouveau devis`, renseigne les informations du client et du projet, clique sur `Calculer le devis`, puis consulte immediatement le resultat detaille dans l'onglet `Resultat`.

L'interface doit etre guidee, rapide a comprendre, et bloquer les erreurs les plus importantes avant calcul.

## 5. Design du formulaire

## 5.1 Structure des sections

Le formulaire sera compose des groupes suivants :

### Client

- nom du client ;
- contact du client.

### Projet

- type de batiment ;
- localisation ;
- surface ;
- nombre d'etages ;
- nombre de pieces.

### Technique

- type de structure ;
- type de toiture ;
- niveau de finition ;
- niveau de complexite.

### Notes

- zone de texte libre pour remarques additionnelles.

### Action

- bouton `Calculer le devis`.

## 5.2 Type de champs

- `QLineEdit` pour le nom, le contact et certaines valeurs simples ;
- `QComboBox` pour les listes guidees ;
- `QSpinBox` ou equivalent pour les entiers ;
- `QDoubleSpinBox` ou equivalent pour la surface ;
- `QTextEdit` pour les notes ;
- `QPushButton` pour le lancement du calcul.

## 5.3 Champs obligatoires

Les champs suivants seront obligatoires :

- nom du client ;
- type de batiment ;
- localisation ;
- surface ;
- nombre d'etages ;
- type de structure ;
- type de toiture ;
- niveau de finition ;
- niveau de complexite.

Le nombre de pieces pourra rester optionnel ou semi-obligatoire selon le type de projet, mais dans cette iteration il sera accepte comme champ renseigne sans logique conditionnelle complexe.

## 6. Validation stricte

## 6.1 Regles de validation

Le calcul sera refuse si l'une des conditions suivantes est rencontree :

- nom client vide ;
- type de batiment non selectionne ;
- localisation non selectionnee ;
- surface inferieure ou egale a zero ;
- nombre d'etages invalide ;
- type de structure non selectionne ;
- type de toiture non selectionne ;
- niveau de finition non selectionne ;
- niveau de complexite non selectionne.

## 6.2 Restitution des erreurs

Les erreurs devront etre exprimees clairement dans l'interface. Le systeme devra expliquer :

- quel champ pose probleme ;
- pourquoi le calcul est refuse ;
- ce que l'utilisateur doit corriger.

L'iteration ne necessite pas encore une gestion avancee des erreurs multi-zones. Un affichage synthétique et lisible suffit, par exemple un message global au-dessus ou au-dessous du formulaire.

## 7. Chargement des listes de reference

## 7.1 Principe

Les listes du formulaire devront fonctionner en mode mixte :

1. charger les valeurs depuis la base si elles existent ;
2. utiliser des valeurs par defaut si la base ne contient pas encore les references necessaires.

## 7.2 Listes concernees

- types de batiments ;
- localisations ;
- types de structure ;
- types de toiture ;
- niveaux de finition ;
- niveaux de complexite.

## 7.3 Valeurs par defaut

Les valeurs de secours devront etre suffisantes pour rendre l'application utilisable immediatement apres installation. Elles devront etre simples, stables et coherentes avec le domaine metier.

Exemples de valeurs par defaut possibles :

- types de batiments : Villa, Immeuble, Local commercial ;
- localisations : Antananarivo, Toamasina, Mahajanga ;
- structures : Beton arme, Maconnerie porteuse ;
- toitures : Tuile, Bac acier, Dalle beton ;
- finitions : Economique, Standard, Haut standing ;
- complexites : Simple, Normal, Complexe.

## 8. Flux fonctionnel du bouton Calculer

Au clic sur `Calculer le devis`, l'application suit la sequence suivante :

1. lire les valeurs du formulaire ;
2. valider les donnees ;
3. construire un `QuoteInput` ;
4. charger les references de calcul ;
5. executer le calcul estimatif ;
6. enregistrer le devis ;
7. mettre a jour l'onglet `Resultat`.

Si une etape echoue, l'utilisateur doit recevoir un message clair et l'application ne doit pas se fermer ni entrer dans un etat incoherent.

## 9. Design de l'onglet Resultat

L'onglet `Resultat` affichera quatre blocs principaux :

### 9.1 Montant total estime

Affichage prominent du montant global du devis, formate de maniere lisible.

### 9.2 Detail par lots

Liste ou tableau des postes :

- fondations ;
- structure ;
- toiture ;
- finitions ;
- divers.

### 9.3 Coefficients appliques

Presentation des multiplicateurs ou ajustements utilises dans le calcul, notamment :

- localisation ;
- structure ;
- toiture ;
- complexite ;
- etages.

### 9.4 Resume du projet

Resume des informations principales :

- client ;
- type de batiment ;
- surface ;
- localisation ;
- finition ;
- structure ;
- toiture.

## 10. Architecture technique de l'iteration

## 10.1 Validation separee du widget

La logique de validation ne devra pas etre dispersee directement dans les widgets. Une couche dediee devra centraliser :

- la lecture des donnees de formulaire ;
- les erreurs de validation ;
- la creation du `QuoteInput`.

## 10.2 Fournisseur de donnees de reference

Un composant dedie chargera les listes depuis la base, avec repli sur des valeurs par defaut. Cela evitera d'entremeler la base de donnees directement dans le code d'affichage des widgets.

## 10.3 Controleur de formulaire

Un service ou controleur de formulaire pilotera :

- la validation ;
- le lancement du workflow de devis ;
- la gestion des erreurs ;
- l'envoi des donnees a la vue resultat.

## 10.4 Affichage du resultat

L'onglet `Resultat` devra pouvoir etre mis a jour dynamiquement apres calcul, sans recreer toute la fenetre principale.

## 11. Cas d'erreur a couvrir

- formulaire incomplet ;
- surface invalide ;
- references de calcul indisponibles ;
- absence de profil de prix pour la combinaison choisie ;
- coefficient manquant pour une valeur selectionnee ;
- echec d'enregistrement du devis.

Dans chacun de ces cas, le message doit rester comprehensible pour un utilisateur metier, pas seulement pour un developpeur.

## 12. Tests attendus

Cette iteration devra ajouter au minimum :

- tests de validation formulaire ;
- tests de chargement des listes avec valeurs par defaut ;
- test du calcul lance depuis l'interface ;
- test de blocage du calcul si formulaire invalide ;
- test de mise a jour de l'onglet `Resultat` ;
- test d'affichage des coefficients et de la ventilation.

## 13. Critères de succes

L'iteration sera consideree comme reussie si :

- l'utilisateur peut saisir un devis complet depuis l'interface ;
- les listes du formulaire sont exploitables meme sans parametrage complet de la base ;
- le calcul est bloque en cas de saisie invalide ;
- un devis valide produit un resultat detaille dans l'onglet `Resultat` ;
- le devis est enregistre dans l'historique.

## 14. Recommandation de mise en oeuvre

Cette iteration doit rester focalisee sur le chemin principal de creation d'un devis. Il ne faut pas chercher a traiter tous les cas particuliers metier des maintenant.

La priorite est :

1. rendre le formulaire reellement utilisable ;
2. connecter l'interface au workflow metier existant ;
3. rendre le resultat lisible et credible.

## 15. Conclusion

Cette iteration constitue la transition entre un socle technique fonctionnel et un veritable outil metier utilisable par les equipes internes. Elle est critique, car elle transforme une architecture correcte mais encore technique en experience de saisie et de calcul directement exploitable.

on # Cahier des charges fonctionnel

## 1. Intitule du projet

Conception et developpement d'un logiciel desktop de devis approximatifs pour projets de construction de batiments.

## 2. Contexte

L'entreprise cliente opere dans le secteur du genie civil et souhaite disposer d'un outil informatique permettant d'etablir rapidement des devis estimatifs pour des prospects ou clients souhaitant construire des batiments, villas, immeubles, locaux commerciaux ou autres ouvrages courants.

Aujourd'hui, l'estimation rapide repose generalement sur l'experience des collaborateurs, sur des calculs manuels ou sur des references non centralisees. Cela entraine des variations de resultat, une perte de temps et une difficulte a uniformiser la reponse commerciale.

Le projet vise donc a mettre en place un logiciel interne, simple d'utilisation, capable de produire une estimation rapide, coherente et presentable, sans realiser un metre detaille complet.

## 3. Objectifs du projet

### 3.1 Objectif general

Mettre a disposition de l'entreprise un logiciel desktop interne permettant de generer des devis approximatifs rapides pour des projets de construction de batiments a Madagascar.

### 3.2 Objectifs specifiques

- Reduire le temps necessaire pour produire une estimation preliminaire.
- Standardiser les regles de chiffrage au sein de l'entreprise.
- Fournir une estimation globale et un detail par grands postes.
- Conserver un historique des devis produits.
- Permettre a un administrateur interne de gerer les prix de base et les coefficients de calcul.
- Offrir un outil d'aide commerciale pour les premiers echanges avec les clients.

## 4. Portee du projet

### 4.1 Perimetre fonctionnel retenu pour la version 1

La version 1 du logiciel couvrira les besoins suivants :

- utilisation interne uniquement par le personnel de l'entreprise ;
- execution sous forme d'application desktop ;
- prise en charge de projets de construction de tous types de batiments ;
- production de devis approximatifs de niveau intermediaire ;
- calcul base sur une methode mixte : prix de base puis ajustements par coefficients ;
- affichage d'un montant estimatif global ;
- affichage d'un detail par grands postes de travaux ;
- enregistrement de l'historique des devis ;
- administration des regles de calcul et des parametres de prix.

### 4.2 Hors perimetre de la version 1

Les fonctionnalites suivantes ne sont pas incluses dans la premiere version :

- metre detaille complet ;
- generation automatique de plans ;
- consultation libre-service par les clients ;
- gestion comptable ou facturation ;
- suivi complet de chantier ;
- multi-agences internationales ou multi-pays ;
- synchronisation avancee avec ERP ou logiciels tiers ;
- calcul structurel technique ou dimensionnement d'ouvrages.

## 5. Beneficiaires et utilisateurs

### 5.1 Beneficiaire principal

L'entreprise de genie civil cliente du projet.

### 5.2 Utilisateurs vises

- commerciaux ;
- techniciens estimateurs ;
- responsables d'etudes ;
- administrateur interne charge de la mise a jour des prix et parametres.

### 5.3 Types de profils

#### a. Utilisateur standard

Peut creer un devis, consulter l'historique, rechercher une estimation existante et imprimer ou exporter un recapitulatif si cette fonction est retenue.

#### b. Administrateur

Dispose des droits supplementaires pour :

- gerer les prix de base ;
- modifier les coefficients d'ajustement ;
- administrer les listes de reference ;
- gerer les comptes utilisateurs si cette option est retenue dans l'implementation.

## 6. Resultats attendus

Le logiciel devra permettre, en quelques minutes, d'obtenir une estimation preliminaire fiable a usage commercial, basee sur des regles homogenes et modifiables.

Chaque devis devra produire au minimum :

- les informations generales du client et du projet ;
- le montant total estime ;
- la ventilation par grands postes ;
- la date de creation ;
- l'identification de l'utilisateur ayant saisi le devis ;
- une trace dans l'historique.

## 7. Description fonctionnelle detaillee

### 7.1 Module 1 : Nouveau devis

Ce module permettra de saisir les informations necessaires a la production d'un devis estimatif.

#### Donnees minimales a saisir

- nom du client ;
- contact du client ;
- type de batiment ;
- localisation du projet ;
- surface totale estimee ;
- nombre d'etages ;
- type de structure ;
- type de toiture ;
- nombre de pieces si pertinent ;
- niveau de finition ;
- observations eventuelles.

#### Exigences fonctionnelles

- le formulaire doit etre simple, clair et rapide a remplir ;
- les champs obligatoires doivent etre identifies ;
- les listes de choix doivent etre parametrees par l'administrateur autant que possible ;
- des controles doivent empecher les valeurs incoherentes, par exemple surface negative ou nombre d'etages invalide.

### 7.2 Module 2 : Calcul estimatif

Ce module aura pour role de transformer les donnees saisies en estimation globale et en detail par lots.

#### Principe de calcul retenu

La methode de calcul reposera sur :

1. une base de prix de reference ;
2. une surface estimee ;
3. des coefficients d'ajustement selon les caracteristiques du projet ;
4. une repartition du montant total par grands postes.

#### Etapes de calcul

1. Selection d'un prix de base selon le type de batiment et, si necessaire, le niveau de finition ou la categorie de projet.
2. Calcul d'un montant initial a partir de la surface.
3. Application de coefficients d'ajustement en fonction des parametres saisis.
4. Production d'un montant global final.
5. Ventilation du montant global en grands postes de travaux.

#### Parametres d'ajustement prevus

- type de batiment ;
- niveau de finition ;
- nombre d'etages ;
- type de structure ;
- type de toiture ;
- localisation ;
- complexite generale du projet.

#### Sorties du calcul

- montant total approximatif ;
- detail par grands postes ;
- hypotheses utilisees pour le calcul ;
- coefficients appliques.

### 7.3 Module 3 : Historique des devis

Le logiciel devra enregistrer les devis deja produits afin de permettre leur consultation ulterieure.

#### Informations a enregistrer

- numero ou identifiant du devis ;
- date et heure de creation ;
- utilisateur createur ;
- nom du client ;
- resume du projet ;
- montant total ;
- detail par lots ;
- commentaires ou remarques.

#### Fonctions attendues

- lister les devis precedents ;
- rechercher par client, date ou type de projet ;
- consulter le detail d'un devis existant ;
- dupliquer un devis pour en creer un nouveau sur une base proche.

### 7.4 Module 4 : Administration

Ce module permettra de maintenir le referentiel de calcul sans intervention du developpeur pour les mises a jour courantes.

#### Elements administrables

- prix de base par type de batiment ;
- coefficients par niveau de finition ;
- coefficients par type de toiture ;
- coefficients par type de structure ;
- coefficients par zone geographique ;
- repartition type par grands postes ;
- listes de valeurs : types de batiments, finitions, structures, toitures, zones, niveaux de complexite.

#### Exigences fonctionnelles

- seules les personnes autorisees peuvent modifier ces donnees ;
- les changements doivent etre sauvegardes de facon fiable ;
- l'interface d'administration doit rester comprehensible pour un utilisateur non developpeur.

## 8. Logique de chiffrage fonctionnelle

### 8.1 Nature du devis

Le devis produit par le logiciel est un devis approximatif d'orientation commerciale. Il ne remplace pas :

- un avant-metre detaille ;
- une etude technique complete ;
- un devis definitif de realisation.

### 8.2 Modele de calcul propose

Formule generale :

Montant estime = (surface x prix de base) x coefficients d'ajustement

Ensuite :

Montant par poste = montant estime x pourcentage du poste

### 8.3 Exemples de postes de ventilation

- etudes et preparation ;
- terrassement et fondations ;
- structure et elevation ;
- charpente et toiture ;
- menuiseries ;
- electricite et plomberie ;
- revetements et finitions ;
- divers et imprevus.

### 8.4 Regles de gestion

- toute estimation doit etre rattachee a un type de batiment ;
- toute estimation doit comporter une surface valide ;
- les coefficients doivent etre parametrables ;
- l'administrateur doit pouvoir corriger les valeurs de reference sans modifier le code source ;
- les montants doivent etre affiches dans la devise definie par l'entreprise, vraisemblablement en Ariary.

## 9. Exigences non fonctionnelles

### 9.1 Ergonomie

- interface simple et professionnelle ;
- navigation claire entre devis, historique et administration ;
- temps de prise en main court ;
- saisie rapide en rendez-vous ou en entretien commercial.

### 9.2 Performance

- affichage rapide des ecrans ;
- calcul quasi instantane pour un devis standard ;
- consultation fluide de l'historique.

### 9.3 Fiabilite

- enregistrement securise des devis ;
- prevention des pertes de donnees ;
- verification des champs obligatoires ;
- gestion propre des erreurs de saisie.

### 9.4 Securite

- acces reserve aux utilisateurs internes ;
- separation des droits entre utilisateur standard et administrateur ;
- protection minimale des donnees stockees localement.

### 9.5 Maintenance

- architecture modulaire ;
- possibilite de faire evoluer les regles de calcul ;
- facilite de maintenance du logiciel apres livraison.

## 10. Contraintes du projet

- le logiciel doit fonctionner en mode desktop ;
- la version 1 doit pouvoir etre utilisee sans connexion internet permanente ;
- l'entreprise ne dispose pas encore d'une base de prix formalisee ;
- une phase de parametrage initial des prix sera donc indispensable ;
- les estimations devront etre adaptees au contexte de Madagascar.

## 11. Donnees de reference a constituer

Avant ou pendant l'implementation, il faudra constituer une base initiale de parametres metier comprenant :

- liste des types de batiments ;
- grille des prix de base ;
- coefficients par finition ;
- coefficients par structure ;
- coefficients par toiture ;
- coefficients par zone ;
- pourcentages de repartition par lot ;
- exemples de devis reels servant de reference metier.

Cette phase est critique, car la qualite des estimations dependra directement de la qualite de ces donnees.

## 12. Proposition d'architecture fonctionnelle

L'application sera organisee autour des blocs suivants :

- interface utilisateur desktop ;
- moteur de calcul estimatif ;
- module de gestion des donnees de reference ;
- base de donnees locale pour les devis et parametres ;
- module d'administration.

Le moteur de calcul devra etre separe de l'interface afin de permettre l'evolution des regles sans remettre en cause l'ensemble du logiciel.

## 13. Ecrans principaux attendus

- ecran d'accueil ;
- ecran de creation d'un devis ;
- ecran d'affichage du resultat ;
- ecran d'historique des devis ;
- ecran de detail d'un devis ;
- ecran d'administration des parametres ;
- ecran de connexion si une authentification est retenue.

## 14. Livrables attendus

Les livrables du projet pourront inclure :

- le logiciel desktop executable ;
- le code source du projet ;
- la base initiale de parametres ;
- un guide utilisateur ;
- un guide administrateur ;
- le present cahier des charges valide ;
- un document de recette ou de tests fonctionnels.

## 15. Planning indicatif du projet

Le planning detaille sera etabli apres validation du present cahier des charges. A titre indicatif, le projet pourra etre mene selon les phases suivantes :

1. cadrage et validation du besoin ;
2. conception fonctionnelle et technique ;
3. constitution de la base initiale de prix et coefficients ;
4. developpement de la version 1 ;
5. tests internes ;
6. recette utilisateur ;
7. corrections et livraison ;
8. formation et prise en main.

## 16. Critères de reussite

Le projet sera considere comme reussi si :

- un utilisateur interne peut creer un devis complet sans assistance technique ;
- le calcul produit un montant global et un detail par postes ;
- les regles de calcul peuvent etre modifiees par un administrateur ;
- l'historique des devis est consultable ;
- le logiciel est stable sur les postes cibles ;
- le client juge l'outil suffisamment rapide et coherent pour un usage commercial initial.

## 17. Risques et points de vigilance

- absence de base de prix initiale deja formalisee ;
- risque d'ecarts entre estimation logicielle et realite chantier si les coefficients sont mal calibres ;
- besoin d'impliquer un referent metier pour valider les regles de calcul ;
- necessite de faire evoluer periodiquement les prix selon le marche ;
- risque d'alourdir la version 1 si trop de cas specifiques sont integres trop tot.

## 18. Recommandations pour la suite

Pour lancer le projet dans de bonnes conditions, il est recommande de proceder ensuite a :

1. la validation du present cahier des charges par le client ;
2. la definition precise des regles de calcul ;
3. la collecte des prix et coefficients de reference ;
4. la production d'un plan de developpement detaille ;
5. la realisation de maquettes d'ecrans avant implementation.

## 19. Conclusion

Le present cahier des charges definit le cadre fonctionnel d'un logiciel desktop interne de devis approximatifs pour projets de construction. La solution vise a accelerer la reponse commerciale, homogeniser les estimations et capitaliser les donnees produites par l'entreprise.

La reussite du projet dependra autant de la qualite du developpement logiciel que de la qualite de la base de prix et des regles metier qui seront definies avec l'entreprise cliente.

# Améliorations globales — Jeannot Devis Bâtiment

Date : 2026-07-13

## Contexte

L'application desktop (PySide6 + SQLite) produit des devis approximatifs de
bâtiment. Un refactor récent a déplacé la logique de calcul vers un moteur
basé sur `matériaux × volume` ([services/calcul_btp.py](../../../src/devis_batiment/services/calcul_btp.py)),
mais plusieurs éléments hérités de l'ancien modèle (« prix au m² ») et des
fonctionnalités jamais branchées subsistent. L'app démarre et les 13 tests
passent, mais il existe du code mort, des incohérences de documentation et des
lacunes d'intégrité en base.

Cette spec couvre un ensemble d'améliorations ciblées, sans refonte de
l'architecture ni du moteur de calcul (qui reste `matériaux × volume`).

## Objectifs

1. Supprimer le système « Profils de prix au m² », déconnecté du calcul.
2. Rendre l'export PDF réellement accessible depuis l'UI.
3. Permettre de rouvrir un devis existant depuis l'historique.
4. Rendre la devise paramétrable effective à l'affichage.
5. Garantir l'intégrité référentielle en base (FK + cascades).
6. Nettoyer le code mort, les incohérences de nommage et le dépôt.
7. Mettre le README en cohérence avec le code actuel.
8. Étendre la couverture de tests aux nouveaux comportements.

## Hors périmètre

- Aucune refonte du moteur de calcul (reste `matériaux × volume`).
- Pas de refactor des styles inline vers `theme.py` (risque de régression
  visuelle ; à traiter séparément si souhaité).
- Pas de nouveau mode d'estimation.

## Lots de travail

### Lot A — Supprimer le système « Profils de prix »

Décision : supprimer entièrement (le calcul n'utilise pas le prix/m²).

- [storage.py](../../../src/devis_batiment/storage.py) : retirer la table
  `pricing_profiles`, son index unique, et les méthodes
  `upsert_pricing_profile`, `delete_pricing_profile`, `fetch_pricing_profiles`.
- [config.py](../../../src/devis_batiment/config.py) : supprimer
  `DEFAULT_PRICING_PROFILES`.
- [services/__init__.py](../../../src/devis_batiment/services/__init__.py) :
  supprimer `save_pricing_profile`, `list_pricing_profiles`,
  `delete_pricing_profile`, et le bloc de seed correspondant dans
  `seed_defaults_if_empty`.
- [admin_view.py](../../../src/devis_batiment/ui/admin_view.py) : supprimer
  l'onglet « Prix de base », la table `pricing_table`, `_load_pricing`,
  `_add_pricing`, `_del_pricing`, la classe `_PricingDialog`, et la constante
  `BUILDING_TYPES`. L'onglet Admin conserve « Coefficients » et « Répartition ».

Les bases existantes conservent la table orpheline (non supprimée par
migration) ; ce n'est pas un problème fonctionnel. Pas de migration destructive.

### Lot B — Brancher l'export PDF

- [pyproject.toml](../../../pyproject.toml) : ajouter `reportlab>=4.0,<5.0` aux
  dépendances runtime.
- [quote_result.py](../../../src/devis_batiment/ui/quote_result.py) : ajouter un
  bouton « Exporter en PDF ». Au clic : `QFileDialog.getSaveFileName` (défaut
  `devis_<id>.pdf`), puis appel à `export_quote_pdf(output_path, company_info,
  quote_id, quote_input, estimate)`. `company_info` est construit depuis
  `SettingsService.get_all()`. Succès → message d'information ; échec →
  `QMessageBox.critical`.
- Le widget mémorise le dernier `quote_id`, `quote_input`, `estimate` reçus dans
  `show_result`. Le bouton est désactivé tant qu'aucun résultat n'est affiché.
- [main_window.py](../../../src/devis_batiment/ui/main_window.py) : injecter
  `settings_service` dans `QuoteResultWidget` (constructeur ou setter).

### Lot C — Réouverture d'un devis depuis l'historique

- [history_view.py](../../../src/devis_batiment/ui/history_view.py) : émettre
  `open_quote_requested(quote_id)` sur double-clic d'une ligne
  (`cellDoubleClicked` / `itemDoubleClicked`).
- [main_window.py](../../../src/devis_batiment/ui/main_window.py) : connecter ce
  signal à un handler qui lit `Database.fetch_quote_payload(quote_id)`,
  reconstruit `QuoteInput` et `QuoteEstimate` (comme
  `QuoteService.duplicate_quote`, mais sans réinsérer), puis appelle
  `quote_result.show_result(...)` et bascule sur l'onglet résultat.
- Affichage **lecture seule** : on relit l'estimate persistée, aucun recalcul.
- Refactor léger : extraire la reconstruction `payload → (QuoteInput,
  QuoteEstimate)` dans une méthode réutilisable de `QuoteService` (ex.
  `load_quote(quote_id) -> tuple[QuoteInput, QuoteEstimate]`) pour éviter la
  duplication avec `duplicate_quote`.

### Lot D — Devise cohérente

- Remplacer les helpers `_fmt_mga` codant « Ar » en dur dans
  [quote_result.py](../../../src/devis_batiment/ui/quote_result.py),
  [history_view.py](../../../src/devis_batiment/ui/history_view.py) et
  [dashboard_view.py](../../../src/devis_batiment/ui/dashboard_view.py) par un
  formatage prenant la devise en paramètre, alimenté par
  `settings.currency` (fallback « Ar »).
- Les vues concernées reçoivent la devise via `SettingsService` (déjà
  disponible dans `MainWindow`) au moment du `refresh`/`show_result`.

### Lot E — Intégrité base de données

- [storage.py](../../../src/devis_batiment/storage.py) : exécuter
  `PRAGMA foreign_keys = ON` sur chaque connexion (`_connect`).
- Ajouter `ON DELETE CASCADE` sur `projects.client_id → clients.id` et
  `quote_lines.quote_id → quotes.id` dans le schéma `CREATE TABLE`.
- Comportement voulu : supprimer un client supprime ses projets.
- Bases existantes : les FK ne sont pas rétro-ajoutées (SQLite ne modifie pas
  une contrainte de table existante) ; comportement garanti sur base neuve.
  Documenter ce point dans le README.

### Lot F — Nettoyage & cohérence

- Supprimer la base obsolète `devis_batiment.db` à la racine (la base active
  est `database/db.sqlite`).
- Uniformiser le nom de l'application en « Jeannot Devis Bâtiment » :
  titre de fenêtre et label d'en-tête ([main_window.py](../../../src/devis_batiment/ui/main_window.py)),
  `build_app_metadata` ([app.py](../../../src/devis_batiment/app.py)),
  `SETTING_DEFAULTS["company_name"]` ([services/__init__.py](../../../src/devis_batiment/services/__init__.py)),
  et les valeurs par défaut du PDF ([utils/pdf.py](../../../src/devis_batiment/utils/pdf.py)).
- [admin_view.py](../../../src/devis_batiment/ui/admin_view.py) : remonter
  l'import `from devis_batiment.services import AdminService` en tête de fichier,
  supprimer le no-op `self.category.setCurrentIndex(...)` et la classe morte
  `_CategoryCombo`.
- Resserrer les `except Exception` là où une exception précise est identifiable
  (sans changer le comportement UI de repli).

### Lot G — README à jour

- [README.md](../../../README.md) : corriger la section Structure (plus de
  `calculator.py`/`services.py` ; présence de `services/`, `utils/pdf.py`,
  nouvelles vues), et la Formule de calcul (`matériaux × volume × coefficients`
  au lieu de `surface × prix_base`). Mentionner l'export PDF et la note FK
  (base neuve).

### Lot H — Tests

Ajouter des tests (exécutés avec `QT_QPA_PLATFORM=offscreen`) :

- Export PDF : `export_quote_pdf` produit un fichier non vide à partir d'un
  `QuoteInput`/`QuoteEstimate` de référence.
- Réouverture : `QuoteService.load_quote` reconstruit fidèlement input/estimate
  depuis un devis persisté.
- Intégrité FK : sur base neuve, supprimer un client supprime ses projets.
- Devise : le formatage reflète la devise configurée.
- Non-régression : suppression des profils de prix ne casse pas le seed ni
  l'ouverture de la fenêtre principale ; toute la suite passe.

## Ordre d'exécution suggéré

E (schéma/FK) → A (suppression profils) → C (réouverture, dépend du service) →
B (PDF) → D (devise) → F (nettoyage) → G (README) → H (tests), avec exécution
de la suite de tests après chaque lot à effet fonctionnel.

## Critères de succès

- `QT_QPA_PLATFORM=offscreen pytest` : 100 % vert, tests nouveaux inclus.
- L'app démarre, l'onglet Admin n'a plus « Prix de base ».
- Export PDF fonctionnel depuis l'écran résultat.
- Double-clic sur un devis de l'historique rouvre son résultat.
- La devise configurée s'affiche partout.
- Suppression d'un client (base neuve) supprime ses projets.
- README cohérent avec le code.

# Catalogue d'outils evalues pour l'ecosysteme HUMEAN

Ce fichier vit dans le repo plutot que dans la memoire personnelle de Claude, car
la memoire personnelle ne conserve que ce que l'utilisateur affirme sur lui-meme,
pas les resultats de recherche ou les evaluations d'outils. Ce fichier, lui, est
relisible par Claude a chaque session future en le recuperant depuis GitHub.

Mise a jour au fil des listes d'outils envoyees par l'utilisateur (issues de recherches
Claude Code communautaires). Statut : a-installer / installe / ecarte, avec la raison.

## Deja actif

- **Security Guidance** (catalogue plugins Claude) et **anthropics/claude-code-security-review**
  (Action GitHub officielle) : les deux poussés sur `fact-check-app` et `time-travel-companion`
  le 2026-09-20. Necessite un secret `CLAUDE_API_KEY` par repo (a ajouter par l'utilisateur).
- **frontend-design** (skill interne Claude) : deja utilise pour le redesign dossier/tampon
  de Fact Check et billet d'embarquement de Time & Travel.

## Pertinents, pas encore installes

- **Design** (plugin catalogue) : critique design, audits accessibilite, specs pixel-perfect.
- **Marketing** (plugin catalogue) : utile pour SMV en phase de croissance (contenu, concurrents).
- **Engineering** (plugin catalogue) : standups, revue de code, decisions d'architecture.
- **Ui ux pro max** (`nextlevelbuilder/ui-ux-pro-max-skill`) + **Task observer**
  (bundle `anupkatuwal/claude-skills`) : importables directement dans claude.ai via
  Customize -> Skills (ZIP), pas besoin de terminal.
- **Unlazy** (`Leonxlnx/unlazy`, terminal Claude Code) : methode anti-paresse "Depth Tree",
  force a creuser chaque sous-tache en profondeur plutot que s'arreter tot.
- **Claude-mem** (`thedotmack/claude-mem`, terminal Claude Code) : memoire persistante
  inter-sessions pour Claude Code (different de la memoire de claude.ai).
- **Competitor ads extractor** : pertinent pour SMV (analyse pub des concurrents comparateurs).
- **Planning with files** : formaliser un fichier de plan par projet, dans la continuite
  des specs deja publiees.
- **Graphipy** : graphe de connaissances entre projets (HUMEAN, SMV, Fact Check, Time & Travel,
  iGuess, AlterEgo, chaine YouTube) -- interessant maintenant que ca commence a se referencer.

## Hors sujet pour les apps web actuelles (SMV / Fact Check / Time & Travel)

- **Remotion**, **Elevenlabs** : montage video programmatique / voix off -- pour la chaine
  YouTube "La boite a Boulon", pas pour les apps.
- **Content research writer** : redaction de contenu -- utile plus tard pour du marketing SMV.
- **Headroom** (deux outils distincts trouves sous ce nom : appli menu-bar de reduction de
  cout tokens, ou barre d'usage de fenetre de contexte) : gestion de budget, pas de code produit.
- **Claude stack** : pas de projet unique identifie sous ce nom exact, a preciser si l'utilisateur
  retrouve la source.
- **Context engineering** : methodologie/mot-cle general, pas un outil specifique.

## A eviter d'installer sans verification

Tous les outils communautaires ci-dessus (non listes comme "officiel Anthropic") sont du code
tiers non verifie -- lire le code avant de lancer une installation qui s'execute avec les droits
de Claude Code sur la machine de l'utilisateur.


## Architectures de reference trouvees par recherche proactive (pas des installs, des inspirations)

- **WikiCheck** (`trokhymovych/WikiCheck`) : API de fact-checking basee sur Wikipedia, open source,
  developpee avec la Wikimedia Foundation. Candidat serieux comme vrai connecteur source niveau 1/2
  pour Fact Check V2, pas juste une reference.
- **reverify** (`2akouwu/reverify`, 1231 etoiles) : meme principe que notre moteur -- des outils
  deterministes tranchent, chaque affirmation verifiee contre une verite terrain. A etudier pour
  comparer notre architecture.
- **ClaimeAI** (`BharathxD/ClaimeAI`) : decoupe un texte en affirmations verifiables individuelles
  via LangGraph. Meme logique que notre moteur, implementation alternative a comparer.
- **voyant** (`chernistry/voyant`) : agent de voyage avec verification factuelle -- croisement
  interessant entre Fact Check et Time & Travel.
- **MyTripPlanner** (`Prot10/MyTripPlanner`) : concurrent direct le plus proche de Time & Travel
  (self-hosted, vrais hotels/restos/budget). A regarder pour ce qu'ils ont resolu qu'on n'a pas encore.
- **hesreallyhim/awesome-claude-code** (54k etoiles) : liste de reference maitresse a checker en
  premier avant toute future evaluation d'outil individuel.

Trouves via recherche GitHub proactive (triee par etoiles) plutot qu'a partir d'un nom fourni --
a refaire periodiquement, pas seulement quand l'utilisateur envoie une liste.

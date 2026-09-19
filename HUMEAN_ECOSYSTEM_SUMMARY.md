# HUMEAN Ecosystem — Document de synthèse (septembre 2026)
> Document de passation/contexte, à transmettre pour toute reprise du projet ailleurs (autre chat IA, repo GitHub, nouveau collaborateur).

---

## 1. Vue d'ensemble de l'écosystème

Trois briques distinctes, à ne pas confondre :

```
HUMEAN / OMNIROUTE          ← infrastructure générique (invisible pour l'utilisateur final)
        │
   ┌────┴────┐
   ▼         ▼
  SMV    TIME & TRAVEL       ← applications concrètes, mono-domaine, mono-audience
(avancé)     (concept)
```

**Règle produit fondamentale** : HUMEAN/OmniRoute reste générique et invisible. Chaque application reste volontairement étroite (un domaine, un public), pour éviter de reproduire la dérive "trop vaste" qu'a connue HUMEAN à ses débuts.

**Domaines explicitement écartés pour l'instant** : logistique, aéronautique, pharmaceutique, ingénierie — trop réglementés, cycles de vente B2B trop longs, aucune expérience/légitimité de départ sur ces secteurs. Pas de nouveau domaine tant que SMV ou Time&Travel n'a pas d'utilisateur réel.

**Objectif économique transversal** : viser l'autofinancement — coûts (API, hébergement) inférieurs aux revenus, pour que le développement reste soutenable sans financement externe.

---

## 2. HUMEAN / OmniRoute — l'infrastructure

### 2.1 Répartition des rôles

- **OmniRoute** = moteur d'orchestration/routage dynamique. Répond à *"qui doit faire quoi ?"* — décompose une tâche, identifie les capacités nécessaires, sélectionne agent/modèle/outil/source, exécute, vérifie.
- **HUMEAN** = couche supérieure de contrôle au-dessus d'OmniRoute : mémoire, évaluation, gouvernance, risque, audit. Répond à *"pourquoi cette combinaison ? est-elle fiable ? que fait-on du résultat ?"*
- **MetaCortex** = nom possible de la couche de délibération/orchestration de HUMEAN (pas une "super-IA" autonome — explicitement écarté du périmètre).

### 2.2 Noyau fonctionnel retenu
Task Decomposition · Capability Registry · Dynamic Routing · Multi-Agent/Multi-Model Deliberation · Evidence & Provenance · Uncertainty · Memory · Performance Evaluation · Risk/Policy Engine · Human Gate · Audit.

### 2.3 Idées explicitement abandonnées du périmètre produit
Conscience artificielle · IA cherchant à se libérer ou développant une volonté propre · "super-IA" centrale · agrégation systématique de tous les LLM.

### 2.4 Capability Registry
Schéma SQL défini (PostgreSQL/Supabase) : table `capabilities` (id, type, domaine, coût, latence, fiabilité, statut), `capability_performance_log` (résultats réels d'exécution), `registry_diffs` (propositions de mise à jour, jamais appliquées directement), vue `capability_scores`.

**Capacités identifiées au démarrage** :

| id | statut | accès |
|---|---|---|
| claude-sonnet-4-6 | active | abonnement |
| gemini | active | clé API |
| deepseek-chat | active | clé API |
| grok-free | candidate | web only, pas d'API |
| chatgpt-free | candidate | web only, pas d'API |

### 2.5 Environment Watch / Self-Update Loop
Module de veille qui détecte les changements externes (nouveaux modèles, tarifs, dépréciations) et propose des diffs structurés au registre — jamais d'application automatique silencieuse. Validation auto uniquement si haute confiance + faible impact ; sinon passage obligatoire par un **Human Gate**.

### 2.6 État du prototype
**Aucun code encore écrit** — uniquement de la conception/architecture. Deux premiers livrables produits en session (schéma SQL du registre + script Python de test Claude/Gemini/DeepSeek avec log JSON local), à récupérer et intégrer manuellement.

---

## 3. SMV / SaveMoneyReminder — application n°1 (la plus avancée)

Comparateur/simulateur d'économies sur les abonnements (internet, mobile, musique, TV/streaming, assurance auto, énergie, banque).

**Stack réelle** (construite via Emergent, emergent.sh) :
- Frontend : React 19, Tailwind CSS, framer-motion, Lenis
- Backend : FastAPI (Python), MongoDB (motor)
- Email transactionnel via intégration Emergent (proxy Resend)

**État fonctionnel** : app publique sans compte utilisateur, 115 offres en base (112 particulier + 3 pro), 7 secteurs, 52 fournisseurs. Moteur de calcul validé (compare au meilleur prix du pool filtré, calcule économie annuelle nette des frais de résiliation estimés). Capture de leads + envoi d'email réel opérationnels.

**Modèle produit** : "pur comparateur" — redirection vers le fournisseur, sans traitement de documents/justificatifs, avec instructions claires de résiliation/changement pour chaque offre.

**Modèle économique** : phase de croissance gratuite d'abord, puis monétisation (CPA/premium). Structure de coûts saine : les appels LLM servent à enrichir la base d'offres (coût fixe, indépendant du nombre d'utilisateurs), pas à répondre en temps réel à chaque utilisateur — donc pas (encore) de risque de coût-par-requête qui grimpe avec le trafic.

**Backlog connu** :
- P1 : vérification mobile, export PDF, pages légales réelles
- P2 : comptes utilisateurs, alertes prix, page admin des leads, scraping fournisseurs automatisé, mode sombre
- Limite actuelle : le scraping des prix fournisseurs réel n'est pas branché (le pipeline attend un JSON déjà préparé)

---

## 4. Time & Travel Companion — application n°2 (concept)

Assistant intelligent du temps libre, des sorties et des déplacements (nom non défini). L'utilisateur indique quand/où/avec qui/budget/envie ; le moteur construit des scénarios de sorties/voyages réalisables (activité + repas + déplacement + budget), du format "1h de pause déjeuner" au road-trip longue distance avec gestion carburant/recharge électrique.

**État** : cahier des charges détaillé et abouti (scénarios d'acceptation, hiérarchie stricte des sources, architecture à connecteurs modulaires par fournisseur de données), **aucun code, aucun choix technique arrêté**.

**Principes clés** : jamais inventer une donnée (prix, horaire, disponibilité) ; hiérarchie de sources (officiel > institutionnel > partenaires > agrégateurs) avec horodatage de vérification ; ne jamais déduire une caractéristique personnelle sensible (ex. religion) à partir du contexte calendaire.

**Segmentation recommandée** pour un MVP réaliste : commencer par les scénarios simples ("j'ai 2h autour de moi", "ce soir, budget X") avant d'ajouter calendrier/composition de journée, puis seulement ensuite road-trip longue distance et festivals.

---

## 5. Ce que ce document ne couvre pas
Ce résumé synthétise les décisions et l'architecture — il ne remplace pas le `CONTEXT.md` technique détaillé de SMV (modèle de données complet, API, commandes, état des tests) pour toute reprise fine du code.

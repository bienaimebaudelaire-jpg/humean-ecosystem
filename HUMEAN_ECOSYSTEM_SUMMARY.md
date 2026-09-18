# HUMEAN Ecosystem — Document de synthèse (septembre 2026)

> Document de passation et source de contexte. HUMEAN/OmniRoute est l'infrastructure générique ; les applications restent ciblées.

## Vue d'ensemble

```text
HUMEAN / OMNIROUTE          infrastructure générique
        │
   ┌────┴────┐
   ▼         ▼
  SMV    TIME & TRAVEL       applications ciblées
```

- **OmniRoute** décompose une tâche, identifie les capacités requises, sélectionne les agents/modèles/outils/sources, exécute et vérifie.
- **HUMEAN** fournit mémoire, évaluation, gouvernance, risque, audit, provenance et human gate.
- **SMV / SaveMoneyReminder** est la première application concrète et la plus avancée.
- **Time & Travel Companion** est un concept ; aucun code ni choix technique n'est arrêté.

Domaines écartés pour l'instant : logistique, aéronautique, pharmaceutique et ingénierie. Aucun nouveau domaine avant un usage réel sur SMV ou Time & Travel.

## Noyau fonctionnel

Task Decomposition · Capability Registry · Dynamic Routing · Multi-Agent/Multi-Model Deliberation · Evidence & Provenance · Uncertainty · Memory · Performance Evaluation · Risk/Policy Engine · Human Gate · Audit.

Sont explicitement hors périmètre : conscience artificielle, volonté propre, super-IA centrale, auto-réécriture silencieuse et agrégation systématique de tous les LLM.

## Capability Registry

Le registre décrit les capacités, leur domaine, coût, latence, fiabilité, statut et performances réelles. Les changements externes produisent des `registry_diffs` proposés ; ils ne sont jamais appliqués silencieusement.

Capacités initiales indicatives : Claude Sonnet, Gemini et DeepSeek lorsqu'une API légitime est disponible. Les accès web gratuits restent des candidats et ne doivent pas être automatisés par contournement de quotas.

## Auto-mise à jour contrôlée

```text
veille externe → détection → diff proposé → évaluation du risque → human gate → application
```

HUMEAN peut apprendre des résultats d'exécution et mettre à jour des scores avec des données observées. Il ne réécrit pas son code ni ses politiques critiques de façon autonome.

## Applications

### SMV / SaveMoneyReminder

Comparateur d'économies sur les abonnements. Stack actuelle : React/Tailwind côté frontend, FastAPI/MongoDB côté backend. L'application est déjà fonctionnelle avec une base d'offres, calcul d'économies, capture de leads et email transactionnel.

Priorités : vérification mobile, export PDF et pages légales réelles. Le scraping réel des prix reste à automatiser.

### Time & Travel Companion

Assistant de sorties et déplacements avec scénarios vérifiables. Commencer par « j'ai deux heures autour de moi » et « ce soir, budget X ». Ne jamais inventer un prix, un horaire ou une disponibilité ; chaque donnée doit porter sa source et son horodatage.

## Objectif économique

Viser l'autofinancement : coûts API et hébergement inférieurs aux revenus. Les quotas gratuits sont des opportunités légitimes, jamais le socle d'une stratégie de contournement des limites ou des conditions d'utilisation.

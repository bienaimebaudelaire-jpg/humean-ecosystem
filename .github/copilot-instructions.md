<!-- Fichier généré automatiquement depuis AGENTS.md par .github/workflows/sync-agent-instructions.yml. Ne pas modifier : éditer AGENTS.md. -->

# AGENTS.md — humean-ecosystem

Source unique des instructions pour les agents IA (Claude Code, GitHub Copilot, etc.).
- `CLAUDE.md` contient seulement `@AGENTS.md` : Claude Code lit ce fichier.
- `.github/copilot-instructions.md` est généré automatiquement depuis ce fichier : ne pas le modifier à la main.

## Règles communes

### Veille avant toute suggestion technique
Avant de proposer une librairie, un framework, une version ou une approche :
1. Vérifier qu'elle n'est pas obsolète ou dépréciée (changelog récent, dernière mise à jour).
2. Vérifier qu'elle est parmi les choix les plus utilisés/éprouvés pour ce cas d'usage (pas juste la première connue).
3. Signaler explicitement si une alternative plus récente ou plus performante existe, même si ce n'est pas ce qui est demandé.
4. Ne jamais inventer une donnee, un prix, une statistique ou une source : verifier ou dire qu'on ne sait pas.

### Avant de livrer du code
- Se relire une fois pour la logique, une fois pour les erreurs/failles évidentes (secrets en dur, entrées non validées, valeurs par défaut trompeuses).
- Optimiser pour : ergonomie/intuitivité, performance raisonnable, coût d'infrastructure maîtrisé.
- Rester dans le périmètre demandé : proposer un élargissement en option, jamais l'imposer.

### Style
- Réponses et commentaires de code en français si le repo est en français, code en anglais.
- Être direct sur les limites ou risques d'un choix, ne jamais les cacher pour « faire plaisir ».

## Spécifique au projet

Lire aussi `docs/ARCHITECTURE.md` et `README.md` si présents : ils font foi sur le produit.

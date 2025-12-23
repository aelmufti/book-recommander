# Book Finder - Frontend

## Description

Interface de recherche de livres utilisant le design **Liquid Glass** - une évolution du glassmorphism classique vers une esthétique plus vivante et organique.

### Concept visuel

L'interface simule des panneaux de verre transparent flottant au-dessus d'un fond coloré. Les éléments clés :

- **Fond dégradé** : tons beige/taupe chaleureux évoquant une bibliothèque
- **Orbes colorés animés** : formes fluides (ambre, mauve, bleu) visibles à travers le verre, créant profondeur et mouvement
- **Cartes en verre** : vraiment transparentes avec fort blur (40px), laissant voir et déformant les couleurs derrière
- **Reflets dynamiques** : le highlight suit le curseur de la souris, simulant la lumière sur du verre réel
- **Bordures lumineuses** : ligne blanche en haut de chaque carte imitant la réfraction de la lumière

### Fonctionnalités

1. **Sélecteur de langue** : 6 langues disponibles (FR, EN, ES, DE, IT, PT) avec option "Toutes les langues"

2. **Recherche par mots-clés** :
   - Système de tags : l'utilisateur tape un mot puis appuie sur Entrée
   - Maximum 6 mots-clés
   - Tags supprimables individuellement
   - Animation d'apparition des tags

3. **Résultats** :
   - Cartes animées avec apparition en cascade
   - Affichage : titre, auteur, note, nombre d'avis, tier de popularité, langue
   - Premier résultat mis en avant (🏆)
   - Indication si l'IA a enrichi la recherche

### Stack technique

- **React** avec hooks (useState, useEffect, useRef)
- **Tailwind CSS** pour les utilitaires
- **CSS custom** pour les effets liquid glass
- **Vite** comme bundler

### Effets CSS notables

```css
/* Blur de réfraction */
backdrop-filter: blur(40px) saturate(140%);

/* Reflet suivant le curseur */
background: radial-gradient(
  circle 200px at var(--mouse-x) var(--mouse-y),
  rgba(255, 255, 255, 0.35) 0%,
  transparent 60%
);

/* Bordure lumineuse */
border: 1px solid rgba(255, 255, 255, 0.3);
box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.4);
```
T
### Lancer le projet

```bash
cd frontend
npm install
npm run dev
```

Le frontend communique avec le backend sur `/recommend` (POST).

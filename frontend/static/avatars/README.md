# Avatars des personas

Dépose ici une image par persona pour qu'elle apparaisse dans la tuile "visio"
du mode vocal, à la place du rond coloré avec l'initiale :

- `claire.jpg` (ou `.jpeg` / `.png` / `.webp`)
- `marc.jpg`
- `lea.jpg`
- `hugo.jpg`

Le nom de fichier doit correspondre exactement à l'id de la persona (en
minuscules, sans accent). N'importe laquelle des extensions ci-dessus
fonctionne — le frontend essaie `.jpg`, puis `.jpeg`, `.png`, `.webp` dans cet
ordre, et retombe automatiquement sur le rond coloré + initiale si aucune
image n'est trouvée pour une persona donnée. Pas besoin de toucher au code :
il suffit d'ajouter les fichiers ici (`frontend/static/avatars/`) et de
relancer `npm run dev` si le serveur tournait déjà.

Une image carrée (au moins 200x200px) donne le meilleur rendu, mais toute
image fonctionne — elle est recadrée automatiquement en cercle.

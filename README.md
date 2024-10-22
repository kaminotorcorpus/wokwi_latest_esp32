# wokwi_latest_esp32
Wokwi python librarie to generate HTML with latest result

Explication du script :
Requête HTTP : Le script utilise requests pour envoyer des requêtes à l'URL spécifiée.
Analyse du HTML : BeautifulSoup est utilisé pour analyser la page HTML renvoyée et extraire les projets. Il faut trouver la bonne balise qui contient les titres des projets.
Pagination : Si la page prend en charge la pagination, le script parcourt plusieurs pages jusqu'à atteindre le nombre de projets désiré (500 dans ton cas).
Stockage des projets : Chaque projet est ajouté à une liste avec son titre et son lien.

import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime

# Fichier pour stocker les projets déjà récupérés
PROJET_JSON_FILE = 'projets_enregistres.json'

# Fonction pour charger les projets enregistrés à partir d'un fichier JSON
def charger_projets_enregistres():
    try:
        with open(PROJET_JSON_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []  # Si le fichier n'existe pas, retourner une liste vide

# Fonction pour sauvegarder les projets dans un fichier JSON
def sauvegarder_projets_enregistres(projets):
    with open(PROJET_JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(projets, f, ensure_ascii=False, indent=4)

# Fonction pour récupérer les projets de la section "Latest Projects" uniquement
def get_latest_projects(url):
    projects = []
    seen_links = set()  # Utiliser un ensemble pour vérifier les doublons

    try:
        response = requests.get(url, timeout=10)  # Timeout après 10 secondes
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la récupération de la page {url}: {e}")
        return projects

    if response.status_code != 200:
        print(f"Erreur HTTP lors de la récupération de la page: Status {response.status_code}")
        return projects

    soup = BeautifulSoup(response.text, 'html.parser')

    # Trouver la section "Latest Projects" en utilisant une classe spécifique
    latest_projects_section = soup.find('section', {'id': 'latest-projects'})

    # Si la section n'est pas trouvée, retourner une liste vide
    if not latest_projects_section:
        print("Impossible de trouver la section 'Latest Projects'.")
        return projects

    # Récupérer les projets dans la section "Latest Projects"
    project_elements = latest_projects_section.find_all('a', class_='MuiTypography-root MuiTypography-inherit MuiLink-root MuiLink-underlineAlways css-1w2fn6y')

    # Extraire les informations des projets
    for project in project_elements:
        title = project.text.strip()
        link = project['href']

        # Vérifier si le lien est absolu ou relatif
        if not link.startswith('http'):
            full_link = f"https://wokwi.com{link}"  # Si c'est un lien relatif, ajouter le domaine
        else:
            full_link = link  # Si c'est déjà un lien complet, pas besoin de le modifier

        # Extraire la miniature s'il y a une balise img dans le projet
        img_element = project.find_previous('img')  # Si l'image se trouve avant l'élément <a>
        img_src = img_element['src'] if img_element else 'https://via.placeholder.com/150'  # Placeholder si pas d'image

        # Créer un dictionnaire pour stocker les infos du projet
        project_data = {
            'title': title,
            'link': full_link,
            'image': img_src,
            'retrieved_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Ajout de la date de récupération
        }

        projects.append(project_data)

    return projects

# Fonction pour générer un fichier HTML
def generate_html(projects, output_file='projects.html'):
    html_content = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Latest ESP32 Projects</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f4f4f9;
                margin: 0;
                padding: 0;
            }
            h1 {
                text-align: center;
                margin: 20px 0;
                color: #333;
            }
            .container {
                display: flex;
                flex-wrap: wrap;
                justify-content: center;
                padding: 0 20px;
            }
            .project {
                border: 1px solid #ddd;
                border-radius: 8px;
                margin: 10px;
                padding: 20px;
                width: 300px;
                background-color: white;
                text-align: center;
                box-shadow: 2px 2px 12px rgba(0, 0, 0, 0.1);
                transition: transform 0.3s, box-shadow 0.3s;
            }
            .project img {
                max-width: 100%;
                height: auto;
                border-radius: 4px;
            }
            .project h3 {
                font-size: 18px;
                color: #007BFF;
                margin: 10px 0;
            }
            .project a {
                text-decoration: none;
                color: #007BFF;
                font-weight: bold;
            }
            .project a:hover {
                color: #0056b3;
            }
            .project:hover {
                transform: translateY(-10px);
                box-shadow: 4px 4px 20px rgba(0, 0, 0, 0.2);
            }

            /* Media Queries for responsiveness */
            @media (max-width: 768px) {
                .project {
                    width: 45%;
                }
            }
            @media (max-width: 480px) {
                .project {
                    width: 100%;
                }
            }
        </style>
    </head>
    <body>
        <h1>Latest ESP32 Projects</h1>
        <div class="container">
    '''

    # Ajouter chaque projet dans le HTML
    for project in projects:
        html_content += f'''
            <div class="project">
                <img src="{project['image']}" alt="Project Image">
                <h3>{project['title']}</h3>
                <a href="{project['link']}" target="_blank">View Project</a>
                <p>Ajouté le {project['retrieved_at']}</p>
            </div>
        '''

    html_content += '''
        </div>
    </body>
    </html>
    '''

    # Écrire le contenu HTML dans un fichier
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"Le fichier HTML a été généré : {output_file}")

# Boucle infinie pour scanner toutes les minutes
url = "https://wokwi.com/esp32"

projets_enregistres = charger_projets_enregistres()

while True:
    print("Scanning for new projects...")

    # Récupérer les nouveaux projets
    nouveaux_projets = get_latest_projects(url)

    # Ajouter uniquement les nouveaux projets
    nouveaux_ajouts = [p for p in nouveaux_projets if p['link'] not in {proj['link'] for proj in projets_enregistres}]

    if nouveaux_ajouts:
        print(f"{len(nouveaux_ajouts)} nouveaux projets trouvés.")
        projets_enregistres.extend(nouveaux_ajouts)
        sauvegarder_projets_enregistres(projets_enregistres)
        generate_html(projets_enregistres[::-1])

    else:
        print("Aucun nouveau projet trouvé.")

    # Attendre 60 secondes avant de recommencer
    time.sleep(60)

# MDO SMART GUIDE

Application Streamlit d'accueil et d'accompagnement des étudiants de première année MDO à l'ESTC.

## Lancer en local
```bash
python3 -m pip install -r requirements.txt
python3 -m streamlit run app.py
```

Le dossier `assets/` doit rester à côté de `app.py` : il contient l'image originale de l'emploi du temps S1 extraite du livret fourni.

## Assistant
L'assistant est un moteur documentaire local, sans API payante. Il recherche des correspondances parmi les informations du livret et indique lorsqu'il ne trouve pas de réponse fiable. Il ne s'agit pas d'un modèle génératif comparable à ChatGPT.

## Déploiement
Déployer le dépôt sur Streamlit Community Cloud en sélectionnant `app.py` comme fichier principal.

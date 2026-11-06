import streamlit as st
from pathlib import Path
import re
import unicodedata
from difflib import SequenceMatcher

# ============================================================
# MDO SMART GUIDE — ESTC / INED / MDO — 2026/2027
# Assistant documentaire gratuit : réponses issues du livret.
# Aucun appel API, aucune clé secrète, aucune donnée externe.
# ============================================================

st.set_page_config(
    page_title="MDO SMART GUIDE | ESTC",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- STYLE ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Manrope:wght@500;600;700;800&display=swap');
:root { --purple:#392064; --purple2:#5B3A91; --teal:#20B8B0; --ink:#24213A; }
.stApp { background:linear-gradient(180deg,#F8F6FC 0%,#F4F8FA 100%); color:var(--ink); }
html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }
[data-testid="stSidebar"] { background:linear-gradient(180deg,#281449,#40236B); }
[data-testid="stSidebar"] * { color:#fff !important; }
[data-testid="stSidebar"] .stRadio label { padding:5px 0; }
h1,h2,h3 { font-family:'Manrope',sans-serif !important; color:#392064 !important; }
.hero { background:linear-gradient(120deg,#35205D,#65439A); padding:2rem 2.2rem; border-radius:22px; color:white; margin-bottom:1.2rem; box-shadow:0 12px 30px rgba(47,26,83,.13); }
.hero h1 { color:white !important; font-size:2.35rem; margin:0 0 .5rem 0; }
.hero p { color:#F1EAFE; font-size:1.05rem; margin:0; }
.kpi { background:white; border:1px solid #EAE4F4; border-radius:16px; padding:1rem; min-height:112px; }
.kpi .num { color:#20AFA8; font-size:1.65rem; font-weight:800; }
.kpi .lbl { color:#615B70; font-size:.9rem; }
.info-card { background:white; border:1px solid #EAE4F4; border-left:5px solid #20B8B0; border-radius:13px; padding:1rem 1.1rem; margin:.5rem 0; }
.small-muted { color:#777187; font-size:.85rem; }
div.stButton > button { border-radius:11px; border:0; background:#20B8B0; color:white; font-weight:700; }
div.stButton > button:hover { background:#168E89; color:white; }
[data-testid="stMetric"] { background:white; padding:14px; border:1px solid #eee8f5; border-radius:14px; }
.stTabs [data-baseweb="tab-list"] { gap:8px; }
.stTabs [data-baseweb="tab"] { background:#eee9f6; border-radius:10px 10px 0 0; padding:10px 16px; }
hr { border-color:#E8E1F0; }
</style>
""", unsafe_allow_html=True)

# ---------- SOURCE DATA ----------
S1 = {
    "Langues": ["Langue française", "Business English"],
    "Méthodologie de travail universitaire": ["Institutions administratives et politiques (Arabe)"],
    "Économie et management": ["Économie générale", "Management des organisations"],
    "Mathématiques appliquées": ["Mathématiques appliquées"],
    "Comptabilité financière": ["Comptabilité financière"],
    "Mathématiques et statistiques": ["Mathématiques financières", "Statistiques descriptives"],
    "Informatique de base": ["Informatique de base"],
}
S2 = {
    "Langues": ["Langue française", "Business English"],
    "Compétences informatiques et digitales": ["Compétences informatiques et digitales"],
    "Système juridique": ["Système juridique des organisations", "Droit commercial"],
    "Comptabilité financière": ["Comptabilité financière"],
    "Marketing et management commercial": ["Marketing fondamental", "Management commercial"],
    "GRH et droit social": ["Introduction à la gestion des ressources humaines", "Droit social"],
    "Statistiques et informatique de gestion": ["Statistique probabiliste", "Logiciels de gestion"],
}
FAQ = [
("Que signifie MDO ?", "MDO signifie Management Digital des Organisations. La filière associe les principes du management et de la gestion d’entreprise aux technologies numériques."),
("Qu’est-ce que l’ESTC ?", "L’École Supérieure de Technologie de Casablanca est un établissement public relevant de l’Université Hassan II de Casablanca. Elle a été créée en 1986."),
("Où se trouve l’ESTC ?", "L’ESTC se situe Route d’El Jadida, KM 7, Casablanca."),
("Qu’est-ce que le département INED ?", "INED signifie Innovation et Entrepreneuriat Digital. Le département comprend les filières MDO et Banque Finance Assurances (BFA)."),
("Quelles matières étudie-t-on en S1 ?", "En S1 : langues, institutions administratives et politiques (Arabe), économie générale, management des organisations, mathématiques appliquées, comptabilité financière, mathématiques financières, statistiques descriptives et informatique de base."),
("Quelles matières étudie-t-on en S2 ?", "En S2 : langues, compétences informatiques et digitales, système juridique des organisations, droit commercial, comptabilité financière, marketing fondamental, management commercial, introduction à la GRH, droit social, statistique probabiliste et logiciels de gestion."),
("Comment valider un module ?", "En session normale, la moyenne du module doit être égale ou supérieure à 10/20. Si le module comporte deux éléments, la compensation est possible si la note la plus faible est au moins égale à 5/20."),
("Quelle est la règle des absences ?", "La présence aux cours et aux TD est obligatoire. Si les absences non justifiées dépassent 50 % du volume horaire global d’un module, l’étudiant est privé de la session normale pour ce module et orienté vers le rattrapage."),
("Comment fonctionne le rattrapage ?", "En cas de non-validation en session normale, l’étudiant est convoqué au rattrapage pour les éléments non validés, sous réserve d’avoir obtenu au moins 5/20 au module."),
("Le S2 est-il disponible ?", "Selon le livret d’accueil 2026/2027, l’emploi du temps du S2 n’est pas encore publié. Il sera communiqué par le département à la fin du S1."),
("Quels sont les clubs de l’ESTC ?", "Le livret présente Goutte d’Espoir (solidarité), Club Sportif ESTC (football, volleyball, basketball), Echos Art Musicale (musique) et Lens ESTC (photographie et image)."),
("Quels sont les services de l’ESTC ?", "Le livret présente la salle de lecture, le service de scolarité, l’internat sous conditions et la restauration."),
("À quoi sert Aptus Educat ?", "Selon les fonctionnalités activées, Aptus Educat permet de consulter les notes, les emplois du temps, les absences, les informations scolaires et l’autorisation à passer les examens. Les identifiants sont à récupérer auprès de la scolarité."),
("Le stage d’initiation est-il obligatoire ?", "Le livret indique qu’un stage d’observation est à effectuer à la fin de la première année. Les modalités pratiques doivent être confirmées auprès du département."),
("Comment trouver un stage ?", "Préparez un CV professionnel, créez un profil LinkedIn, ciblez des entreprises, personnalisez vos candidatures, préparez les entretiens et développez vos compétences numériques."),
("Quels domaines peut-on explorer après MDO ?", "Le livret cite notamment le marketing digital, la gestion commerciale, les ressources humaines, l’e-commerce, la fiscalité, la transformation digitale, l’entrepreneuriat, la finance et la comptabilité. Ce sont des domaines à explorer, pas des débouchés garantis."),
("Quel est le contact de l’administration ?", "Le numéro indiqué dans le livret est +212 6 14 00 04 20. Pour une information officielle ou actualisée, contactez directement la scolarité."),
("Quel est le site officiel de l’ESTC ?", "https://www.est-uh2c.ac.ma/estc/"),
]

# Petit lexique documentaire pour reconnaître plusieurs formulations.
KNOWLEDGE = [
    (["mdo", "filiere", "filière", "signifie", "management digital"], FAQ[0][1]),
    (["estc", "ecole", "école", "etablissement", "établissement", "universite", "université"], FAQ[1][1]),
    (["adresse", "situe", "située", "localisation", "où se trouve", "route el jadida"], FAQ[2][1]),
    (["ined", "departement", "département", "bfa"], FAQ[3][1]),
    (["s1", "semestre 1", "premier semestre", "matiere s1", "matières s1"], FAQ[4][1]),
    (["s2", "semestre 2", "deuxieme semestre", "deuxième semestre", "matiere s2"], FAQ[5][1]),
    (["valider", "validation", "moyenne", "10/20", "compensation", "note minimale"], FAQ[6][1]),
    (["absence", "absences", "assiduite", "assiduité", "50%", "presence", "présence"], FAQ[7][1]),
    (["rattrapage", "rattrap", "session normale"], FAQ[8][1]),
    (["emploi du temps", "edt", "horaire", "horaires", "planning", "s2 publie", "s2 publié"], FAQ[9][1]),
    (["club", "clubs", "goutte d'espoir", "lens", "sportif", "musicale"], FAQ[10][1]),
    (["service", "scolarite", "scolarité", "internat", "restauration", "salle de lecture"], FAQ[11][1]),
    (["aptus", "educat", "plateforme", "identifiant", "mot de passe"], FAQ[12][1]),
    (["stage", "stages", "observation", "fin de premiere annee", "fin de première année"], FAQ[13][1]),
    (["cv", "linkedin", "candidature", "entretien", "trouver un stage"], FAQ[14][1]),
    (["debouche", "débouché", "metier", "métier", "carriere", "carrière", "avenir", "domaines"], FAQ[15][1]),
    (["telephone", "téléphone", "contact", "numero", "numéro"], FAQ[16][1]),
    (["site officiel", "site web", "website", "lien estc"], FAQ[17][1]),
]

def normalize(text):
    text = text.lower().strip()
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    text = re.sub(r"[^a-z0-9%+ ]", " ", text)
    return re.sub(r"\s+", " ", text)

def answer_question(question):
    q = normalize(question)
    if not q:
        return None
    # Score par mots-clés : plus les mots-clés distincts sont présents,
    # plus la réponse correspond à la question.
    best_answer, best_score = None, 0
    for keywords, answer in KNOWLEDGE:
        score = sum(1 for word in keywords if normalize(word) in q)
        if score > best_score:
            best_score, best_answer = score, answer
    if best_score > 0:
        return best_answer
    # Recherche de question proche dans la FAQ (tolère certaines formulations).
    best_ratio, best_faq = 0, None
    for question_faq, answer in FAQ:
        ratio = SequenceMatcher(None, q, normalize(question_faq)).ratio()
        if ratio > best_ratio:
            best_ratio, best_faq = ratio, answer
    if best_ratio >= 0.48:
        return best_faq
    return ("Je ne trouve pas de réponse suffisamment fiable dans le livret d’accueil intégré. "
            "Pour éviter de vous donner une information incorrecte, veuillez vérifier auprès "
            "du département INED ou du service de scolarité.")

# ---------- SIDEBAR ----------
with st.sidebar:
    st.markdown("## 🎓 MDO SMART GUIDE")
    st.caption("ESTC • INED • Année 2026/2027")
    st.markdown("---")
    page = st.radio(
        "NAVIGATION",
        ["Accueil", "Découvrir l’ESTC & MDO", "Programme pédagogique",
         "Emploi du temps", "Évaluation & assiduité", "Services & vie étudiante",
         "Conseils de réussite", "Stages & avenir", "Quiz", "Assistant MDO"],
        label_visibility="visible"
    )
    st.markdown("---")
    st.caption("Source principale : Livret d’accueil MDO 2026/2027")
    st.caption("Version documentaire sans API payante.")

# ---------- HOME ----------
if page == "Accueil":
    st.markdown("""
    <div class="hero">
      <div style="font-size:.85rem;letter-spacing:2px;font-weight:700;color:#BDEFEA">VOTRE GUIDE UNIVERSITAIRE</div>
      <h1>MDO SMART GUIDE</h1>
      <p>Bienvenue à l’ESTC ! Découvrez votre filière, organisez vos études et trouvez les informations essentielles pour réussir votre première année.</p>
    </div>
    """, unsafe_allow_html=True)
    c1,c2,c3 = st.columns(3)
    for col, num, label in [(c1,"2026/27","Année universitaire"),(c2,"2","Semestres au programme"),(c3,"24/7","Guide consultable en ligne")]:
        with col:
            st.markdown(f'<div class="kpi"><div class="num">{num}</div><div class="lbl">{label}</div></div>', unsafe_allow_html=True)
    st.write("")
    st.subheader("Explorez votre espace étudiant")
    cards = st.columns(2)
    with cards[0]:
        st.markdown('<div class="info-card"><b>📚 Comprendre la formation</b><br>Découvrez l’ESTC, le département INED, la filière MDO et les matières des deux semestres.</div>',unsafe_allow_html=True)
        st.markdown('<div class="info-card"><b>🗓️ Organiser votre semaine</b><br>Consultez le véritable emploi du temps S1 fourni dans le livret.</div>',unsafe_allow_html=True)
        st.markdown('<div class="info-card"><b>📝 Comprendre l’évaluation</b><br>Validation, compensation, rattrapage et suivi des absences.</div>',unsafe_allow_html=True)
    with cards[1]:
        st.markdown('<div class="info-card"><b>🏫 Découvrir la vie étudiante</b><br>Services, plateforme Aptus Educat et clubs de l’ESTC.</div>',unsafe_allow_html=True)
        st.markdown('<div class="info-card"><b>🚀 Préparer son avenir</b><br>Conseils pour le stage d’initiation et domaines professionnels à explorer.</div>',unsafe_allow_html=True)
        st.markdown('<div class="info-card"><b>💬 Poser une question</b><br>Interrogez l’assistant documentaire à partir des informations du livret.</div>',unsafe_allow_html=True)
    st.info("Conseil : les informations administratives et les emplois du temps peuvent évoluer. Vérifiez toujours les annonces officielles de l’ESTC.")

# ---------- DISCOVER ----------
elif page == "Découvrir l’ESTC & MDO":
    st.title("Découvrir l’ESTC et la filière MDO")
    tab1,tab2,tab3 = st.tabs(["L’ESTC","Département INED","Filière MDO"])
    with tab1:
        st.subheader("École Supérieure de Technologie de Casablanca")
        st.write("L’ESTC est un établissement public relevant de l’Université Hassan II de Casablanca. Créée en 1986, elle propose des formations professionnalisantes associant enseignements théoriques, travaux pratiques et projets.")
        st.write("Le parcours DUT dure deux ans. Le livret mentionne également une possibilité d’accès au Bachelor à travers un concours écrit et oral.")
        st.markdown("**Adresse :** Route d’El Jadida, KM 7, Casablanca.")
        st.link_button("Visiter le site officiel de l’ESTC","https://www.est-uh2c.ac.ma/estc/")
    with tab2:
        st.subheader("Innovation et Entrepreneuriat Digital")
        st.write("Le département INED comprend deux filières : Management Digital des Organisations (MDO) et Banque Finance Assurances (BFA).")
        st.write("Il encourage l’innovation, les projets digitaux, le développement des compétences professionnelles et l’adaptation aux évolutions technologiques.")
    with tab3:
        st.subheader("Management Digital des Organisations")
        st.write("La filière associe les principes du management et de la gestion d’entreprise aux technologies numériques.")
        st.markdown("**Domaines abordés :**")
        st.write("- Gestion et administration\n- Marketing et commerce\n- Management des organisations\n- Ressources humaines\n- Outils numériques et bureautiques\n- Transformation digitale\n- Entrepreneuriat et innovation")
        st.markdown("**Objectifs de la formation :** comprendre les entreprises, développer des compétences en gestion, maîtriser des outils numériques, travailler en équipe, communiquer, analyser des situations et se préparer progressivement à l’insertion professionnelle.")

# ---------- PROGRAM ----------
elif page == "Programme pédagogique":
    st.title("Programme pédagogique 2026/2027")
    sem = st.segmented_control("Choisir le semestre",["Semestre 1","Semestre 2"],default="Semestre 1")
    modules = S1 if sem == "Semestre 1" else S2
    for module, subjects in modules.items():
        with st.expander(f"📘 {module}", expanded=False):
            for subject in subjects:
                st.markdown(f"- {subject}")
    st.caption("Les intitulés sont repris du livret d’accueil MDO 2026/2027.")

# ---------- TIMETABLE ----------
elif page == "Emploi du temps":
    st.title("Emploi du temps 2026/2027")
    st.write("Consultez le tableau officiel reproduit dans le livret d’accueil MDO.")
    t1,t2 = st.tabs(["Semestre 1","Semestre 2"])
    with t1:
        img = Path(__file__).parent / "assets" / "emploi_du_temps_S1.png"
        if img.exists():
            st.image(str(img), caption="Emploi du temps S1 — document fourni dans le Livret d’accueil MDO, page 6.", use_container_width=True)
        else:
            st.warning("Le fichier image du tableau S1 est introuvable. Vérifiez que le dossier assets accompagne app.py.")
        st.info("Le tableau est affiché sous forme d’image afin de conserver exactement les jours, horaires, matières, enseignants et salles du document source.")
    with t2:
        st.warning("Selon le livret d’accueil 2026/2027, l’emploi du temps du S2 n’est pas encore disponible ni publié. Il sera communiqué par le département à la fin du S1.")

# ---------- ASSESSMENT ----------
elif page == "Évaluation & assiduité":
    st.title("Comprendre l’évaluation")
    st.subheader("Validation d’un module")
    st.write("Pour valider un module en session normale, la moyenne générale doit être égale ou supérieure à 10/20.")
    st.subheader("Compensation entre deux éléments")
    st.write("Si un module comporte deux éléments, une note élevée peut compenser une note plus faible, à condition que cette dernière soit au moins égale à 5/20.")
    with st.expander("Exemple pédagogique de compensation"):
        st.write("Exemple illustratif : si les deux éléments d’un module ont des notes de 14/20 et 6/20, la compensation peut être possible si la moyenne du module atteint 10/20 et si les règles du module le permettent. Vérifiez toujours les modalités données par l’enseignant.")
    st.subheader("Rattrapage")
    st.write("En cas de non-validation en session normale, l’étudiant est convoqué au rattrapage pour les éléments non validés, sous réserve d’avoir obtenu au moins 5/20 au module.")
    st.subheader("Suivi des absences")
    st.warning("La présence aux cours et aux TD est obligatoire. Si les absences non justifiées dépassent 50 % du volume horaire global d’un module, l’étudiant est automatiquement privé de la session normale pour ce module et orienté vers le rattrapage.")
    st.subheader("Composition de la note finale")
    st.write("Selon les modules et les enseignants, peuvent être pris en compte : les notes des DS, l’assiduité, la présence en cours et la participation en classe.")
    st.caption("Les modalités peuvent varier selon le module et l’enseignant. Le livret ne précise pas de coefficients communs à tous les modules.")

# ---------- CAMPUS ----------
elif page == "Services & vie étudiante":
    st.title("Services et vie étudiante")
    services = {
        "📖 Salle de lecture":"Un espace pour la lecture, le travail personnel, la préparation des exposés et des projets, ainsi que la révision des DS.",
        "🏢 Service de scolarité":"Le service à contacter pour les démarches administratives, les attestations, les questions étudiantes, les stages, les résultats et les procédures.",
        "🛏️ Internat":"Hébergement destiné aux étudiants éligibles venant de villes éloignées. Les conditions, les places disponibles et l’inscription doivent être confirmées auprès des services concernés.",
        "🍽️ Restauration":"Le livret mentionne un espace de restauration pour les étudiants internes et une buvette pour les étudiants externes.",
        "💻 Aptus Educat":"Plateforme numérique utilisée par les étudiants de l’ESTC. Selon les fonctionnalités activées, elle permet de consulter les notes, emplois du temps, absences, informations scolaires et autorisation à passer les examens."
    }
    for title,desc in services.items():
        with st.expander(title):
            st.write(desc)
    st.subheader("Conseils pour utiliser Aptus Educat")
    st.write("1. Récupérez vos identifiants auprès de la scolarité.\n2. Connectez-vous à la plateforme.\n3. Consultez les différentes rubriques.\n4. Vérifiez régulièrement les informations.\n5. Gardez vos identifiants confidentiels.\n6. Déconnectez-vous après utilisation.")
    st.caption("Le livret ne fournit pas d’adresse directe vérifiable pour Aptus Educat : utilisez le lien communiqué par l’établissement.")
    st.subheader("Les clubs à découvrir")
    clubs = {
        "Goutte d’Espoir":"Actions humanitaires et solidarité.",
        "Club Sportif ESTC":"Football, volleyball et basketball.",
        "Echos Art Musicale":"Chant, instruments et composition.",
        "Lens ESTC":"Photographie et image."
    }
    cols = st.columns(2)
    for i,(name,desc) in enumerate(clubs.items()):
        with cols[i%2]:
            st.markdown(f'<div class="info-card"><b>{name}</b><br>{desc}</div>',unsafe_allow_html=True)

# ---------- SUCCESS ----------
elif page == "Conseils de réussite":
    st.title("Conseils pour réussir sa première année")
    tips = [
        ("Organisez votre travail","Préparez un planning hebdomadaire, classez vos cours et évitez les révisions de dernière minute."),
        ("Soyez assidu(e)","Assistez aux cours et aux TD et suivez vos absences."),
        ("Participez","Posez des questions, prenez la parole et échangez avec les enseignants."),
        ("Travaillez en équipe","Communiquez, partagez les responsabilités et respectez les délais des projets."),
        ("Développez vos compétences","Progressez en langues, outils numériques, communication et organisation.")
    ]
    for i,(title,desc) in enumerate(tips,1):
        st.markdown(f'<div class="info-card"><b>{i}. {title}</b><br>{desc}</div>',unsafe_allow_html=True)

# ---------- CAREER ----------
elif page == "Stages & avenir":
    st.title("Stages et avenir professionnel")
    st.subheader("Stage d’initiation")
    st.write("Le livret indique qu’un stage d’observation est à effectuer à la fin de la première année. Il permet de découvrir le fonctionnement d’une organisation et son environnement professionnel.")
    st.subheader("Préparer sa recherche")
    st.write("1. Préparer un CV professionnel.\n2. Créer un profil LinkedIn.\n3. Rechercher des entreprises correspondant à ses intérêts.\n4. Envoyer des candidatures adaptées.\n5. Se préparer aux entretiens.\n6. Développer ses compétences sur les outils numériques de gestion.\n7. Profiter de chaque expérience pour apprendre.")
    st.subheader("Domaines à explorer")
    fields = ["Marketing digital","Gestion commerciale","Ressources humaines","E-commerce","Fiscalité","Transformation digitale","Entrepreneuriat","Finance et comptabilité"]
    st.write(" • ".join(fields))
    st.info("Ces domaines sont des pistes d’exploration citées dans le livret, et non une garantie d’emploi ou de débouché.")

# ---------- QUIZ ----------
elif page == "Quiz":
    st.title("Quiz — Testez vos connaissances")
    quiz = [
        ("Que signifie MDO ?",["Management Digital des Organisations","Marketing et Développement Opérationnel","Management des Données et Outils"],0,"MDO signifie Management Digital des Organisations."),
        ("Quelle est la moyenne minimale pour valider un module en session normale ?",["8/20","10/20","12/20"],1,"Le seuil indiqué dans le livret est 10/20."),
        ("Quel est le seuil minimal de la note la plus faible pour permettre la compensation entre deux éléments ?",["3/20","5/20","8/20"],1,"La note la plus faible doit être au moins égale à 5/20."),
        ("Quel service contacter pour récupérer ses identifiants Aptus ?",["Le club sportif","La scolarité","La bibliothèque"],1,"Le livret conseille de récupérer les identifiants auprès du service de scolarité."),
        ("L’emploi du temps S2 est-il publié dans le livret ?",["Oui","Non"],1,"Le livret précise que l’emploi du temps S2 sera communiqué à la fin du S1.")
    ]
    if "quiz_answers" not in st.session_state:
        st.session_state.quiz_answers = {}
    for i,(question,options,correct,explanation) in enumerate(quiz):
        st.markdown(f"**{i+1}. {question}**")
        st.session_state.quiz_answers[i] = st.radio("Votre réponse",options,key=f"quiz_{i}",label_visibility="collapsed")
        st.divider()
    if st.button("Corriger mon quiz"):
        score = 0
        for i,(_,options,correct,_) in enumerate(quiz):
            if st.session_state.quiz_answers.get(i) == options[correct]:
                score += 1
        st.success(f"Votre score : {score}/{len(quiz)}")
        for i,(question,options,correct,explanation) in enumerate(quiz):
            if st.session_state.quiz_answers.get(i) == options[correct]:
                st.write(f"✅ Question {i+1} : {explanation}")
            else:
                st.write(f"❌ Question {i+1} : Réponse correcte — {options[correct]}. {explanation}")

# ---------- ASSISTANT ----------
elif page == "Assistant MDO":
    st.title("Assistant MDO 💬")
    st.write("Posez votre question librement. L’assistant recherche une réponse dans les informations du livret d’accueil.")
    st.caption("Assistant documentaire gratuit • Sans API • Il ne remplace pas les informations officielles du département.")
    lang = st.radio("Langue de réponse",["Français","Darija"],horizontal=True)
    suggested = st.selectbox("Questions fréquentes",["Choisir une question"]+[q for q,_ in FAQ])
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    for item in st.session_state.chat_history:
        with st.chat_message(item["role"]):
            st.markdown(item["content"])
    if suggested != "Choisir une question":
        if st.button("Afficher la réponse à cette question"):
            ans = dict(FAQ)[suggested]
            st.session_state.chat_history.append({"role":"user","content":suggested})
            st.session_state.chat_history.append({"role":"assistant","content":ans})
            st.rerun()
    question = st.chat_input("Écrivez votre question ici…")
    if question:
        ans = answer_question(question)
        if lang == "Darija":
            # Keep official terms and facts intact; simple Darija framing.
            if "Je ne trouve pas" in ans:
                ans = "سمح ليا، ما لقيتش جواب موثوق على هاد السؤال فالدليل. باش ما نعطيكش معلومة غالطة، تواصل مع قسم INED أو مصلحة الشؤون الطلابية."
            else:
                ans = "حسب دليل استقبال طلبة MDO 2026/2027:\n\n" + ans + "\n\nإلى كانت المعلومة إدارية أو قابلة للتغيير، تأكد منها عند المصلحة المختصة."
        st.session_state.chat_history.append({"role":"user","content":question})
        st.session_state.chat_history.append({"role":"assistant","content":ans})
        st.rerun()
    if st.button("Effacer la conversation"):
        st.session_state.chat_history = []
        st.rerun()

# ---------- FOOTER ----------
st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#777187;font-size:.82rem'>"
    "MDO SMART GUIDE • ESTC – INED • Année universitaire 2026/2027<br>"
    "Contenu basé sur le Livret d’accueil MDO fourni par l’équipe du projet."
    "</div>", unsafe_allow_html=True
)

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

# ===== KLARES, FUNKTIONALES DESIGN =====
st.set_page_config(
    layout="wide", 
    page_title="🚀 Produktivitäts-Tracker",
    page_icon="📊"
)

# Modernes, minimales CSS
st.markdown("""
<style>
:root {
    --primary: #4e73df;
    --secondary: #2e59a9;
    --accent: #1cc88a;
    --warning: #f6c23e;
    --danger: #e74a3b;
}
* {
    font-family: 'Segoe UI', 'SF Pro Display', -apple-system, sans-serif;
}
.stApp {
    max-width: 1200px;
    margin: 0 auto;
    padding: 1rem;
}
.stProgress > div > div {
    background-color: var(--primary) !important;
}
.stMetric {
    border-left: 4px solid var(--primary);
    padding-left: 1rem;
}
.card {
    background: white;
    border-radius: 10px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    border: 1px solid #e3e6f0;
}
h1, h2, h3, h4 {
    color: var(--secondary);
    font-weight: 700;
}
.progress-bar {
    height: 20px;
    background: #eaecf4;
    border-radius: 10px;
    margin: 10px 0;
    overflow: hidden;
}
.progress-fill {
    height: 100%;
    background: var(--accent);
    border-radius: 10px;
    transition: width 0.5s ease;
}
.due-soon {
    background-color: #fff8e1 !important;
    border-left: 4px solid var(--warning) !important;
}
.due-urgent {
    background-color: #ffebee !important;
    border-left: 4px solid var(--danger) !important;
}
</style>
""", unsafe_allow_html=True)

# ===== DATENSTRUKTUREN =====
if 'tasks' not in st.session_state:
    st.session_state.tasks = pd.DataFrame(columns=[
        'Task', 'Kategorie', 'Priorität', 'Startdatum', 'Fälligkeitsdatum', 
        'Status', 'Fortschritt', 'Aufgewendete Zeit (h)'
    ])
    
if 'time_log' not in st.session_state:
    st.session_state.time_log = pd.DataFrame(columns=[
        'Datum', 'Task', 'Dauer (h)', 'Produktivität'
    ])

# ===== HAUPTLAYOUT =====
st.title("🚀 Produktivitäts-Tracker")
st.markdown("---")

# ===== NEUE TASK ERFASSUNG =====
with st.expander("➕ Neuen Task hinzufügen", expanded=True):
    with st.form("task_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            task = st.text_input("Task-Beschreibung*", placeholder="z.B. Projektbericht erstellen")
            kategorie = st.selectbox("Kategorie*", ["Arbeit", "Persönlich", "Lernen", "Fitness", "Sonstiges"])
            prioritaet = st.select_slider("Priorität*", options=["Niedrig", "Mittel", "Hoch", "Kritisch"], value="Mittel")
        
        with col2:
            start = st.date_input("Startdatum*", datetime.now())
            frist = st.date_input("Fälligkeitsdatum*", datetime.now() + timedelta(days=7))
            status = st.selectbox("Status*", ["Geplant", "In Bearbeitung", "Im Review", "Abgeschlossen"], index=0)
            fortschritt = st.slider("Fortschritt (%)", 0, 100, 0)
        
        if st.form_submit_button("Task speichern"):
            if task:
                neuer_task = pd.DataFrame([{
                    'Task': task,
                    'Kategorie': kategorie,
                    'Priorität': prioritaet,
                    'Startdatum': start,
                    'Fälligkeitsdatum': frist,
                    'Status': status,
                    'Fortschritt': fortschritt,
                    'Aufgewendete Zeit (h)': 0
                }])
                
                st.session_state.tasks = pd.concat(
                    [st.session_state.tasks, neuer_task], 
                    ignore_index=True
                )
                st.success("Task erfolgreich hinzugefügt!")
            else:
                st.error("Bitte eine Task-Beschreibung eingeben")

# ===== ZEITERFASSUNG =====
with st.expander("⏱️ Zeiterfassung", expanded=True):
    if not st.session_state.tasks.empty:
        aktive_tasks = st.session_state.tasks[st.session_state.tasks['Status'].isin(["Geplant", "In Bearbeitung", "Im Review"])]
        
        if not aktive_tasks.empty:
            with st.form("time_form"):
                col1, col2, col3 = st.columns([3, 2, 2])
                
                with col1:
                    selected_task = st.selectbox("Task auswählen", aktive_tasks['Task'])
                
                with col2:
                    dauer = st.number_input("Dauer (Stunden)*", min_value=0.25, max_value=12.0, value=1.0, step=0.25)
                
                with col3:
                    produktivitaet = st.slider("Produktivität*", 1, 10, 8, help="1 = sehr unproduktiv, 10 = sehr produktiv")
                
                if st.form_submit_button("Zeiteintrag speichern"):
                    neuer_eintrag = pd.DataFrame([{
                        'Datum': datetime.now().date(),
                        'Task': selected_task,
                        'Dauer (h)': dauer,
                        'Produktivität': produktivitaet
                    }])
                    
                    # Zeit zum Task hinzufügen
                    idx = st.session_state.tasks.index[st.session_state.tasks['Task'] == selected_task].tolist()
                    if idx:
                        st.session_state.tasks.at[idx[0], 'Aufgewendete Zeit (h)'] += dauer
                    
                    st.session_state.time_log = pd.concat(
                        [st.session_state.time_log, neuer_eintrag], 
                        ignore_index=True
                    )
                    st.success(f"{dauer} Stunden für '{selected_task}' erfasst!")
        else:
            st.info("Keine aktiven Tasks verfügbar")
    else:
        st.info("Erfasse zuerst Tasks um Zeit zu erfassen")

# ===== FORTSCHRITTS-DASHBOARD =====
st.header("📊 Produktivitäts-Dashboard")

if not st.session_state.tasks.empty:
    # KPI-Karten
    col1, col2, col3, col4 = st.columns(4)
    
    gesamt_tasks = len(st.session_state.tasks)
    abgeschlossen = len(st.session_state.tasks[st.session_state.tasks['Status'] == "Abgeschlossen"])
    in_progress = len(st.session_state.tasks[st.session_state.tasks['Status'] == "In Bearbeitung"])
    gesamt_zeit = st.session_state.tasks['Aufgewendete Zeit (h)'].sum()
    
    col1.metric("📋 Gesamt-Tasks", gesamt_tasks)
    col2.metric("✅ Abgeschlossen", abgeschlossen, f"{abgeschlossen/gesamt_tasks*100:.1f}%")
    col3.metric("🚧 In Arbeit", in_progress)
    col4.metric("⏱️ Gesamtzeit", f"{gesamt_zeit}h")
    
    # Fortschrittsbalken für alle Tasks
    st.subheader("Task-Fortschritt")
    for _, row in st.session_state.tasks.iterrows():
        days_left = (row['Fälligkeitsdatum'] - datetime.now().date()).days
        status_class = ""
        
        if days_left < 0:
            status_class = "due-urgent"
        elif days_left <= 3:
            status_class = "due-soon"
        
        with st.container():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{row['Task']}**  \n*{row['Kategorie']} | Priorität: {row['Priorität']}*")
                
                # Fortschrittsbalken mit CSS
                st.markdown(f"""
                <div class="progress-bar">
                    <div class="progress-fill" style="width:{row['Fortschritt']}%"></div>
                </div>
                <div style="display:flex; justify-content:space-between">
                    <span>Fortschritt: {row['Fortschritt']}%</span>
                    <span>Verbrauchte Zeit: {row['Aufgewendete Zeit (h)']}h</span>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.caption(f"Fällig: {row['Fälligkeitsdatum'].strftime('%d.%m.%Y')}")
                st.caption(f"Status: **{row['Status']}**")
                if days_left < 0:
                    st.error(f"Überfällig: {abs(days_left)} Tage")
                elif days_left <= 3:
                    st.warning(f"Noch {days_left} Tage")
                else:
                    st.info(f"Noch {days_left} Tage")
    
    # Diagramme
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Task-Verteilung nach Kategorie")
        if not st.session_state.tasks.empty:
            cat_dist = st.session_state.tasks['Kategorie'].value_counts().reset_index()
            fig1 = px.pie(
                cat_dist, 
                names='Kategorie', 
                values='count',
                hole=0.4,
                color_discrete_sequence=px.colors.sequential.Blues_r
            )
            st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        st.subheader("Status-Verteilung")
        if not st.session_state.tasks.empty:
            status_dist = st.session_state.tasks['Status'].value_counts().reset_index()
            fig2 = px.bar(
                status_dist, 
                x='Status', 
                y='count',
                color='Status',
                color_discrete_sequence=['#4e73df', '#1cc88a', '#f6c23e', '#858796']
            )
            st.plotly_chart(fig2, use_container_width=True)
    
    # Zeitverbrauchsanalyse
    st.subheader("⏱️ Zeitinvestition nach Kategorie")
    if not st.session_state.tasks.empty:
        zeit_pro_kategorie = st.session_state.tasks.groupby('Kategorie')['Aufgewendete Zeit (h)'].sum().reset_index()
        fig3 = px.bar(
            zeit_pro_kategorie, 
            x='Kategorie', 
            y='Aufgewendete Zeit (h)',
            color='Kategorie',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        st.plotly_chart(fig3, use_container_width=True)
    
    # Erinnerungen / Fällige Tasks
    st.subheader("🔔 Anstehende Fristen")
    heute = datetime.now().date()
    fällige_tasks = st.session_state.tasks[
        (st.session_state.tasks['Status'] != "Abgeschlossen") & 
        (st.session_state.tasks['Fälligkeitsdatum'] <= heute + timedelta(days=7))
    ]
    
    if not fällige_tasks.empty:
        # Priorität sortieren
        priorität_order = {"Kritisch": 0, "Hoch": 1, "Mittel": 2, "Niedrig": 3}
        fällige_tasks['Priorität_Order'] = fällige_tasks['Priorität'].map(priorität_order)
        fällige_tasks = fällige_tasks.sort_values(['Fälligkeitsdatum', 'Priorität_Order'])
        
        st.dataframe(
            fällige_tasks[['Task', 'Kategorie', 'Priorität', 'Fälligkeitsdatum', 'Status']],
            height=300,
            use_container_width=True,
            column_config={
                "Fälligkeitsdatum": st.column_config.DateColumn(
                    format="DD.MM.YYYY",
                    help="Fälligkeitsdatum"
                )
            }
        )
    else:
        st.success("Keine anstehenden Fristen in den nächsten 7 Tagen!")
    
    # Produktivitätsverlauf
    st.subheader("📈 Produktivitätsverlauf")
    if not st.session_state.time_log.empty:
        time_log = st.session_state.time_log.copy()
        time_log['Datum'] = pd.to_datetime(time_log['Datum'])
        
        # Wochennummer und Jahr hinzufügen
        time_log['Kalenderwoche'] = time_log['Datum'].dt.isocalendar().week
        time_log['Jahr'] = time_log['Datum'].dt.year
        time_log['KW/Jahr'] = time_log['Kalenderwoche'].astype(str) + '/' + time_log['Jahr'].astype(str)
        
        produktivitaet_woche = time_log.groupby('KW/Jahr')['Produktivität'].mean().reset_index()
        
        fig4 = px.line(
            produktivitaet_woche, 
            x='KW/Jahr', 
            y='Produktivität',
            markers=True,
            title='Durchschnittliche Produktivität pro Woche',
            range_y=[1, 10]
        )
        fig4.update_traces(line=dict(width=3), marker=dict(size=8))
        fig4.update_layout(yaxis_title="Produktivität (1-10)")
        st.plotly_chart(fig4, use_container_width=True)
    
else:
    st.info("Füge deine ersten Tasks hinzu, um deine Produktivität zu tracken")

# ===== DATENVERWALTUNG =====
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    if st.button("🔄 Alle Daten zurücksetzen", type="primary"):
        st.session_state.tasks = pd.DataFrame(columns=st.session_state.tasks.columns)
        st.session_state.time_log = pd.DataFrame(columns=st.session_state.time_log.columns)
        st.experimental_rerun()

with col2:
    if not st.session_state.tasks.empty:
        csv = st.session_state.tasks.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="💾 Tasks als CSV exportieren",
            data=csv,
            file_name="produktivitaet_tasks.csv",
            mime="text/csv"
        )

# ===== TIPPS =====
with st.expander("💡 Produktivitäts-Tipps", expanded=True):
    st.markdown("""
    **Effizienzsteigerung:**
    - 🍅 Nutze die Pomodoro-Technik (25 Min. Arbeit + 5 Min. Pause)
    - 📵 Eliminiere Ablenkungen während Arbeitsphasen
    - 🌟 Beginne mit der wichtigsten Aufgabe des Tages (Eat the Frog)
    
    **Task-Management:**
    - 🔼 Priorisiere nach der Eisenhower-Matrix (Dringend/Wichtig)
    - 📆 Plane realistische Fristen mit Pufferzeit
    - ✂️ Teile große Tasks in kleinere Unteraufgaben
    
    **Gesundes Arbeiten:**
    - 💧 Trinke ausreichend Wasser (mind. 2 Liter/Tag)
    - 🚶‍♂️ Mache alle 60 Minuten 5 Minuten Bewegung
    - 😌 Praktiziere tägliche Reflexion (Was lief gut? Was kann besser?)
    """)

st.caption("© Produktivitäts-Tracker v1.0 | Daten werden lokal in deinem Browser gespeichert")

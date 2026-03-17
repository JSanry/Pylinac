import streamlit as st
import json
import os
from datetime import datetime, date

DATA_FILE = "tasks.json"

# --- AUTH CONFIG ---
USERS = {
    "admin": "1234",
    "user": "abcd"
}

# --- LOAD/SAVE ---
def load_tasks():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {k: [] for k in ["mercado","casa","limpeza","contas","geral"]}


def save_tasks(tasks):
    with open(DATA_FILE, "w") as f:
        json.dump(tasks, f, indent=2, default=str)


# --- AUTH ---
def login():
    st.title("🔐 Login")
    user = st.text_input("Usuário")
    password = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if user in USERS and USERS[user] == password:
            st.session_state.authenticated = True
            st.session_state.user = user
            st.rerun()
        else:
            st.error("Credenciais inválidas")


if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    login()
    st.stop()

# --- INIT ---
if "tasks" not in st.session_state:
    st.session_state.tasks = load_tasks()

st.set_page_config(page_title="Gestor de Afazeres", layout="wide")

st.title("📊 Gestor de Afazeres")

# --- HELPERS ---
def prioridade_cor(p):
    return {"Alta":"#ff6b6b","Média":"#f7b267","Baixa":"#6bcB77"}[p]


def status_cor(s):
    return {
        "Disponível": "#4dabf7",
        "Em andamento": "#ffd43b",
        "Concluído": "#51cf66"
    }[s]


def vencimento_cor(due):
    if not due:
        return "#999"
    delta = (due - date.today()).days
    if delta <= 1:
        return "#ff4d4d"
    elif delta <= 3:
        return "#ffa94d"
    return "#6bcB77"


listas = {
    "mercado": "🛒 Mercado",
    "casa": "🏠 Casa",
    "limpeza": "🧹 Limpeza",
    "contas": "💰 Contas",
    "geral": "📌 Geral"
}

aba = st.sidebar.selectbox("Lista", list(listas.keys()), format_func=lambda x: listas[x])

# --- FILTERS ---
st.sidebar.subheader("Filtros")
f_prioridade = st.sidebar.multiselect("Prioridade", ["Alta","Média","Baixa"])
f_status = st.sidebar.multiselect("Status", ["Disponível","Em andamento","Concluído"])
f_vencimento = st.sidebar.checkbox("Apenas próximas (≤3 dias)")
ordenar = st.sidebar.checkbox("Ordenar por urgência")

st.header(listas[aba])

# --- ADD ---
with st.expander("➕ Nova tarefa"):
    nova = st.text_input("Descrição")
    prioridade = st.selectbox("Prioridade", ["Baixa","Média","Alta"])
    status = st.selectbox("Status", ["Disponível","Em andamento","Concluído"])
    vencimento = st.date_input("Vencimento", value=None)

    if st.button("Adicionar") and nova:
        st.session_state.tasks[aba].append({
            "task": nova,
            "done": status=="Concluído",
            "priority": prioridade,
            "status": status,
            "due": str(vencimento) if vencimento else None
        })
        save_tasks(st.session_state.tasks)
        st.rerun()

# --- FILTER LOGIC ---
def apply_filters(tasks):
    result = []
    for t in tasks:
        due = datetime.strptime(t["due"], "%Y-%m-%d").date() if t["due"] else None

        if f_prioridade and t["priority"] not in f_prioridade:
            continue
        if f_status and t["status"] not in f_status:
            continue
        if f_vencimento and due:
            if (due - date.today()).days > 3:
                continue

        result.append((t, due))

    if ordenar:
        result.sort(key=lambda x: (x[1] is None, x[1]))

    return result

filtered = apply_filters(st.session_state.tasks[aba])

# --- DISPLAY ---
for i, (t, due_date) in enumerate(filtered):
    col1, col2, col3, col4, col5 = st.columns([0.05,0.4,0.15,0.15,0.25])

    with col1:
        done = st.checkbox("", value=t["done"], key=f"done_{aba}_{i}")

    with col2:
        style = "text-decoration: line-through;" if done else ""
        st.markdown(f"<div style='{style}'>{t['task']}</div>", unsafe_allow_html=True)

    with col3:
        st.markdown(f"<span style='color:{prioridade_cor(t['priority'])}'>{t['priority']}</span>", unsafe_allow_html=True)

    with col4:
        st.markdown(f"<span style='color:{status_cor(t['status'])}'>{t['status']}</span>", unsafe_allow_html=True)

    with col5:
        if due_date:
            st.markdown(f"<span style='color:{vencimento_cor(due_date)}'>{due_date}</span>", unsafe_allow_html=True)
        if st.button("❌", key=f"del_{aba}_{i}"):
            st.session_state.tasks[aba].remove(t)
            save_tasks(st.session_state.tasks)
            st.rerun()

    t["done"] = done

# --- CLEAN ---
if st.button("🧹 Limpar concluídas"):
    st.session_state.tasks[aba] = [t for t in st.session_state.tasks[aba] if not t["done"]]
    save_tasks(st.session_state.tasks)
    st.rerun()

# --- LOGOUT ---
if st.sidebar.button("Sair"):
    st.session_state.authenticated = False
    st.rerun()


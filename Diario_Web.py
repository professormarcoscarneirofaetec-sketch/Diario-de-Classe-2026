# Célula 1: Setup, Lógica e Funções de BD (Final)

!pip install pandas
import sqlite3
import pandas as pd
import os
from datetime import date
from ipywidgets import VBox, Dropdown, FloatText, Button, Output
import ipywidgets as widgets # Importa o alias 'widgets' para a interface
from IPython.display import display, clear_output, Markdown
import numpy as np 

print("--- Setup Inicial Completo e Bibliotecas Importadas ---")

# =========================================================================
# CONSTANTES E DADOS DE EXEMPLO
# =========================================================================
CORTE_FREQUENCIA = 75
NOTA_APROVACAO_DIRETA = 7.0
NOTA_MINIMA_P3 = 4.0
NOTA_MINIMA_FINAL = 5.0
DB_NAME = 'diario_de_classe.db'
diario_de_classe = {
    "Alice": {
        "Português Instrumental": {
            "presencas": [{"data": "2025-09-01", "conteudo": "Revisão Gramatical", "status": 1}, {"data": "2025-09-08", "conteudo": "Análise de Texto", "status": 1}],
            "avaliacoes": {"P1": 9.0, "P2": 9.0, "P3": None}
        },
        "Inglês Instrumental": {
            "presencas": [{"data": "2025-09-02", "conteudo": "Skimming", "status": 1}, {"data": "2025-09-09", "conteudo": "Scanning", "status": 1}],
            "avaliacoes": {"P1": 8.0, "P2": 7.0, "P3": None}
        }
    },
    "Bruno": {
        "Português Instrumental": {
            "presencas": [{"data": "2025-09-01", "conteudo": "Revisão Gramatical", "status": 1}, {"data": "2025-09-08", "conteudo": "Análise de Texto", "status": 0}],
            "avaliacoes": {"P1": 6.0, "P2": 6.0, "P3": 8.0}
        },
        "Inglês Instrumental": {
            "presencas": [{"data": "2025-09-02", "conteudo": "Skimming", "status": 0}, {"data": "2025-09-09", "conteudo": "Scanning", "status": 1}],
            "avaliacoes": {"P1": 5.0, "P2": 4.0, "P3": 6.0}
        }
    },
    "Carol": {
        "Português Instrumental": {
            "presencas": [{"data": "2025-09-01", "conteudo": "Revisão Gramatical", "status": 1}, {"data": "2025-09-08", "conteudo": "Análise de Texto", "status": 1}],
            "avaliacoes": {"P1": 5.0, "P2": 5.0, "P3": None}
        },
        "Inglês Instrumental": {
            "presencas": [{"data": "2025-09-02", "conteudo": "Skimming", "status": 0}, {"data": "2025-09-09", "conteudo": "Scanning", "status": 0}],
            "avaliacoes": {"P1": 10.0, "P2": 10.0, "P3": None}
        }
    },
}

# =========================================================================
# FUNÇÕES PRINCIPAIS DE LÓGICA E BD
# =========================================================================
def get_nota_valida(nota):
    """Garante que None ou np.nan sejam tratados como 0.0 para cálculo parcial, mas mantém o None para a lógica de P3."""
    if nota is None:
        return 0.0
    try:
        if np.isnan(nota):
            return 0.0
    except:
        pass # Ignora se não for um float (ex: se for um int ou string)
    return float(nota)

def calcular_media_final(avaliacoes):
    p1_val = avaliacoes.get("P1")
    p2_val = avaliacoes.get("P2")
    p3_val = avaliacoes.get("P3")

    # Notas válidas (0.0 se for None/nan) para o cálculo parcial
    p1 = get_nota_valida(p1_val)
    p2 = get_nota_valida(p2_val)
    
    p3 = p3_val # Mantém o valor original (pode ser None) para a lógica de situação

    media_parcial = (p1 + p2) / 2
    nota_final = media_parcial
    situacao_nota = ""
    
    # Resto da lógica...
    if media_parcial >= NOTA_APROVACAO_DIRETA:
        situacao_nota = "APROVADO POR MÉDIA"
    elif media_parcial >= NOTA_MINIMA_P3:
        # AQUI usamos p3_val direto para ver se a nota foi lançada
        if p3_val is None:
            situacao_nota = "PENDENTE (AGUARDANDO P3)"
        else:
            p3_calc = get_nota_valida(p3_val) # Pega o valor 0.0 se for NaN/None
            media_final_com_p3 = (media_parcial + p3_calc) / 2
            nota_final = media_final_com_p3
            if nota_final >= NOTA_MINIMA_FINAL:
                situacao_nota = "APROVADO APÓS P3"
            else:
                situacao_nota = "REPROVADO POR NOTA"
    else: 
        situacao_nota = "REPROVADO DIRETO"
        
    return nota_final, situacao_nota, media_parcial
def lancar_aula_e_frequencia(id_disciplina, data_aula, conteudo):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    id_turma_padrao = 1
    try:
        cursor.execute("""INSERT INTO Aulas (id_turma, id_disciplina, data_aula, conteudo_lecionado) VALUES (?, ?, ?, ?)""", (id_turma_padrao, id_disciplina, data_aula, conteudo))
        conn.commit()
        id_aula = cursor.lastrowid
        cursor.execute("SELECT id_aluno FROM Alunos")
        alunos_ids = [row[0] for row in cursor.fetchall()]
        registros_frequencia = [(id_aula, id_aluno, 1) for id_aluno in alunos_ids]
        cursor.executemany("""INSERT INTO Frequencia (id_aula, id_aluno, presente) VALUES (?, ?, ?)""", registros_frequencia)
        conn.commit()
        print(f"✅ Aula de {conteudo} em {data_aula} lançada (ID: {id_aula}). Todos marcados como Presentes.")
    except Exception as e:
        print(f"❌ Erro ao lançar aula: {e}")
    finally:
        conn.close()

def inserir_nota_no_db(id_aluno, id_disciplina, tipo_avaliacao, valor_nota):
    if valor_nota is None or valor_nota < 0 or valor_nota > 10.0:
        print("⚠️ Erro: Insira um valor de nota válido (0.0 a 10.0).")
        return
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("""REPLACE INTO Notas (id_aluno, id_disciplina, tipo_avaliacao, valor_nota) VALUES (?, ?, ?, ?)""", (id_aluno, id_disciplina, tipo_avaliacao, valor_nota))
        conn.commit()
        print(f"✅ Nota {tipo_avaliacao} ({valor_nota:.1f}) inserida/atualizada para o Aluno {id_aluno} na Disciplina {id_disciplina}.")
    except Exception as e:
        print(f"❌ Erro ao inserir nota: {e}")
    finally: conn.close()

def carregar_ids():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    alunos_db = {nome: id_a for id_a, nome in cursor.execute("SELECT id_aluno, nome FROM Alunos").fetchall()}
    disciplinas_db = {nome: id_d for id_d, nome in cursor.execute("SELECT id_disciplina, nome_disciplina FROM Disciplinas").fetchall()}
    conn.close()
    return alunos_db, disciplinas_db
    
def obter_frequencia_por_aula(id_disciplina, data_aula):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    id_turma_padrao = 1
    
    cursor.execute("""
        SELECT id_aula FROM Aulas WHERE id_turma = ? AND id_disciplina = ? AND data_aula = ?
    """, (id_turma_padrao, id_disciplina, data_aula))
    result = cursor.fetchone()
    
    if not result:
        conn.close()
        return None, "❌ Aula não encontrada para essa data/disciplina."
        
    id_aula = result[0]
    
    df = pd.read_sql_query(f"""
        SELECT 
            A.nome AS Aluno, 
            F.id_frequencia,
            F.presente 
        FROM Frequencia F
        JOIN Alunos A ON F.id_aluno = A.id_aluno
        WHERE F.id_aula = {id_aula}
        ORDER BY A.nome;
    """, conn)
    conn.close()
    
    df['Status Atual'] = df['presente'].apply(lambda x: 'PRESENTE ✅' if x == 1 else 'FALTA 🚫')
    df['Opção'] = df['id_frequencia'].astype(str) + ' - ' + df['Aluno']
    
    return df, id_aula
    
def atualizar_status_frequencia(id_frequencia, novo_status):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE Frequencia SET presente = ? WHERE id_frequencia = ?
        """, (novo_status, id_frequencia))
        conn.commit()
        return f"✅ Status de Presença Atualizado! (ID Frequência: {id_frequencia})"
    except Exception as e:
        return f"❌ Erro ao atualizar frequência: {e}"
    finally:
        conn.close()

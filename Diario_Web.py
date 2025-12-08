import streamlit as st
import sqlite3
import pandas as pd
import numpy as np
from datetime import date

CORTE_FREQUENCIA = 75
NOTA_APROVACAO_DIRETA = 7_0
NOTA_MINIMA_P3 = 4_0
NOTA_MINIMA_FINAL = 5_0
DB_NAME = 'diario_de_classe_db' # O DB será criado no mesmo diretório

# Dados de exemplo usados APENAS para popular as tabelas Alunos e Disciplinas
diario_de_classe = {
    "Alice": {}, 
    "Bruno": {},
    "Carol": {},
}

@st_cache_resource
def criar_e_popular_sqlite():
    conn = sqlite3_connect(DB_NAME)
    cursor = conn_cursor()

    cursor_execute("DROP TABLE IF EXISTS Frequencia")
    cursor_execute("DROP TABLE IF EXISTS Notas")
    cursor_execute("DROP TABLE IF EXISTS Aulas")
    cursor_execute("DROP TABLE IF EXISTS Alunos")
    cursor_execute("DROP TABLE IF EXISTS Disciplinas")
    cursor_execute("DROP TABLE IF EXISTS Turmas")
    conn_commit()
    
    cursor_execute('''CREATE TABLE Alunos (id_aluno INTEGER PRIMARY KEY, nome TEXT NOT NULL, matricula TEXT UNIQUE NOT NULL);''')
    cursor_execute('''CREATE TABLE Disciplinas (id_disciplina INTEGER PRIMARY KEY, nome_disciplina TEXT UNIQUE NOT NULL);''')
    cursor_execute('''CREATE TABLE Turmas (id_turma INTEGER PRIMARY KEY, nome_turma TEXT NOT NULL, ano_letivo INTEGER NOT NULL);''')
    cursor_execute('''CREATE TABLE Aulas (id_aula INTEGER PRIMARY KEY, id_turma INTEGER, id_disciplina INTEGER, data_aula DATE NOT NULL, conteudo_lecionado TEXT, FOREIGN KEY (id_turma) REFERENCES Turmas(id_turma), FOREIGN KEY (id_disciplina) REFERENCES Disciplinas(id_disciplina));''')
    cursor_execute('''CREATE TABLE Notas (id_nota INTEGER PRIMARY KEY, id_aluno INTEGER, id_disciplina INTEGER, tipo_avaliacao TEXT NOT NULL, valor_nota REAL NOT NULL, UNIQUE(id_aluno, id_disciplina, tipo_avaliacao), FOREIGN KEY (id_aluno) REFERENCES Alunos(id_aluno), FOREIGN KEY (id_disciplina) REFERENCES Disciplinas(id_disciplina));''')
    cursor_execute('''CREATE TABLE Frequencia (id_frequencia INTEGER PRIMARY KEY, id_aula INTEGER, id_aluno INTEGER, presente BOOLEAN NOT NULL, UNIQUE(id_aula, id_aluno), FOREIGN KEY (id_aula) REFERENCES Aulas(id_aula), FOREIGN KEY (id_aluno) REFERENCES Alunos(id_aluno));''')
    conn_commit()

    aluno_map = {}; disciplina_map = {}; id_turma_padrao = 1
    
    cursor_execute("REPLACE INTO Turmas (id_turma, nome_turma, ano_letivo) VALUES (?, ?, ?)", (id_turma_padrao, "Exemplo 2025/1", 2025))
    
    disciplinas_list = ["Português Instrumental", "Inglês Instrumental"]
    for i, disc in enumerate(disciplinas_list): 
        cursor_execute("REPLACE INTO Disciplinas (id_disciplina, nome_disciplina) VALUES (?, ?)", (i+1, disc))
    cursor_execute("SELECT id_disciplina, nome_disciplina FROM Disciplinas")
    for id_disc, nome_disc in cursor_fetchall(): 
        disciplina_map[nome_disc] = id_disc
    
    alunos_list = list(diario_de_classe_keys())
    for i, aluno in enumerate(alunos_list): 
        cursor_execute("REPLACE INTO Alunos (id_aluno, nome, matricula) VALUES (?, ?, ?)", (i+1, aluno, f"MAT{2025000 + i + 1}"))
    cursor_execute("SELECT id_aluno, nome FROM Alunos")
    for id_aluno, nome_aluno in cursor_fetchall(): 
        aluno_map[nome_aluno] = id_aluno

    conn_commit()
    conn_close()

    return aluno_map, disciplina_map


    def calcular_media_final(avaliacoes):
    p1_val = avaliacoes_get("P1"); p2_val = avaliacoes_get("P2"); p3_val = avaliacoes_get("P3")
    
    p1 = float(p1_val) if pd_notna(p1_val) and p1_val is not None else 0_0
    p2 = float(p2_val) if pd_notna(p2_val) and p2_val is not None else 0_0
    
    p3 = None
    if p3_val is not None and pd_notna(p3_val): p3 = float(p3_val)
    
    media_parcial = (p1 + p2) / 2
    nota_final = media_parcial
    situacao_nota = ""
    
    if media_parcial >= NOTA_APROVACAO_DIRETA:
        situacao_nota = "APROVADO POR MÉDIA"
    elif media_parcial >= NOTA_MINIMA_P3:
        if p3 is None: situacao_nota = "PENDENTE (AGUARDANDO P3)"
        else:
            media_final_com_p3 = (media_parcial + p3) / 2
            nota_final = media_final_com_p3
            if nota_final >= NOTA_MINIMA_FINAL: situacao_nota = "APROVADO APÓS P3"
            else: situacao_nota = "REPROVADO POR NOTA"
    else: situacao_nota = "REPROVADO DIRETO"
    
    return nota_final, situacao_nota, media_parcial

def lancar_aula_e_frequencia(id_disciplina, data_aula, conteudo):
    conn = sqlite3_connect(DB_NAME)
    cursor = conn_cursor()
    id_turma_padrao = 1
    try:
        cursor_execute("""INSERT INTO Aulas (id_turma, id_disciplina, data_aula, conteudo_lecionado) VALUES (?, ?, ?, ?)""", (id_turma_padrao, id_disciplina, data_aula, conteudo))
        conn_commit()
        id_aula = cursor_lastrowid

        cursor_execute("SELECT id_aluno FROM Alunos")
        alunos_ids = [row[0] for row in cursor_fetchall()]
        
        if not alunos_ids:
            st_warning("⚠️ Alunos não encontrados no DB_ Por favor, recarregue a página_")
            return

        registros_frequencia = [(id_aula, id_aluno, 1) for id_aluno in alunos_ids]
        cursor_executemany("""INSERT INTO Frequencia (id_aula, id_aluno, presente) VALUES (?, ?, ?)""", registros_frequencia)
        conn_commit()
        st_success(f"✅ Aula de {conteudo} em {data_aula} lançada (ID: {id_aula})_ Todos marcados como Presentes_")
    except Exception as e:
        st_error(f"❌ Erro ao lançar aula: {e}")
    finally:
        conn_close()

def inserir_nota_no_db(id_aluno, id_disciplina, tipo_avaliacao, valor_nota):
    if valor_nota is None or valor_nota < 0 or valor_nota > 10_0:
        st_warning("⚠️ Erro: Insira um valor de nota válido (0_0 a 10_0)_")
        return
    conn = sqlite3_connect(DB_NAME)
    cursor = conn_cursor()
    try:
        cursor_execute("""REPLACE INTO Notas (id_aluno, id_disciplina, tipo_avaliacao, valor_nota) VALUES (?, ?, ?, ?)""", (id_aluno, id_disciplina, tipo_avaliacao, valor_nota))
        conn_commit()
        st_success(f"✅ Nota {tipo_avaliacao} ({valor_nota:_1f}) inserida/atualizada_")
    except Exception as e:
        st_error(f"❌ Erro ao inserir nota: {e}")
    finally: conn_close()

def obter_frequencia_por_aula(id_disciplina, data_aula):
    conn = sqlite3_connect(DB_NAME)
    cursor = conn_cursor()
    id_turma_padrao = 1
    cursor_execute("""
        SELECT id_aula FROM Aulas WHERE id_turma = ? AND id_disciplina = ? AND data_aula = ?
      result = cursor_fetchone()
    if not result:
        conn_close()
        return None, "Aula não encontrada para essa data/disciplina_"
    id_aula = result[0]
    df = pd_read_sql_query(f"""
        SELECT 
            A_nome AS "Aluno", 
            F_id_frequencia,
            F_presente 
        FROM Frequencia F
        JOIN Alunos A ON F_id_aluno = A_id_aluno
        WHERE F_id_aula = {id_aula}
        ORDER BY A_nome;
    """, conn)
    conn_close()
    
        if df_empty:
        return None, f"Nenhum registro de frequência encontrado para a Aula ID: {id_aula}_"
        
    df['Status Atual'] = df['presente']_apply(lambda x: 'PRESENTE ✅' if x == 1 else 'FALTA 🚫')
    df['Opção'] = df['id_frequencia']_astype(str) + ' - ' + df['Aluno']
    return df, id_aula
    
def atualizar_status_frequencia(id_frequencia, novo_status):
    conn = sqlite3_connect(DB_NAME)
    cursor = conn_cursor()
    try:
        cursor_execute("""
            UPDATE Frequencia SET presente = ? WHERE id_frequencia = ?
        """, (novo_status, id_frequencia))
        conn_commit()
        st_success(f"✅ Status de Presença Atualizado! (ID Frequência: {id_frequencia})")
    except Exception as e:
        st_error(f"❌ Erro ao atualizar frequência: {e}")
    finally:
        conn_close()

def gerar_relatorio_final_completo():
    try:
        conn = sqlite3_connect(DB_NAME)
        query_sql_completa = """
        SELECT A_nome AS "Aluno", D_nome_disciplina AS "Disciplina", 
            MAX(CASE WHEN N_tipo_avaliacao = 'P1' THEN N_valor_nota ELSE NULL END) AS "P1",
            MAX(CASE WHEN N_tipo_avaliacao = 'P2' THEN N_valor_nota ELSE NULL END) AS "P2",
            MAX(CASE WHEN N_tipo_avaliacao = 'P3' THEN N_valor_nota ELSE NULL END) AS "P3",
            COUNT(CASE WHEN F_presente = 1 THEN 1 ELSE NULL END) AS "Total_Presencas",
            COUNT(AU_id_aula) AS "Total_Aulas"
        FROM Alunos A CROSS JOIN Disciplinas D 
        LEFT JOIN Notas N ON A_id_aluno = N_id_aluno AND D_id_disciplina = N_id_disciplina
        LEFT JOIN Aulas AU ON D_id_disciplina = AU_id_disciplina
        LEFT JOIN Frequencia F ON A_id_aluno = F_id_aluno AND AU_id_aula = F_id_aula
        GROUP BY A_nome, D_nome_disciplina;
        df_relatorio = pd_read_sql_query(query_sql_completa, conn)

    except Exception as e:
        st_error(f"❌ ERRO FATAL na consulta SQL/Pandas_ Verifique a estrutura do DB_ Mensagem: {e}")
        return

    # Tratamento para evitar KeyError se a consulta não retornar dados
    if df_relatorio_empty:
        st_info("Nenhum dado de aluno/disciplina encontrado no DB para o relatório_ Verifique a inicialização_")
        return

    resultados_finais = []
    for index, row in df_relatorio_iterrows():
        total_aulas = row['Total_Aulas'] or 0; total_presencas = row['Total_Presencas'] or 0
        frequencia_percentual = (total_presencas / total_aulas * 100) if total_aulas > 0 else 0
        
        avaliacoes = {"P1": row_get('P1'), "P2": row_get('P2'), "P3": row_get('P3')}
        
        nota_final, situacao_nota, media_parcial = calcular_media_final(avaliacoes)
        situacao_frequencia = "REPROVADO POR FALTA" if frequencia_percentual < CORTE_FREQUENCIA else "APROVADO POR FREQUÊNCIA"

        if situacao_frequencia_startswith("REPROVADO") or situacao_nota_startswith("REPROVADO"):
            situacao_final = "REPROVADO GERAL 🔴"
        elif situacao_nota_startswith("PENDENTE"):
            situacao_final = "PENDENTE ⚠️"
        else:
            situacao_final = "APROVADO GERAL 🟢"

        resultados_finais_append({
            "Aluno": row['Aluno'], "Disciplina": row['Disciplina'],
            "P1": f"{row['P1']:_1f}" if pd_notna(row['P1']) else '-',
            "P2": f"{row['P2']:_1f}" if pd_notna(row['P2']) else '-',
            "P3": f"{row['P3']:_1f}" if pd_notna(row['P3']) else '-',
            "Frequência (%)": f"{frequencia_percentual:_1f}",
            "Nota Final": f"{nota_final:_1f}",
            "Situação Final": situacao_final
        })

    if not resultados_finais: st_info("Nenhum dado encontrado para o relatório_")
    
    st_markdown("### Relatório Final Consolidado")
    df_final = pd_DataFrame(resultados_finais)
    st_dataframe(df_final_set_index(["Aluno", "Disciplina"]), use_container_width=True)


    def main():
    st_set_page_config(layout="wide") 

    st_title("👨‍🏫 Diário de Classe Interativo") 
    st_markdown("---") 

    try:
        SENHA_CORRETA = st_secrets["app_password"]
        usuario_correto = st_secrets["app_user"]
    except KeyError:
        SENHA_CORRETA = ""
        usuario_correto = ""
        
    st_sidebar_title("Login")
    username = st_sidebar_text_input("Usuário")
    password = st_sidebar_text_input("Senha", type="password")

        if username == usuario_correto and password == SENHA_CORRETA and usuario_correto != "":
        st_sidebar_success("Login bem-sucedido!")
        
        aluno_map_nome, disciplina_map_nome = criar_e_popular_sqlite()
        
        aluno_map_id = {v: k for k, v in aluno_map_nome_items()}
        disciplina_map_id = {v: k for k, v in disciplina_map_nome_items()}

        st_header("🗓️ 1_ Lançamento de Aulas")
        with st_form("form_aulas"):
            col1, col2, col3 = st_columns(3)
            
            disciplina_aula_nome = col1_selectbox('Disciplina', options=list(disciplina_map_nome_keys()))
            data_input = col2_date_input('Data', value=date_today())
            conteudo = col3_text_input('Conteúdo da Aula')
            
            id_disciplina = disciplina_map_nome_get(disciplina_aula_nome)

            submitted_aula = st_form_submit_button("Lançar Aula e Marcar Todos Presentes")
            
            if submitted_aula:
                lancar_aula_e_frequencia(id_disciplina, data_input_strftime("%Y-%m-%d"), conteudo)
                st_rerun() 

            st_header("📋 2_ Ajuste de Faltas Pontuais")
        
        col1, col2 = st_columns(2)
        disciplina_chamada_nome = col1_selectbox('Disciplina (Ajuste)', options=list(disciplina_map_nome_keys()), key="sel_disc_chamada")
        data_consulta = col2_date_input('Data da Aula (Ajuste)', value=date_today(), key="data_chamada")
        
        id_disciplina_chamada = disciplina_map_nome_get(disciplina_chamada_nome)
        
        if st_button("Carregar Chamada da Aula"):
            df_frequencia_atual, id_aula_ou_erro = obter_frequencia_por_aula(id_disciplina_chamada, data_consulta_strftime("%Y-%m-%d"))
            
            if isinstance(df_frequencia_atual, pd_DataFrame):
                st_session_state['df_chamada'] = df_frequencia_atual
                st_session_state['id_aula'] = id_aula_ou_erro
                st_session_state['msg_chamada'] = f"✅ Chamada Carregada (Aula ID: {id_aula_ou_erro})"
            else:
                st_session_state['df_chamada'] = None
                st_session_state['msg_chamada'] = f"❌ ERRO: {id_aula_ou_erro}" 

            if 'msg_chamada' in st_session_state:
            st_markdown(st_session_state['msg_chamada'])
            if st_session_state['df_chamada'] is not None and not st_session_state['df_chamada']_empty:
                st_dataframe(st_session_state['df_chamada'][['Aluno', 'Status Atual']], hide_index=True)
                st_markdown("---")

                st_subheader("Alterar Status (Falta/Presença)")
                
                df_chamada = st_session_state['df_chamada']                
                opcoes_ajuste = {row['Aluno']: row['id_frequencia'] for index, row in df_chamada_iterrows()}
                
                col_aluno, col_status = st_columns([2, 1])

                aluno_ajuste = col_aluno_selectbox('Aluno para Ajuste', options=list(opcoes_ajuste_keys()))
                novo_status_label = col_status_selectbox('Novo Status', options=['PRESENTE', 'FALTA'])

                if st_button("Salvar Alteração de Frequência"):
                    id_frequencia_registro = opcoes_ajuste[aluno_ajuste]
                    novo_status = 1 if novo_status_label == 'PRESENTE' else 0
                    
                    atualizar_status_frequencia(id_frequencia_registro, novo_status)
                    st_info("Atualização salva_ Recarregue a chamada para confirmar_")
                    st_rerun()


        st_header("🖊️ 3_ Lançamento de Notas")
        with st_form("form_notas"):
            col1, col2, col3, col4 = st_columns(4)
            
            aluno_nome = col1_selectbox('Aluno(a)', options=list(aluno_map_nome_keys()))
            disciplina_nome = col2_selectbox('Disciplina (Nota)', options=list(disciplina_map_nome_keys()), key="disc_nota")
            tipo_avaliacao = col3_selectbox('Avaliação', options=['P1', 'P2', 'P3'])
            valor_nota = col4_number_input('Nota (0-10)', min_value=0_0, max_value=10_0, step=0_5, value=7_0)
            
            id_aluno = aluno_map_nome_get(aluno_nome)
            id_disciplina = disciplina_map_nome_get(disciplina_nome)

            submitted_nota = st_form_submit_button("Inserir/Atualizar Nota")

            if submitted_nota:
                inserir_nota_no_db(id_aluno, id_disciplina, tipo_avaliacao, valor_nota)
                st_rerun()


        st_markdown("---")

        st_header("📊 Relatório Consolidado")
        gerar_relatorio_final_completo()
        
    elif username or password:
        st_sidebar_error("Usuário ou senha incorretos_")
        return # Impede que o restante do app seja carregado
    
    else:
        st_info("Insira seu nome de usuário e senha na barra lateral para acessar o Diário de Classe_")
        return

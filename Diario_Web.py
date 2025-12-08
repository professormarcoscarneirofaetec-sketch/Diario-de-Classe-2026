st.markdown("---")

        # =========================================================================
        # 4. Relatório Consolidado
        # =========================================================================
        st.header("📊 Relatório Consolidado")
        
        # 1. Chama a função para gerar o relatório e retorna o DataFrame
        df_relatorio_final = gerar_relatorio_final_completo()
        
        if df_relatorio_final is not None and not df_relatorio_final.empty:
            st.markdown("---")
            col_csv, col_print = st.columns([1, 4])
            
            # 2. BOTÃO GERAR CONTEÚDO (CSV)
            # Transforma o DataFrame em CSV para download
            csv_data = df_relatorio_final.to_csv(index=False).encode('utf-8')
            col_csv.download_button(
                label="⬇️ Gerar Conteúdo (CSV)",
                data=csv_data,
                file_name=f'Relatorio_Diario_Classe_{date.today()}.csv',
                mime='text/csv',
                key='download_csv'
            )
            
            # 3. BOTÃO IMPRIMIR RELATÓRIO (USANDO ST.BUTTON + JAVASCRIPT)
            if col_print.button("🖨️ Imprimir Relatório (Página Atual)"):
                st.components.v1.html(
                    """
                    <script>
                        window.print();
                    </script>
                    """,
                    height=0, width=0
                )
        
    elif username == "" and password == "":
        # Mensagem inicial para guiar o usuário (apenas se os campos estiverem vazios)
        st.info("Insira seu nome de usuário e senha na barra lateral para acessar o Diário de Classe.")
        return 
        
    else:
        # Mensagem de erro (apenas se houver tentativa de login inválida)
        st.sidebar.error("Usuário ou senha incorretos.")
        return # Impede que o restante do app seja carregado

if __name__ == "__main__":
    main()

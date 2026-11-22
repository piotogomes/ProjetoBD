from servicos.database.manager import DatabaseManager

#Requisito funcional 1: Consultas sobre desempenho dos alunos
#Domínio 1: Engajamento e moedas
def consultar_engajamento_moedas(
    ultimos_meses=None,
    tipo_impacto=None,       # "maior" ou "menor"
    top_atividades=None,
    ordenar_por="girassois", # "girassois", "participacoes", "media_atividade"
    ordem="desc",
    limite=None
):

    #consulta base
    query = """
        SELECT al.nome,
               SUM(p.girassol_recebido) AS total_girassois,
               COUNT(p.cod_atividade) AS qtd_participacoes,
               ROUND((SUM(p.girassol_recebido) * 1.0) / COUNT(p.cod_atividade), 2) AS media_por_atividade
        FROM aluno al
        JOIN participacao p ON al.cpf = p.cpf_aluno
        JOIN ministra_atividade ma ON p.cod_atividade = ma.cod_atividade
        WHERE 1 = 1
    """
    parametros = []

    if ultimos_meses is not None:
        query += " AND ma.data_atividade >= CURRENT_DATE - (%s * INTERVAL '1 month')"
        parametros.append(int(ultimos_meses))

    if tipo_impacto in ("maior", "menor") and top_atividades is not None:
        direcao_impacto = "DESC" if tipo_impacto == "maior" else "ASC"
        query += f"""
            AND p.cod_atividade IN (
                SELECT cod_atividade
                FROM participacao
                GROUP BY cod_atividade
                ORDER BY SUM(girassol_recebido) {direcao_impacto}
                LIMIT %s
            )
        """
        parametros.append(int(top_atividades))

    query += " GROUP BY al.cpf, al.nome"

    colunas_ordenacao = {
        "girassois": "total_girassois",
        "participacoes": "qtd_participacoes",
        "media_atividade": "media_por_atividade"
    }
    coluna = colunas_ordenacao.get(ordenar_por, "total_girassois")
    direcao = "ASC" if str(ordem).lower() == "asc" else "DESC"
    query += f" ORDER BY {coluna} {direcao}"

    if limite is not None:
        query += " LIMIT %s"
        parametros.append(int(limite))

    db = DatabaseManager()
    try:
        return db.execute_select_all(query, tuple(parametros))
    finally:
        db.close()

#Domínio 2: Desempenho pedagogico
def consultar_desempenho_pedagogico(
    disciplina=None,
    abaixo_media=False,
    qtd_disciplinas_abaixo=None,
    ordem="desc",
    limite=None
):
    query = """
        SELECT al.nome AS nome_aluno,
               m.nota_recebida,
               d.nome AS nome_disciplina
        FROM aluno al
        JOIN matricula m ON al.cpf = m.cpf_aluno
        JOIN disciplina d ON m.cod_disciplina = d.cod
        WHERE 1 = 1
    """
    parametros = []

    if disciplina:
        query += " AND d.nome ILIKE %s"
        parametros.append(f"%{disciplina}%")

    if abaixo_media or qtd_disciplinas_abaixo is not None:
        query += """
            AND m.nota_recebida < (
                SELECT AVG(m2.nota_recebida)
                FROM matricula m2
                WHERE m2.cod_disciplina = m.cod_disciplina
            )
        """

    if qtd_disciplinas_abaixo is not None:
        query += """
            AND al.cpf IN (
                SELECT m_sub.cpf_aluno
                FROM matricula m_sub
                WHERE m_sub.nota_recebida < (
                    SELECT AVG(m2.nota_recebida)
                    FROM matricula m2
                    WHERE m2.cod_disciplina = m_sub.cod_disciplina
                )
                GROUP BY m_sub.cpf_aluno
                HAVING COUNT(m_sub.cod_disciplina) = %s
            )
        """
        parametros.append(int(qtd_disciplinas_abaixo))

    direcao = "ASC" if str(ordem).lower() == "asc" else "DESC"
    query += f" ORDER BY m.nota_recebida {direcao}"

    if limite is not None:
        query += " LIMIT %s"
        parametros.append(int(limite))

    db = DatabaseManager()
    try:
        return db.execute_select_all(query, tuple(parametros))
    finally:
        db.close()

#Domínio 3: Necessidades especiais
def consultar_necessidades_contatos(ordenar_por="contatos", limite=None):
    query = """
        SELECT al.nome AS nome_aluno,
               COUNT(DISTINCT c.cpf_coordenador || '-' || c.cpf_responsavel || '-' || c.motivo) AS qtd_contatos,
               COUNT(DISTINCT an.cuidado_especial) AS qtd_necessidades
        FROM aluno al
        LEFT JOIN possui_resp_aluno pra ON al.cpf = pra.cpf_aluno
        LEFT JOIN contato c ON pra.cpf_responsavel = c.cpf_responsavel
        LEFT JOIN aluno_necessidade an ON al.cpf = an.cpf_aluno
        WHERE 1 = 1
        GROUP BY al.cpf, al.nome
    """
    parametros = []

    coluna = "qtd_necessidades" if ordenar_por == "necessidades" else "qtd_contatos"
    query += f" ORDER BY {coluna} DESC"

    if limite is not None:
        query += " LIMIT %s"
        parametros.append(int(limite))

    db = DatabaseManager()
    try:
        return db.execute_select_all(query, tuple(parametros))
    finally:
        db.close()

#Requisito funcional 2: Consultas sobre desempenho de funcionários
#Domínio 4: Quanto às atividades
def consultar_desempenho_recreadores(
    top_girassois=None,
    ordenar_por="maior_nota", # "maior_nota", "menor_nota", "media"
    ordem="desc",
    limite=None
):
    query = """
        SELECT f.nome AS nome_recreador,
               ROUND(AVG(ar.nota_recebida), 2) AS media_notas,
               MAX(ar.nota_recebida) AS maior_nota,
               MIN(ar.nota_recebida) AS menor_nota
        FROM funcionario f
        JOIN recreador r ON f.cpf = r.cpf_funcionario
        LEFT JOIN avalia_recreador ar ON r.cpf_funcionario = ar.cpf_recreador
        WHERE 1 = 1
    """
    parametros = []

    if top_girassois is not None:
        query += """
            AND f.cpf IN (
                SELECT ma2.cpf_recreador
                FROM participacao p2
                JOIN ministra_atividade ma2 ON ma2.cod_atividade = p2.cod_atividade
                GROUP BY ma2.cpf_recreador
                ORDER BY SUM(p2.girassol_recebido) DESC
                LIMIT %s
            )
        """
        parametros.append(int(top_girassois))

    query += " GROUP BY f.cpf, f.nome"

    colunas_ordenacao = {
        "maior_nota": "maior_nota",
        "menor_nota": "menor_nota",
        "media": "media_notas"
    }
    coluna = colunas_ordenacao.get(ordenar_por, "maior_nota")
    direcao = "ASC" if str(ordem).lower() == "asc" else "DESC"
    query += f" ORDER BY {coluna} {direcao} NULLS LAST"

    if limite is not None:
        query += " LIMIT %s"
        parametros.append(int(limite))

    db = DatabaseManager()
    try:
        return db.execute_select_all(query, tuple(parametros))
    finally:
        db.close()
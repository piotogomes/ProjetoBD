from servicos.database.manager import DatabaseManager

#Requisito funcional 1: Consultas sobre desempenho e interesses dos alunos
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
        WHERE 1 = 1
    """
    parametros = []

    if ultimos_meses is not None:
        query += """
            AND EXISTS (
                SELECT 1
                FROM ministra_atividade ma
                WHERE ma.cod_atividade = p.cod_atividade
                  AND ma.data_atividade >= CURRENT_DATE - (%s * INTERVAL '1 month')
            )
        """
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

#Domínio 4: Quanto aos interesses
def consultar_alunos_por_interesse(
    interesse=None,
    cod_atividade=None,
    apenas_nao_participantes=False,
    ordem="asc",
    limite=None
):
    query = """
        SELECT DISTINCT
            al.cpf,
            al.nome AS nome_aluno,
            al.escolaridade,
            ai.interesse
        FROM aluno al
        JOIN aluno_interesse ai ON al.cpf = ai.cpf_aluno
        WHERE 1 = 1
    """
    parametros = []

    if interesse:
        query += " AND ai.interesse ILIKE %s"
        parametros.append(f"%{interesse}%")

    if cod_atividade:
        query += """
            AND EXISTS (
                SELECT 1
                FROM atividade a
                WHERE a.cod = %s
                  AND (
                      a.nome ILIKE '%%' || ai.interesse || '%%'
                      OR ai.interesse ILIKE '%%' || a.nome || '%%'
                  )
            )
        """
        parametros.append(cod_atividade)

        if apenas_nao_participantes:
            query += """
                AND NOT EXISTS (
                    SELECT 1
                    FROM participacao p
                    WHERE p.cpf_aluno = al.cpf
                      AND p.cod_atividade = %s
                )
            """
            parametros.append(cod_atividade)

    direcao = "DESC" if str(ordem).lower() == "desc" else "ASC"
    query += f" ORDER BY al.nome {direcao}"

    if limite is not None:
        query += " LIMIT %s"
        parametros.append(int(limite))

    db = DatabaseManager()
    try:
        return db.execute_select_all(query, tuple(parametros))
    finally:
        db.close()

#Interesse nas atividades
def listar_opcoes_interesses():
    query = """
        SELECT DISTINCT interesse
        FROM aluno_interesse
        ORDER BY interesse ASC
    """
    db = DatabaseManager()
    try:
        return db.execute_select_all(query)
    finally:
        db.close()


#Requisito funcional 2: Consultas sobre desempenho de funcionários
#Domínio 5: Quanto às atividades
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


#Domínio 6: Quanto às aulas (Professores)
def consultar_desempenho_professores(
    ordenar_por="maior_nota_coordenador", # "maior_nota_coordenador", "media_notas_coordenador", "media_notas_alunos"
    ordem="desc",
    limite=None
):
    query = """
        SELECT f.nome AS nome_professor,
               ROUND(AVG(ap.nota_recebida), 2) AS media_notas_coordenador,
               MAX(ap.nota_recebida) AS maior_nota_coordenador,
               ROUND((
                   SELECT AVG(m.nota_recebida)
                   FROM ministra_oferecimento mo
                   JOIN matricula m ON m.cod_disciplina = mo.cod_disciplina
                   WHERE mo.cpf_professor = p.cpf_funcionario
               ), 2) AS media_notas_alunos
        FROM funcionario f
        JOIN professor p ON f.cpf = p.cpf_funcionario
        LEFT JOIN avalia_professor ap ON p.cpf_funcionario = ap.cpf_professor
        WHERE 1 = 1
    """
    parametros = []

    query += " GROUP BY f.cpf, f.nome, p.cpf_funcionario"

    colunas_ordenacao = {
        "maior_nota_coordenador": "maior_nota_coordenador",
        "media_notas_coordenador": "media_notas_coordenador",
        "media_notas_alunos": "media_notas_alunos"
    }
    coluna = colunas_ordenacao.get(ordenar_por, "maior_nota_coordenador")
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


#Domínio 7: Quanto à carga de trabalho
def consultar_carga_trabalho(
    ultimos_meses=None,
    perfil=None, # "recreador", "professor", "coordenador"
    ordenar_por="atividades", # "atividades", "oferecimentos", "contatos", "disponibilidade_alocacao"
    ordem="desc",
    limite=None
):
    query = """
        SELECT f.nome AS nome_funcionario,
               COUNT(DISTINCT ma.cod_atividade || '-' || ma.data_atividade || '-' || ma.horario) AS qtd_atividades,
               COUNT(DISTINCT mo.cod_disciplina || '-' || mo.data_inicio || '-' || mo.data_fim) AS qtd_oferecimentos,
               COUNT(DISTINCT c.cpf_responsavel || '-' || c.motivo) AS qtd_contatos,
               COUNT(DISTINCT fd.disponibilidade) AS qtd_disponibilidades
        FROM funcionario f
        LEFT JOIN ministra_atividade ma ON f.cpf = ma.cpf_recreador
        LEFT JOIN ministra_oferecimento mo ON f.cpf = mo.cpf_professor
        LEFT JOIN contato c ON f.cpf = c.cpf_coordenador
        LEFT JOIN funcionario_disponibilidade fd ON f.cpf = fd.cpf_funcionario
        WHERE 1 = 1
    """
    parametros = []

    if ultimos_meses is not None:
        query += " AND ma.data_atividade >= CURRENT_DATE - (%s * INTERVAL '1 month')"
        parametros.append(int(ultimos_meses))

    if perfil == "recreador":
        query += " AND ma.cpf_recreador IS NOT NULL"
    elif perfil == "professor":
        query += " AND mo.cpf_professor IS NOT NULL"
    elif perfil == "coordenador":
        query += " AND c.cpf_coordenador IS NOT NULL"

    query += " GROUP BY f.cpf, f.nome"

    if ordenar_por == "disponibilidade_alocacao":
        query += """
            ORDER BY qtd_disponibilidades DESC,
                     (COUNT(DISTINCT ma.cod_atividade || '-' || ma.data_atividade || '-' || ma.horario)
                    + COUNT(DISTINCT mo.cod_disciplina || '-' || mo.data_inicio || '-' || mo.data_fim)) ASC
        """
    else:
        colunas_ordenacao = {
            "atividades": "qtd_atividades",
            "oferecimentos": "qtd_oferecimentos",
            "contatos": "qtd_contatos"
        }
        coluna = colunas_ordenacao.get(ordenar_por, "qtd_atividades")
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


#Requisito funcional 3: Consultas sobre atividades e aulas
#Domínio 8: Desempenho e logística das atividades
def consultar_desempenho_atividades(
    ultimos_meses=None,
    local_atividade=None,
    data_inicio=None,
    data_fim=None,
    ordenar_por="participacoes", # "participacoes", "media_notas_recreadores", "materiais"
    ordem="desc",
    limite=None
):
    query = """
        SELECT a.nome AS nome_atividade,
               a.local_atividade,
               a.periodo,
               COUNT(DISTINCT p.cpf_aluno) AS qtd_participacoes,
               COUNT(DISTINCT am.material) AS qtd_materiais,
               ROUND((
                   SELECT AVG(ar.nota_recebida)
                   FROM avalia_recreador ar
                   WHERE ar.cod_atividade = a.cod
               ), 2) AS media_notas_recreadores
        FROM atividade a
        LEFT JOIN participacao p ON a.cod = p.cod_atividade
        LEFT JOIN ministra_atividade ma ON a.cod = ma.cod_atividade
        LEFT JOIN atividade_material am ON a.cod = am.cod_atividade
        WHERE 1 = 1
    """
    parametros = []

    if ultimos_meses is not None:
        query += " AND ma.data_atividade >= CURRENT_DATE - (%s * INTERVAL '1 month')"
        parametros.append(int(ultimos_meses))

    if local_atividade:
        query += " AND a.local_atividade ILIKE %s"
        parametros.append(f"%{local_atividade}%")

    if data_inicio:
        query += " AND ma.data_atividade >= %s"
        parametros.append(data_inicio)

    if data_fim:
        query += " AND ma.data_atividade <= %s"
        parametros.append(data_fim)

    query += " GROUP BY a.cod, a.nome, a.local_atividade, a.periodo"

    colunas_ordenacao = {
        "participacoes": "qtd_participacoes",
        "media_notas_recreadores": "media_notas_recreadores",
        "materiais": "qtd_materiais"
    }
    coluna = colunas_ordenacao.get(ordenar_por, "qtd_participacoes")
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


#Domínio 9: Quanto às aulas (Disciplinas e Oferecimentos)
def consultar_disciplinas_oferecimentos(
    data_inicio=None,
    data_fim=None,
    professor=None,
    ordenar_por="media_notas", # "media_notas", "matriculados", "abaixo_media", "data_inicio"
    ordem="desc",
    limite=None
):
    query = """
        SELECT d.nome AS nome_disciplina,
               o.data_inicio,
               o.data_fim,
               o.hora_inicio,
               f.nome AS nome_professor,
               COUNT(DISTINCT m.cpf_aluno) AS qtd_matriculados,
               ROUND((
                   SELECT AVG(m2.nota_recebida)
                   FROM matricula m2
                   WHERE m2.cod_disciplina = d.cod
               ), 2) AS media_notas,
               (
                   SELECT COUNT(*)
                   FROM matricula m3
                   WHERE m3.cod_disciplina = d.cod
                     AND m3.nota_recebida < (
                         SELECT AVG(m4.nota_recebida)
                         FROM matricula m4
                         WHERE m4.cod_disciplina = d.cod
                     )
               ) AS qtd_abaixo_media
        FROM disciplina d
        LEFT JOIN matricula m ON d.cod = m.cod_disciplina
        LEFT JOIN oferecimento o ON d.cod = o.cod_disciplina
        LEFT JOIN ministra_oferecimento mo ON o.cod_disciplina = mo.cod_disciplina
                                           AND o.data_inicio = mo.data_inicio
                                           AND o.data_fim = mo.data_fim
        LEFT JOIN funcionario f ON mo.cpf_professor = f.cpf
        WHERE 1 = 1
    """
    parametros = []

    if data_inicio:
        query += " AND o.data_inicio >= %s"
        parametros.append(data_inicio)

    if data_fim:
        query += " AND o.data_fim <= %s"
        parametros.append(data_fim)

    if professor:
        query += " AND f.nome ILIKE %s"
        parametros.append(f"%{professor}%")

    query += " GROUP BY d.cod, d.nome, o.data_inicio, o.data_fim, o.hora_inicio, f.nome"

    colunas_ordenacao = {
        "media_notas": "media_notas",
        "matriculados": "qtd_matriculados",
        "abaixo_media": "qtd_abaixo_media",
        "data_inicio": "o.data_inicio"
    }
    coluna = colunas_ordenacao.get(ordenar_por, "media_notas")
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


#Requisito funcional 4: Educação financeira
#Domínio 10: Rendimento individual
def consultar_rendimento_individual(
    aluno=None,
    ultimos_meses=None,
    data_inicio=None,
    data_fim=None,
    ordenar_por="total_girassois", # "total_girassois", "media_girassois"
    ordem="desc",
    limite=None
):
    query = """
        SELECT al.nome AS nome_aluno,
               a.nome AS nome_atividade,
               SUM(p.girassol_recebido) AS total_girassois,
               ROUND(AVG(p.girassol_recebido), 2) AS media_girassois
        FROM aluno al
        JOIN participacao p ON al.cpf = p.cpf_aluno
        JOIN atividade a ON p.cod_atividade = a.cod
        JOIN ministra_atividade ma ON a.cod = ma.cod_atividade
        WHERE 1 = 1
    """
    parametros = []

    if aluno:
        query += " AND al.nome ILIKE %s"
        parametros.append(f"%{aluno}%")

    if ultimos_meses is not None:
        query += " AND ma.data_atividade >= CURRENT_DATE - (%s * INTERVAL '1 month')"
        parametros.append(int(ultimos_meses))

    if data_inicio:
        query += " AND ma.data_atividade >= %s"
        parametros.append(data_inicio)

    if data_fim:
        query += " AND ma.data_atividade <= %s"
        parametros.append(data_fim)

    query += " GROUP BY al.cpf, al.nome, a.cod, a.nome"

    colunas_ordenacao = {
        "total_girassois": "total_girassois",
        "media_girassois": "media_girassois"
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


#Domínio 11: Distribuição de moedas no projeto
def consultar_distribuicao_moedas(
    ultimos_meses=None,
    data_inicio=None,
    data_fim=None,
    ordenar_por="total_girassois", # "total_girassois", "media_girassois"
    ordem="desc",
    limite=None
):
    query = """
        SELECT a.nome AS nome_atividade,
               al.escolaridade,
               SUM(p.girassol_recebido) AS total_girassois,
               ROUND(AVG(p.girassol_recebido), 2) AS media_girassois
        FROM participacao p
        JOIN atividade a ON p.cod_atividade = a.cod
        JOIN aluno al ON p.cpf_aluno = al.cpf
        JOIN ministra_atividade ma ON a.cod = ma.cod_atividade
        WHERE 1 = 1
    """
    parametros = []

    if ultimos_meses is not None:
        query += " AND ma.data_atividade >= CURRENT_DATE - (%s * INTERVAL '1 month')"
        parametros.append(int(ultimos_meses))

    if data_inicio:
        query += " AND ma.data_atividade >= %s"
        parametros.append(data_inicio)

    if data_fim:
        query += " AND ma.data_atividade <= %s"
        parametros.append(data_fim)

    query += " GROUP BY a.cod, a.nome, al.escolaridade"

    colunas_ordenacao = {
        "total_girassois": "total_girassois",
        "media_girassois": "media_girassois"
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
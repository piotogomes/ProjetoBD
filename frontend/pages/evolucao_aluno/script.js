document.addEventListener("DOMContentLoaded", async () => {
    const tipoImpactoSelect = document.getElementById("eng-tipo-impacto");
    const topAtividadesInput = document.getElementById("eng-top-atividades");
    const atividadeSelect = document.getElementById("int-atividade");
    const naoParticipaCheck = document.getElementById("int-nao-participa");
    const interesseSelect = document.getElementById("int-interesse");

    // Se escolher tipo_impacto sem definir top_atividades, preenche padrão 3 para a consulta funcionar
    tipoImpactoSelect.addEventListener("change", () => {
        if (tipoImpactoSelect.value && !topAtividadesInput.value) {
            topAtividadesInput.value = "3";
        }
        if (!tipoImpactoSelect.value) {
            topAtividadesInput.value = "";
        }
    });

    function syncNaoParticipaState() {
        const hasActivity = Boolean(atividadeSelect.value);
        naoParticipaCheck.disabled = !hasActivity;
        if (!hasActivity) {
            naoParticipaCheck.checked = false;
        }
    }
    atividadeSelect.addEventListener("change", syncNaoParticipaState);
    syncNaoParticipaState();

    // Carrega opções dinâmicas de interesses
    try {
        const res = await fetchConsulta("/api/consultas/interesses/opcoes");
        const opcoes = res.dados || [];
        opcoes.forEach((item) => {
            const opt = document.createElement("option");
            opt.value = item.interesse;
            opt.textContent = item.interesse;
            interesseSelect.appendChild(opt);
        });
    } catch (err) {
        console.warn("Não foi possível carregar opções de interesses:", err.message);
    }

    const controllers = {
        engajamento: setupDomainController({
            formId: "form-engajamento",
            endpoint: "/api/consultas/engajamento",
            tableContainerId: "table-engajamento",
            countBadgeId: "count-engajamento",
            presetsSelector: ".preset-engajamento",
            resetBtnId: "reset-engajamento",
            getParams: (form) => {
                const tipoImpacto = form.elements.tipo_impacto.value;
                let topAtividades = form.elements.top_atividades.value;
                if (tipoImpacto && !topAtividades) {
                    topAtividades = "3";
                    form.elements.top_atividades.value = "3";
                }
                return {
                    ultimos_meses: form.elements.ultimos_meses.value,
                    tipo_impacto: tipoImpacto,
                    top_atividades: topAtividades,
                    ordenar_por: form.elements.ordenar_por.value,
                    ordem: form.elements.ordem.value,
                    limite: form.elements.limite.value,
                };
            },
            columns: [
                { key: "nome", label: "Aluno" },
                {
                    key: "total_girassois",
                    label: "Total de Girassóis",
                    render: (v) => `<span class="badge badge-gold">🌻 ${formatInt(v)}</span>`,
                },
                {
                    key: "qtd_participacoes",
                    label: "Participações",
                    render: (v) => formatInt(v),
                },
                {
                    key: "media_por_atividade",
                    label: "Média por Atividade",
                    render: (v) => formatNumber(v, 2),
                },
            ],
        }),

        pedagogico: setupDomainController({
            formId: "form-pedagogico",
            endpoint: "/api/consultas/pedagogico",
            tableContainerId: "table-pedagogico",
            countBadgeId: "count-pedagogico",
            presetsSelector: ".preset-pedagogico",
            resetBtnId: "reset-pedagogico",
            getParams: (form) => ({
                disciplina: form.elements.disciplina.value,
                abaixo_media: form.elements.abaixo_media.checked ? "true" : "false",
                qtd_disciplinas_abaixo: form.elements.qtd_disciplinas_abaixo.value,
                ordem: form.elements.ordem.value,
                limite: form.elements.limite.value,
            }),
            columns: [
                { key: "nome_aluno", label: "Aluno" },
                { key: "nome_disciplina", label: "Disciplina" },
                {
                    key: "nota_recebida",
                    label: "Nota",
                    render: (v) => {
                        if (v === null || v === undefined) {
                            return '<span class="badge badge-blue">Não lançada</span>';
                        }
                        const num = Number(v);
                        const cls = num < 6 ? "badge-red" : "badge-green";
                        return `<span class="badge ${cls}">${formatNumber(num, 2)}</span>`;
                    },
                },
            ],
        }),

        necessidades: setupDomainController({
            formId: "form-necessidades",
            endpoint: "/api/consultas/necessidades",
            tableContainerId: "table-necessidades",
            countBadgeId: "count-necessidades",
            presetsSelector: ".preset-necessidades",
            resetBtnId: "reset-necessidades",
            getParams: (form) => ({
                ordenar_por: form.elements.ordenar_por.value,
                limite: form.elements.limite.value,
            }),
            columns: [
                { key: "nome_aluno", label: "Aluno" },
                {
                    key: "qtd_contatos",
                    label: "Contatos com Responsáveis",
                    render: (v) => formatInt(v),
                },
                {
                    key: "qtd_necessidades",
                    label: "Necessidades Especiais",
                    render: (v) => {
                        const n = Number(v || 0);
                        return n > 0
                            ? `<span class="badge badge-blue">${formatInt(n)}</span>`
                            : "0";
                    },
                },
            ],
        }),

        interesses: setupDomainController({
            formId: "form-interesses",
            endpoint: "/api/consultas/interesses",
            tableContainerId: "table-interesses",
            countBadgeId: "count-interesses",
            presetsSelector: ".preset-interesses",
            resetBtnId: "reset-interesses",
            onReset: () => syncNaoParticipaState(),
            getParams: (form) => {
                syncNaoParticipaState();
                return {
                    interesse: form.elements.interesse.value,
                    cod_atividade: form.elements.cod_atividade.value,
                    apenas_nao_participantes: form.elements.apenas_nao_participantes.checked ? "true" : "false",
                    ordem: form.elements.ordem.value,
                    limite: form.elements.limite.value,
                };
            },
            columns: [
                { key: "nome_aluno", label: "Aluno" },
                { key: "cpf", label: "CPF" },
                { key: "escolaridade", label: "Escolaridade" },
                {
                    key: "interesse",
                    label: "Interesse",
                    render: (v) => `<span class="badge badge-gold">${escapeHtml(v)}</span>`,
                },
            ],
        }),
    };

    const tabs = initDomainTabs((tabId) => {
        if (controllers[tabId]) {
            controllers[tabId].ensureLoaded();
        }
    });

    tabs.activate("engajamento");
});

document.addEventListener("DOMContentLoaded", () => {
    const controllers = {
        atividades: setupDomainController({
            formId: "form-atividades",
            endpoint: "/api/consultas/atividades",
            tableContainerId: "table-atividades",
            countBadgeId: "count-atividades",
            presetsSelector: ".preset-atividades",
            resetBtnId: "reset-atividades",
            getParams: (form) => ({
                ultimos_meses: form.elements.ultimos_meses.value,
                local_atividade: form.elements.local_atividade.value,
                data_inicio: form.elements.data_inicio.value,
                data_fim: form.elements.data_fim.value,
                ordenar_por: form.elements.ordenar_por.value,
                ordem: form.elements.ordem.value,
                limite: form.elements.limite.value,
            }),
            columns: [
                { key: "nome_atividade", label: "Atividade" },
                { key: "local_atividade", label: "Local" },
                {
                    key: "periodo",
                    label: "Período",
                    render: (v) => `<span class="badge badge-blue">${escapeHtml(v || "—")}</span>`,
                },
                {
                    key: "qtd_participacoes",
                    label: "Participações",
                    render: (v) => formatInt(v),
                },
                {
                    key: "qtd_materiais",
                    label: "Qtd. Materiais",
                    render: (v) => formatInt(v),
                },
                {
                    key: "media_notas_recreadores",
                    label: "Média Recreadores",
                    render: (v) =>
                        v === null || v === undefined
                            ? "—"
                            : `<span class="badge badge-green">${formatNumber(v, 2)}</span>`,
                },
            ],
        }),

        disciplinas: setupDomainController({
            formId: "form-disciplinas",
            endpoint: "/api/consultas/disciplinas",
            tableContainerId: "table-disciplinas",
            countBadgeId: "count-disciplinas",
            presetsSelector: ".preset-disciplinas",
            resetBtnId: "reset-disciplinas",
            getParams: (form) => ({
                data_inicio: form.elements.data_inicio.value,
                data_fim: form.elements.data_fim.value,
                professor: form.elements.professor.value,
                ordenar_por: form.elements.ordenar_por.value,
                ordem: form.elements.ordem.value,
                limite: form.elements.limite.value,
            }),
            columns: [
                { key: "nome_disciplina", label: "Disciplina" },
                {
                    key: "data_inicio",
                    label: "Início",
                    render: (v) => formatDateBR(v),
                },
                {
                    key: "data_fim",
                    label: "Fim",
                    render: (v) => formatDateBR(v),
                },
                {
                    key: "hora_inicio",
                    label: "Horário",
                    render: (v) => formatTime(v),
                },
                {
                    key: "nome_professor",
                    label: "Professor",
                    render: (v) => escapeHtml(v || "—"),
                },
                {
                    key: "qtd_matriculados",
                    label: "Matriculados",
                    render: (v) => formatInt(v),
                },
                {
                    key: "media_notas",
                    label: "Média Notas",
                    render: (v) =>
                        v === null || v === undefined
                            ? "—"
                            : `<span class="badge badge-green">${formatNumber(v, 2)}</span>`,
                },
                {
                    key: "qtd_abaixo_media",
                    label: "Abaixo da Média",
                    render: (v) => {
                        const n = Number(v || 0);
                        return n > 0
                            ? `<span class="badge badge-red">${formatInt(n)}</span>`
                            : "0";
                    },
                },
            ],
        }),
    };

    const tabs = initDomainTabs((tabId) => {
        if (controllers[tabId]) {
            controllers[tabId].ensureLoaded();
        }
    });

    tabs.activate("atividades");
});

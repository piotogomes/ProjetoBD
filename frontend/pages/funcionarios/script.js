document.addEventListener("DOMContentLoaded", () => {
    function formatGradeBadge(v) {
        if (v === null || v === undefined) return "—";
        const num = Number(v);
        const cls = num >= 8.5 ? "badge-green" : num >= 7 ? "badge-blue" : "badge-red";
        return `<span class="badge ${cls}">${formatNumber(num, 2)}</span>`;
    }

    const controllers = {
        recreadores: setupDomainController({
            formId: "form-recreadores",
            endpoint: "/api/consultas/recreadores",
            tableContainerId: "table-recreadores",
            countBadgeId: "count-recreadores",
            presetsSelector: ".preset-recreadores",
            resetBtnId: "reset-recreadores",
            getParams: (form) => ({
                top_girassois: form.elements.top_girassois.value,
                ordenar_por: form.elements.ordenar_por.value,
                ordem: form.elements.ordem.value,
                limite: form.elements.limite.value,
            }),
            columns: [
                { key: "nome_recreador", label: "Recreador" },
                {
                    key: "media_notas",
                    label: "Média das Notas",
                    render: formatGradeBadge,
                },
                {
                    key: "maior_nota",
                    label: "Maior Nota",
                    render: formatGradeBadge,
                },
                {
                    key: "menor_nota",
                    label: "Menor Nota",
                    render: formatGradeBadge,
                },
            ],
        }),

        professores: setupDomainController({
            formId: "form-professores",
            endpoint: "/api/consultas/professores",
            tableContainerId: "table-professores",
            countBadgeId: "count-professores",
            presetsSelector: ".preset-professores",
            resetBtnId: "reset-professores",
            getParams: (form) => ({
                ordenar_por: form.elements.ordenar_por.value,
                ordem: form.elements.ordem.value,
                limite: form.elements.limite.value,
            }),
            columns: [
                { key: "nome_professor", label: "Professor" },
                {
                    key: "media_notas_coordenador",
                    label: "Média (Coordenador)",
                    render: formatGradeBadge,
                },
                {
                    key: "maior_nota_coordenador",
                    label: "Maior Nota (Coordenador)",
                    render: formatGradeBadge,
                },
                {
                    key: "media_notas_alunos",
                    label: "Média dos Alunos",
                    render: formatGradeBadge,
                },
            ],
        }),

        carga: setupDomainController({
            formId: "form-carga",
            endpoint: "/api/consultas/carga-trabalho",
            tableContainerId: "table-carga",
            countBadgeId: "count-carga",
            presetsSelector: ".preset-carga",
            resetBtnId: "reset-carga",
            getParams: (form) => ({
                ultimos_meses: form.elements.ultimos_meses.value,
                perfil: form.elements.perfil.value,
                ordenar_por: form.elements.ordenar_por.value,
                ordem: form.elements.ordem.value,
                limite: form.elements.limite.value,
            }),
            columns: [
                { key: "nome_funcionario", label: "Funcionário" },
                {
                    key: "qtd_atividades",
                    label: "Atividades",
                    render: (v) => formatInt(v),
                },
                {
                    key: "qtd_oferecimentos",
                    label: "Oferecimentos",
                    render: (v) => formatInt(v),
                },
                {
                    key: "qtd_contatos",
                    label: "Contatos",
                    render: (v) => formatInt(v),
                },
                {
                    key: "qtd_disponibilidades",
                    label: "Disponibilidades",
                    render: (v) => `<span class="badge badge-blue">${formatInt(v)}</span>`,
                },
            ],
        }),
    };

    const tabs = initDomainTabs((tabId) => {
        if (controllers[tabId]) {
            controllers[tabId].ensureLoaded();
        }
    });

    tabs.activate("recreadores");
});

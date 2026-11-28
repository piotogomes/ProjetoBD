document.addEventListener("DOMContentLoaded", () => {
    function renderSummary(containerId, rows) {
        const container = document.getElementById(containerId);
        if (!container) return;

        if (!rows || rows.length === 0) {
            container.innerHTML = "";
            return;
        }

        const totalGirassois = rows.reduce((acc, r) => acc + Number(r.total_girassois || 0), 0);
        const mediaGeral =
            rows.reduce((acc, r) => acc + Number(r.media_girassois || 0), 0) / rows.length;

        container.innerHTML = `
            <div class="summary-item">
                <div class="summary-label">Soma na Consulta</div>
                <div class="summary-value">🌻 ${formatInt(totalGirassois)}</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">Média dos Registros</div>
                <div class="summary-value">${formatNumber(mediaGeral, 2)}</div>
            </div>
        `;
    }

    const controllers = {
        individual: setupDomainController({
            formId: "form-individual",
            endpoint: "/api/consultas/rendimento-individual",
            tableContainerId: "table-individual",
            countBadgeId: "count-individual",
            presetsSelector: ".preset-individual",
            resetBtnId: "reset-individual",
            onDataLoaded: (rows) => renderSummary("summary-individual", rows),
            getParams: (form) => ({
                aluno: form.elements.aluno.value,
                ultimos_meses: form.elements.ultimos_meses.value,
                data_inicio: form.elements.data_inicio.value,
                data_fim: form.elements.data_fim.value,
                ordenar_por: form.elements.ordenar_por.value,
                ordem: form.elements.ordem.value,
                limite: form.elements.limite.value,
            }),
            columns: [
                { key: "nome_aluno", label: "Aluno" },
                { key: "nome_atividade", label: "Atividade" },
                {
                    key: "total_girassois",
                    label: "Total de Girassóis",
                    render: (v) => `<span class="badge badge-gold">🌻 ${formatInt(v)}</span>`,
                },
                {
                    key: "media_girassois",
                    label: "Média de Girassóis",
                    render: (v) => formatNumber(v, 2),
                },
            ],
        }),

        distribuicao: setupDomainController({
            formId: "form-distribuicao",
            endpoint: "/api/consultas/distribuicao-moedas",
            tableContainerId: "table-distribuicao",
            countBadgeId: "count-distribuicao",
            presetsSelector: ".preset-distribuicao",
            resetBtnId: "reset-distribuicao",
            onDataLoaded: (rows) => renderSummary("summary-distribuicao", rows),
            getParams: (form) => ({
                ultimos_meses: form.elements.ultimos_meses.value,
                data_inicio: form.elements.data_inicio.value,
                data_fim: form.elements.data_fim.value,
                ordenar_por: form.elements.ordenar_por.value,
                ordem: form.elements.ordem.value,
                limite: form.elements.limite.value,
            }),
            columns: [
                { key: "nome_atividade", label: "Atividade" },
                { key: "escolaridade", label: "Escolaridade" },
                {
                    key: "total_girassois",
                    label: "Total de Girassóis",
                    render: (v) => `<span class="badge badge-gold">🌻 ${formatInt(v)}</span>`,
                },
                {
                    key: "media_girassois",
                    label: "Média de Girassóis",
                    render: (v) => formatNumber(v, 2),
                },
            ],
        }),
    };

    const tabs = initDomainTabs((tabId) => {
        if (controllers[tabId]) {
            controllers[tabId].ensureLoaded();
        }
    });

    tabs.activate("individual");
});

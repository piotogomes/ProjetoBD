/**
 * Utilitários compartilhados para consultas dinâmicas do Projeto Girassol.
 */

function escapeHtml(value) {
    if (value === null || value === undefined) return "";
    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");
}

function formatNumber(value, decimals = 2) {
    if (value === null || value === undefined || value === "") return "—";
    const num = Number(value);
    if (Number.isNaN(num)) return escapeHtml(value);
    return num.toLocaleString("pt-BR", {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals,
    });
}

function formatInt(value) {
    if (value === null || value === undefined || value === "") return "—";
    const num = Number(value);
    if (Number.isNaN(num)) return escapeHtml(value);
    return num.toLocaleString("pt-BR");
}

function formatDateBR(value) {
    if (!value) return "—";
    const str = String(value);
    // Suporta YYYY-MM-DD ou strings GMT retornadas pelo Flask jsonify para date
    const isoMatch = str.match(/^(\d{4})-(\d{2})-(\d{2})/);
    if (isoMatch) {
        return `${isoMatch[3]}/${isoMatch[2]}/${isoMatch[1]}`;
    }
    const parsed = new Date(str);
    if (!Number.isNaN(parsed.getTime())) {
        return parsed.toLocaleDateString("pt-BR", { timeZone: "UTC" });
    }
    return escapeHtml(str);
}

function formatTime(value) {
    if (!value) return "—";
    return escapeHtml(String(value).slice(0, 5));
}

function buildQueryString(params) {
    const search = new URLSearchParams();
    Object.entries(params).forEach(([key, val]) => {
        if (val !== null && val !== undefined && String(val).trim() !== "") {
            search.append(key, String(val).trim());
        }
    });
    const qs = search.toString();
    return qs ? `?${qs}` : "";
}

async function fetchConsulta(endpoint, params = {}) {
    const url = `${endpoint}${buildQueryString(params)}`;
    const response = await fetch(url, {
        headers: { Accept: "application/json" },
    });

    const contentType = response.headers.get("content-type") || "";
    if (!response.ok) {
        let msg = `Erro ${response.status} ao consultar dados.`;
        if (contentType.includes("application/json")) {
            const errData = await response.json().catch(() => null);
            if (errData && errData.erro) msg = errData.erro;
        }
        throw new Error(msg);
    }

    if (!contentType.includes("application/json")) {
        throw new Error("Sessão expirada ou resposta inválida. Faça login novamente.");
    }

    return response.json();
}

function renderTable(container, columns, rows, emptyMessage = "Nenhum registro encontrado para os filtros informados.") {
    if (!rows || rows.length === 0) {
        container.innerHTML = `<div class="state-box">${escapeHtml(emptyMessage)}</div>`;
        return;
    }

    const headersHtml = columns.map((col) => `<th>${escapeHtml(col.label)}</th>`).join("");
    const rowsHtml = rows
        .map((row) => {
            const cells = columns
                .map((col) => {
                    const raw = row[col.key];
                    const formatted = col.render ? col.render(raw, row) : escapeHtml(raw ?? "—");
                    return `<td>${formatted}</td>`;
                })
                .join("");
            return `<tr>${cells}</tr>`;
        })
        .join("");

    container.innerHTML = `
        <div class="table-wrapper">
            <table>
                <thead><tr>${headersHtml}</tr></thead>
                <tbody>${rowsHtml}</tbody>
            </table>
        </div>
    `;
}

function initDomainTabs(onTabActivate) {
    const buttons = document.querySelectorAll(".tab-btn[data-tab]");
    const panels = document.querySelectorAll(".domain-panel[data-panel]");

    function activate(tabId) {
        buttons.forEach((btn) => btn.classList.toggle("active", btn.dataset.tab === tabId));
        panels.forEach((panel) => panel.classList.toggle("active", panel.dataset.panel === tabId));
        if (typeof onTabActivate === "function") {
            onTabActivate(tabId);
        }
    }

    buttons.forEach((btn) => {
        btn.addEventListener("click", () => activate(btn.dataset.tab));
    });

    return { activate };
}

function setupDomainController({
    formId,
    endpoint,
    tableContainerId,
    countBadgeId,
    columns,
    getParams,
    onDataLoaded,
    presetsSelector,
    resetBtnId,
    onReset,
}) {
    const form = document.getElementById(formId);
    const tableContainer = document.getElementById(tableContainerId);
    const countBadge = document.getElementById(countBadgeId);
    let loadedOnce = false;

    async function run() {
        tableContainer.innerHTML = '<div class="state-box">Carregando consulta...</div>';
        try {
            const params = getParams(form);
            const payload = await fetchConsulta(endpoint, params);
            const dados = payload.dados || [];
            const total = payload.total ?? dados.length;

            if (countBadge) {
                countBadge.textContent = `${total} ${total === 1 ? "registro" : "registros"}`;
            }

            if (typeof onDataLoaded === "function") {
                onDataLoaded(dados, payload);
            }

            renderTable(tableContainer, columns, dados);
            loadedOnce = true;
        } catch (err) {
            if (countBadge) countBadge.textContent = "Erro";
            tableContainer.innerHTML = `<div class="state-box error">${escapeHtml(err.message)}</div>`;
        }
    }

    form.addEventListener("submit", (e) => {
        e.preventDefault();
        if (presetsSelector) {
            document.querySelectorAll(presetsSelector).forEach((b) => b.classList.remove("active"));
        }
        run();
    });

    if (resetBtnId) {
        const resetBtn = document.getElementById(resetBtnId);
        if (resetBtn) {
            resetBtn.addEventListener("click", () => {
                form.reset();
                if (presetsSelector) {
                    document.querySelectorAll(presetsSelector).forEach((b) => b.classList.remove("active"));
                }
                if (typeof onReset === "function") onReset(form);
                run();
            });
        }
    }

    if (presetsSelector) {
        const chips = document.querySelectorAll(presetsSelector);
        chips.forEach((chip) => {
            chip.addEventListener("click", () => {
                chips.forEach((b) => b.classList.remove("active"));
                chip.classList.add("active");
                form.reset();
                if (typeof onReset === "function") onReset(form);
                const presetData = JSON.parse(chip.dataset.preset || "{}");
                Object.entries(presetData).forEach(([name, value]) => {
                    const input = form.elements[name];
                    if (!input) return;
                    if (input.type === "checkbox") {
                        input.checked = Boolean(value);
                    } else {
                        input.value = value;
                    }
                });
                run();
            });
        });
    }

    return {
        run,
        ensureLoaded: () => {
            if (!loadedOnce) run();
        },
    };
}

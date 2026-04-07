document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("select[data-autosubmit]").forEach((element) => {
    element.addEventListener("change", () => {
      const form = document.getElementById("filters-form");
      if (form) {
        form.submit();
      }
    });
  });

  const previewPanel = document.getElementById("preview-panel");
  const previewBackdrop = document.getElementById("preview-backdrop");
  const previewTitle = document.getElementById("preview-title");
  const previewMeta = document.getElementById("preview-meta");
  const previewContent = document.getElementById("preview-content");
  const previewClose = document.getElementById("preview-close");
  const statusStatsData = document.getElementById("status-stats-data");
  const statusStats = statusStatsData ? JSON.parse(statusStatsData.textContent || "{}") : {};

  function escapeHtml(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");
  }

  function formatValue(value) {
    if (value === null || value === undefined || value === "") {
      return "—";
    }
    if (typeof value === "number") {
      return Number.isInteger(value) ? String(value) : value.toFixed(1);
    }
    return String(value);
  }

  function closePreview() {
    if (previewPanel && previewBackdrop) {
      previewPanel.classList.add("hidden");
      previewBackdrop.classList.add("hidden");
      document.body.classList.remove("modal-open");
    }
  }

  function openModal(title, meta, contentHtml) {
    if (!previewPanel || !previewTitle || !previewMeta || !previewContent) {
      return;
    }

    previewTitle.textContent = title;
    previewMeta.textContent = meta;
    previewContent.innerHTML = contentHtml;
    previewPanel.classList.remove("hidden");
    if (previewBackdrop) {
      previewBackdrop.classList.remove("hidden");
    }
    document.body.classList.add("modal-open");
    if (previewClose) {
      previewClose.focus();
    }
  }

  function openPreview(row) {
    const titleElement = row.querySelector("td strong");
    const metaElement = row.querySelector("td .meta");
    const templateElement = row.querySelector(".item-preview-template");

    if (!titleElement || !metaElement || !templateElement) {
      return;
    }

    openModal(titleElement.textContent || "Preview", metaElement.textContent || "", templateElement.innerHTML);
  }

  function renderMetrics(metrics) {
    if (!metrics || metrics.length === 0) {
      return "";
    }

    const metricHtml = metrics
      .map((metric) => `
        <div class="stat-metric">
          <span>${escapeHtml(metric.label)}</span>
          <strong>${escapeHtml(formatValue(metric.value))}</strong>
        </div>
      `)
      .join("");

    return `<div class="stat-grid">${metricHtml}</div>`;
  }

  function renderHighlight(highlight, fallbackLabel) {
    if (!highlight) {
      return "";
    }

    const label = highlight.label || fallbackLabel;
    const value = highlight.value ?? "—";
    const count = highlight.count !== undefined && highlight.count !== null ? ` (${escapeHtml(formatValue(highlight.count))})` : "";
    const metaParts = [];
    if (highlight.project) {
      metaParts.push(highlight.project);
    }
    if (highlight.source_path) {
      metaParts.push(`${highlight.source_path}:${highlight.source_line}`);
    }
    if (highlight.age_days !== undefined && highlight.age_days !== null) {
      metaParts.push(`approx. ${formatValue(highlight.age_days)} days old`);
    }

    return `
      <div class="stat-highlight">
        <div class="stat-highlight-label">${escapeHtml(label)}</div>
        <div class="stat-highlight-value">${escapeHtml(formatValue(value))}${count}</div>
        ${metaParts.length ? `<div class="stat-highlight-meta">${escapeHtml(metaParts.join(" | "))}</div>` : ""}
      </div>
    `;
  }

  function renderStatusStats(section) {
    const metrics = renderMetrics(section.metrics);
    const highlight = renderHighlight(section.highlight, "Top item");
    const note = section.note ? `<p class="stat-note">${escapeHtml(section.note)}</p>` : "";

    return `
      <div class="status-stats">
        ${metrics}
        ${highlight}
        ${note}
      </div>
    `;
  }

  function openStatusStats(statKey) {
    const section = statusStats[statKey];
    if (!section) {
      return;
    }

    const title = statKey === "closed" ? "Closed statistics" : statKey === "open" ? "Open statistics" : "In progress statistics";
    const meta = section.note || "Status summary for the current workspace.";
    openModal(title, meta, renderStatusStats(section));
  }

  document.querySelectorAll("tr.todo-row").forEach((row) => {
    row.addEventListener("click", () => openPreview(row));
    row.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        openPreview(row);
      }
    });
  });

  document.querySelectorAll("button.summary-card[data-stat-key]").forEach((button) => {
    button.addEventListener("click", () => {
      openStatusStats(button.dataset.statKey || "");
    });
  });

  if (previewClose) {
    previewClose.addEventListener("click", closePreview);
  }

  if (previewBackdrop) {
    previewBackdrop.addEventListener("click", closePreview);
  }

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      closePreview();
    }
  });
});

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

  function closePreview() {
    if (previewPanel && previewBackdrop) {
      previewPanel.classList.add("hidden");
      previewBackdrop.classList.add("hidden");
      document.body.classList.remove("modal-open");
    }
  }

  function openPreview(row) {
    const titleElement = row.querySelector("td strong");
    const metaElement = row.querySelector("td .meta");
    const templateElement = row.querySelector(".item-preview-template");

    if (!previewPanel || !previewTitle || !previewMeta || !previewContent || !titleElement || !metaElement || !templateElement) {
      return;
    }

    previewTitle.textContent = titleElement.textContent;
    previewMeta.textContent = metaElement.textContent;
    previewContent.innerHTML = templateElement.innerHTML;
    previewPanel.classList.remove("hidden");
    if (previewBackdrop) {
      previewBackdrop.classList.remove("hidden");
    }
    document.body.classList.add("modal-open");
    if (previewClose) {
      previewClose.focus();
    }
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

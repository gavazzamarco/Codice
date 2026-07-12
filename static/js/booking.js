document.addEventListener("click", function(event) {
    // 1. Gestione del click sul pulsante per aggiungere un compagno
    if (event.target.classList.contains("detail-add-companion")) {
        const sessionId=event.target.getAttribute("data-session-id");
        const container=document.querySelector(`#companion-container-${sessionId}`);
        
        if (container) {
            const newCompanion = document.createElement("div");
            newCompanion.classList.add("detail-companion-container");
            newCompanion.innerHTML = `
                <div class="p-1 mb-0">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <label class="logreg-label detail-modal-label mb-0">Companion (username):</label>
                        <button type="button" class="create-button-delete detail-delete">X</button>
                    </div>
                    <input type="text" name="companion" class="form-control logreg-input mb-4" required>
                </div>
            `;
            container.appendChild(newCompanion);
            if (container.children.length>=1) {
                event.target.parentElement.classList.add("d-none");
            }
        }
    }

    if (event.target.classList.contains("create-button-delete")) {
        const companionCard=event.target.closest(".detail-companion-container");
        if (companionCard) {
            const container=companionCard.parentElement;
            const sessionId=container.id.replace("companion-container-", "");
            const addButton=document.querySelector(`.detail-add-companion[data-session-id="${sessionId}"]`);
            companionCard.remove();
            if (container.children.length===0 && addButton) {
                addButton.classList.remove("d-none");
            }
        }
    }
});
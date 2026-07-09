const addCompanion=document.querySelector("#add-companion")
const container=document.querySelector("#companion-container")

addCompanion.addEventListener("click", function() {
    const newCompanion=document.createElement("div");
    newCompanion.classList.add("detail-companion-container");
    newCompanion.innerHTML=`
        <div class="col-9">
            <label>Companion:*<label>
            <input type="text" name="companion" class="form-control" required>
        </div>
        <div class="col-3 create-button-delete-container justify-content-center m-0"">
            <button type="button" class="create-button-delete delete-role-btn">X</button>
        </div>
    `;
    container.appendChild(newCompanion);
});

container.addEventListener("click", function(event) {
    if (event.target.classList.contains("create-button-delete")) {
        // Trova il genitore più vicino con la classe 'create-session-card' e rimuovilo dal DOM
        event.target.closest(".detail-companion-container").remove();
    }
});
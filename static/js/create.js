const addSession = document.querySelector("#add-session");
const container = document.querySelector("#session-container");

addSession.addEventListener("click", function () {
    const newSession = document.createElement("div");
    newSession.classList.add("create-session-card", "row", "position-relative", "mt-3");
    newSession.innerHTML = `
        <div class="col-5">
            <label>Day*</label>
            <select name="day" class="form-control" required>
                <option value="">Select a day</option>
                <option value="1">Monday</option>
                <option value="2">Tuesday</option>
            </select>
        </div>
        <div class="col-5">
            <label>Start*</label>
            <input type="text" name="start" class="form-control" required>
        </div>
        <div class="col-2 create-button-delete-container">
            <button type="button" class="create-button-delete">X</button>
        </div>
    `;
    container.appendChild(newSession);
});

container.addEventListener("click", function (event) {
    if (event.target.classList.contains("create-button-delete")) {
        // Trova il genitore più vicino con la classe 'create-session-card' e rimuovilo dal DOM
        event.target.closest(".create-session-card").remove();
    }
});
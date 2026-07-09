const addSession=document.querySelector("#add-session");
const container=document.querySelector("#session-container");
const DAYS_OF_WEEK=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

addSession.addEventListener("click", function() {
    const newSession=document.createElement("div");
    newSession.classList.add("create-session-card", "row", "mt-3");
    newSession.innerHTML=`
        <div class="col-4">
            <label>Day*</label>
            <select name="day" class="form-control" required>
                <option value="">Select a day</option>
            </select>
        </div>
        <div class="col-3">
            <label for="hour">Hour*</label>
            <input type="number" id="hour" name="hour" class="form-control" placeholder="0-24" required>
        </div>
        <div class="col-3">
            <label for="minute">Minute*</label>
            <input type="number" id="minute" name="minute" class="form-control" placeholder="0-60" required>
        </div>
        <div class="col-2 create-button-delete-container">
            <button type="button" class="create-button-delete">X</button>
        </div>`;

    const select=newSession.querySelector("select");
    DAYS_OF_WEEK.forEach((day) => {
        const option=document.createElement("option");
        option.value=day;
        option.textContent=day;
        select.appendChild(option);
    });
    container.appendChild(newSession);
});

container.addEventListener("click", function(event) {
    if (event.target.classList.contains("create-button-delete")) {
        // Trova il genitore più vicino con la classe 'create-session-card' e rimuovilo dal DOM
        event.target.closest(".create-session-card").remove();
    }
});
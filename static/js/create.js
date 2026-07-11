const addSession=document.querySelector("#add-session");
const container=document.querySelector("#session-container");
const DAYS_OF_WEEK=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

addSession.addEventListener("click", function() {
    const newSession=document.createElement("div");
    newSession.classList.add("create-session-card", "row", "mt-3");
    newSession.innerHTML=`
        <div class="col-4">
            <label class="logreg-label" for="day">Day*</label>
            <select id="day" name="day" class="form-control logreg-input mb-4" required>
                <option value="">Select a day</option>
                {% for day in days %}
                <option value="{{ day }}">{{ day }}</option>
                {% endfor %}
            </select>
        </div>
        <div class="col-3">
            <label class="logreg-label" for="hour">Hour*</label>
            <input type="number" id="hour" name="hour" class="form-control logreg-input mb-4" placeholder="0-23" required>
        </div>
        <div class="col-3">
            <label class="logreg-label" for="minute">Minute*</label>
            <input type="number" id="minute" name="minute" class="form-control logreg-input mb-4" placeholder="0-59" required>
        </div>
        <div class="col-2 d-flex justify-content-end align-items-center my-3">
            <button type="button" class="create-button-delete">X</button>
        </div>
        `;

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
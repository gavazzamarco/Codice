const addSession=document.querySelector("#add-session");
const container=document.querySelector("#session-container");
addSession.addEventListener("click", function() {
    const newSession=document.createElement("div");
    newSession.classList.add("dark-box-grey-border", "row", "d-flex", "justify-content-center", "p-2");
    newSession.innerHTML=`
        <div class="col-4">
            <label class="logreg-label" for="day">Day*</label>
            <select id="day" name="day" class="form-control text-serif-bold mb-4" required>
                <option value="">Select a day</option>
                <option value="Monday">Monday</option>
                <option value="Tuesday">Tuesday</option>
                <option value="Wednesday">Wednesday</option>
                <option value="Thursday">Thursday</option>
                <option value="Friday">Friday</option>
                <option value="Saturday">Saturday</option>
                <option value="Sunday">Sunday</option>
            </select>
        </div>
        <div class="col-3">
            <label class="logreg-label" for="hour">Hour*</label>
            <input type="number" id="hour" name="hour" class="form-control text-serif-bold mb-4" placeholder="0-23" min="0" max="23" required>
        </div>
        <div class="col-3">
            <label class="logreg-label" for="minute">Minute*</label>
            <input type="number" id="minute" name="minute" class="form-control text-serif-bold mb-4" placeholder="0-59" min="0" max="59" required>
        </div>
        <div class="col-2 d-flex justify-content-end align-items-center my-3">
            <button type="button" class="create-button-delete">X</button>
        </div>
        <div class="col-9">
            <label class="logreg-label" for="location">Location*</label>
            <select id="location" name="location" class="form-control text-serif-bold mb-4" required>
                <option value="">Select a location</option>
                <option value="Axel">Axel</option>
                <option value="Kingdom of Elroad">Kingdom of Elroad</option>
                <option value="Arcanletia">Arcanletia</option>
            </select>
        </div>`;
    container.appendChild(newSession);
});
container.addEventListener("click", function(event) {
    if (event.target.classList.contains("create-button-delete")) {
        event.target.closest(".dark-box-grey-border").remove();
    }
});
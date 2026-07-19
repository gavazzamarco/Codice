// Puntatore all'elemento html che nel file quest_create.html ha come
// id="add-session" (cioè il bottone per aggiungere una sessione)
const addSession=document.querySelector("#add-session");

// Puntatore all'elemento html che nel file quest_create.html ha come
// id="session-container" (cioè di fatto il div che funge da contenitore
// per tutte le form di creazione di una nuova sessione)
const container=document.querySelector("#session-container");

// mi metto in ascolto per azioni di tipo click che coinvolgono
// l'elemento addSession (cioè il bottone per inserire una nuova sessione)
addSession.addEventListener("click", function() {
    // Creo un elemento html di tipo div ed assegno il puntatore a
    // tale elemento alla variabile newSession
    const newSession=document.createElement("div");
    // all'elemento div appena creato assegno tali classi
    newSession.classList.add("dark-box-grey-border", "row", "d-flex", "justify-content-center", "p-2");
    // All'interno dell'elemento div appena creato inserisco il seguente html che
    // è di fatto il codice html necessario per avere le varie form per creare
    // una nuova sessione (quindi la select del giorno, input di ora e minuti e
    // la select per il luogo)
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
    // Dopodiché inserisco l'elemento appena creato al fondo del contenitore 
    // puntato dalla variabile "container", che è appunto l'elemento div
    // che funge da contenitore per le form di creazione di tutte le sessioni
    container.appendChild(newSession);
});

// Mi metto in ascolto per azioni di tipo click che coninvolgono
// il contenitore di tutte le form per la creazione delle sessioni
container.addEventListener("click", function(event) {
    // Se tale elemento clickato possiede la classe "create-button-delete"
    // singifica che ho schiacciato la x per eliminare una certa "sessione"
    if (event.target.classList.contains("create-button-delete")) {
        // Elimino quindi dal dom il contenitore (e tutto il suo contenuto)
        // dell'elemento html più vicino a lui nel dom che possiede la classe
        // "dark-box-grey-border", ossia il contenitore delle form per la singola sessione
        event.target.closest(".dark-box-grey-border").remove();
    }
});
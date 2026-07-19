document.addEventListener("click", function(event) {
    // Quando avviene un azione di tipo "click" controllo se l'elemento
    // clickato possiede la classe "detail-add-companion". 
    // Se lo contiene allora entro nel corpo dell'if
    if (event.target.classList.contains("detail-add-companion")) {
        // Poi, siccome ho tanti modal quante sono le sessioni, devo andare ad
        // individuare il modal corretto al quale andare ad aggiungere il campo
        // per inserire il nuovo compagno. Siccome l'id del div in cui comparirà
        // la form per il nuovo compagno ha un id del tipo: 
        //        <div id="companion-container-{{ session.id }}"></div>
        // devo andare a recuperare il valore del session-id, che è contenuto
        // nel caso data-session-id del bottone premuto, infatti:
        // <button type="button" class="common-button button-blue text-size-19 detail-add-companion" data-session-id="{{ session.id }}">Add a companion</button>
        const sessionId=event.target.getAttribute("data-session-id");

        // Ottenuto l'id della sessione sono in grado di determinare univocamente
        // l'id del contenitore in cui comparirà la form per inserire l'accompagnatore
        const container=document.querySelector(`#companion-container-${sessionId}`);
        if (container) {
            // Creo un nuovo elemento div e assegno
            // il puntatore a tale elemento alla variabile "newCompanion"
            const newCompanion=document.createElement("div");
            // Assegno al div appena creato la classe "detail-companion-container"
            newCompanion.classList.add("detail-companion-container");
            // All'interno del div appena creato inserisco il seguente codice html
            // che è quello che fa comparire i campi form (label e input) per
            // inserire l'accompagnatore + il bottone per togliere tale form appena inserita
            newCompanion.innerHTML=`
                <div class="p-1 mb-0">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <label class="logreg-label detail-modal-label mb-0">Companion (username):</label>
                        <button type="button" class="create-button-delete detail-delete">X</button>
                    </div>
                    <input type="text" name="companion" class="form-control logreg-input mb-4" required>
                </div>`;

            // Inserisco al fondo del contenitore <div id="companion-container-{{ session.id }}"></div>
            // l'elemento html appena creato
            container.appendChild(newCompanion);
            // Se tale contenitore contiene 1 o più "elementi html che sono
            // dei figli diretti" allora faccio scomparire il bottone per aggiungere
            // un nuovo compagno tanto ogni avventuriero può al massimo portare
            // con sè un avventuriero
            if (container.children.length>=1) {
                event.target.parentElement.classList.add("d-none");
            }
        }
    }
    // Se l'azione di click ha invece coinvolto un elemento html con la classe
    // "create-button-delete", allora individuo l'elemento ad esso più
    // vicino nella risalita del dom che possiede la classe detail-companion-container
    // e rimuovo tale elemento appena individuato (che è di fatto l'elemento html
    // che fa da container per il form di inserimento dell'accompagnatore).
    // L'elemento con la classe "detail-companion-container" viene creata SOLO
    // all'interno di tale file js, quando si preme sul bottone di add-companion
    // [vedere riga 24 di questo file]
    if (event.target.classList.contains("create-button-delete")) {
        const companionCard=event.target.closest(".detail-companion-container");
        if (companionCard) {
            companionCard.remove();
        }
    }
});
// Funktio, joka näyttää oikeat huoltotehtävät valitun vuodenaika mukaan
function showSeasonTasks() {
    // Piilottaa kaikki huoltotehtävät
    var tasks = document.querySelectorAll('.season-tasks');
    tasks.forEach(function(task) {
        task.style.display = 'none';
    });

    // Haetaan valittu vuodenaika
    var selectedSeason = document.getElementById('season-select').value;

    // Näytetään valitun vuodenaika huoltotehtävät
    document.getElementById(selectedSeason).style.display = 'block';
}

// Funktio, joka asettaa vuodenaikatehtävät automaattisesti
function setDefaultSeason() {
    var currentMonth = new Date().getMonth() + 1; // Hakee kuukauden (0-11), lisätään 1
    var defaultSeason;

    // Määritellään vuodenaika kuukauden perusteella
    if (currentMonth >= 12 || currentMonth <= 2) {
        defaultSeason = 'talvi';  // Talvi (joulu, tammikuu, helmikuu)
    } else if (currentMonth >= 3 && currentMonth <= 5) {
        defaultSeason = 'kevat';  // Kevät (maaliskuu, huhtikuu, toukokuu)
    } else if (currentMonth >= 6 && currentMonth <= 8) {
        defaultSeason = 'kesa';   // Kesä (kesä, heinä, elokuu)
    } else {
        defaultSeason = 'syksy';  // Syksy (syys, loka, marraskuu)
    }

    // Asetetaan valittu vuodenaika ja näytetään sen huoltotehtävät
    document.getElementById('season-select').value = defaultSeason;
    showSeasonTasks();
}

// Alustetaan näkymään oikea vuodenaika sen mukaan, mikä kuukausi on
window.onload = setDefaultSeason;
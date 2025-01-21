//Dashboardin sidebarin toggler
const toggler = document.getElementById('asideToggler');
const aside = document.getElementById('dashboardSidebar');
const togglerIcon = toggler.querySelector('i');
const contentDashboard  = document.getElementById('dashboardContent');

  // Tarkistetaan, onko käyttäjä piilottanut aside aikaisemmin
  if (localStorage.getItem('asideHidden') === 'true') {
    aside.classList.add('dashboardnav-hidden');
    toggler.querySelector('i').className = 'fa-solid fa-angles-right';
    dashboardContent.classList.add('dashboard-full-width');
  }

toggler.addEventListener('click', () => {
    const isHidden = aside.classList.toggle('dashboardnav-hidden'); 
    //aside.classList.toggle('dashboardnav-hidden');

    if (togglerIcon.classList.contains('fa-angles-left')) {
        togglerIcon.classList.replace('fa-angles-left', 'fa-angles-right');
    } else {
        togglerIcon.classList.replace('fa-angles-right', 'fa-angles-left');
    }

    contentDashboard.classList.toggle('dashboard-full-width');

    // Tallennetaan tila localStorageen
    localStorage.setItem('asideHidden', isHidden);
});
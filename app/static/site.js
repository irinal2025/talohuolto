document.addEventListener("DOMContentLoaded", function() {
  // Lisää aktiivisen navigointilinkin osoittaminen
  document.querySelectorAll("nav a, ul.nav a").forEach((link) => {
    const url = link.href;
    const hash = url.split('#')[1];

    if (link.pathname === window.location.pathname) {
      if (!hash) {
        link.classList.add("active");
        link.setAttribute("aria-current", "page");
      }
    }
  });

  // Scroll to top button functionality
  const myBackToTopButton = document.getElementById("backToTopBtn");
  if (myBackToTopButton) {
    myBackToTopButton.addEventListener("click", function() {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  // Close alert button functionality
  document.querySelectorAll('.alert .close').forEach(function(button) {
    button.addEventListener('click', function() {
      const alert = button.closest('.alert');
      alert.style.display = 'none';
    });
  });

  // Navbar-toggler functionality
  const toggler = document.querySelector('.navbar-toggler');
  const icon = document.querySelector('.navbar-toggler-icon');
  if (toggler && icon) {
    toggler.addEventListener('click', function() {
      icon.classList.toggle('th-navbar-toggled');
    });
  }
});


//Dashboardin sidebarin toggler
const toggler = document.getElementById('asideToggler');
const aside = document.getElementById('dashboardSidebar');
const togglerIcon = toggler.querySelector('i');
const contentDashboard  = document.getElementById('dashboardContent');

  // Tarkistetaan, onko käyttäjä piilottanut aside aikaisemmin
  if (localStorage.getItem('asideHidden') === 'true') {
    aside.classList.add('dashboardnav-hidden');
    toggler.querySelector('i').className = 'fa-solid fa-angles-right';
    dashboardContent.classList.add('full-width');
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
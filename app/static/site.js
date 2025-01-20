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






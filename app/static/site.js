


//Lisää aktiivisen navigointilinkin osoittaminen Javascriptillä ja CSS:llä:
document.addEventListener("DOMContentLoaded", function() {
    document.querySelectorAll("nav a, ul.nav a").forEach((link) => {
        //if (link.href === window.location.href) 
        var url = (link.href),
            hash = url.split('#')[1];
        if (link.pathname === window.location.pathname) {
            if (hash) {
                //alert(hash)
            } else {
                link.classList.add("active");
                link.setAttribute("aria-current", "page");
            }

        }
    });
  });


// When the user clicks on the button, scroll to the top of the document
const myBackToTopButton = document.getElementById("backToTopBtn");

myBackToTopButton.addEventListener("click", function() {
  document.body.scrollTop = 0; // For Safari
  document.documentElement.scrollTop = 0; // For Chrome, Firefox, IE and Opera
});

document.addEventListener('DOMContentLoaded', function () {
    const closeButtons = document.querySelectorAll('.alert .close');
    closeButtons.forEach(function (button) {
      button.addEventListener('click', function () {
        const alert = button.closest('.alert');
        alert.style.display = 'none';
      });
    });
 });
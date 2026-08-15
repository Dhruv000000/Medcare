// ===============================
// MediCare Landing Page Script
// ===============================

// Wait until HTML is loaded
document.addEventListener("DOMContentLoaded", function () {

    // ===============================
    // DARK MODE
    // ===============================

    const themeBtn = document.getElementById("themeBtn");

    if (themeBtn) {

        themeBtn.addEventListener("click", function () {

            document.body.classList.toggle("dark");

            const icon = this.querySelector("i");

            if (document.body.classList.contains("dark")) {
                icon.classList.remove("fa-moon");
                icon.classList.add("fa-sun");
            } else {
                icon.classList.remove("fa-sun");
                icon.classList.add("fa-moon");
            }

        });

    }

    // ===============================
    // SMOOTH SCROLL
    // ===============================

    document.querySelectorAll('a[href^="#"]').forEach(link => {

        link.addEventListener("click", function (e) {

            const target = document.querySelector(this.getAttribute("href"));

            if (target) {

                e.preventDefault();

                target.scrollIntoView({
                    behavior: "smooth"
                });

            }

        });

    });

    // ===============================
    // SCROLL REVEAL
    // ===============================

    const revealElements = document.querySelectorAll(".reveal");

    function reveal() {

        revealElements.forEach((element) => {

            const windowHeight = window.innerHeight;

            const elementTop = element.getBoundingClientRect().top;

            if (elementTop < windowHeight - 100) {

                element.classList.add("active");

            }

        });

    }

    window.addEventListener("scroll", reveal);

    reveal();

});

// ===============================
// STICKY NAVBAR
// ===============================

window.addEventListener("scroll", function () {

    const navbar = document.querySelector(".navbar");

    if (!navbar) return;

    if (window.scrollY > 50) {

        navbar.style.background = "rgba(255,255,255,0.95)";
        navbar.style.boxShadow = "0 10px 25px rgba(0,0,0,.15)";

        if (document.body.classList.contains("dark")) {

            navbar.style.background = "rgba(17,24,39,.95)";

        }

    }

    else {

        if (document.body.classList.contains("dark")) {

            navbar.style.background = "rgba(17,24,39,.90)";

        }

        else {

            navbar.style.background = "rgba(255,255,255,.35)";

        }

        navbar.style.boxShadow = "0 10px 30px rgba(0,0,0,.08)";

    }

});

// ===============================
// HERO ANIMATION
// ===============================

window.addEventListener("load", function () {

    const left = document.querySelector(".hero-left");
    const right = document.querySelector(".hero-right");

    if (left) {

        left.style.opacity = "0";
        left.style.transform = "translateX(-70px)";
        left.style.transition = "1s";

    }

    if (right) {

        right.style.opacity = "0";
        right.style.transform = "translateX(70px)";
        right.style.transition = "1s";

    }

    setTimeout(() => {

        if (left) {

            left.style.opacity = "1";
            left.style.transform = "translateX(0)";

        }

        if (right) {

            right.style.opacity = "1";
            right.style.transform = "translateX(0)";

        }

    }, 200);

});
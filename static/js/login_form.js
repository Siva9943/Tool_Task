document.addEventListener("DOMContentLoaded", function () {

    const form = document.getElementById("login_form");

    form.addEventListener("submit", function (e) {

        const email = document.querySelector('input[name="email"]');
        const password = document.querySelector('input[name="password"]');

        // Remove previous validation messages
        document.querySelectorAll(".text-danger.validation-error").forEach(el => el.remove());

        let isValid = true;

        // Email validation
        if (email.value.trim() === "") {
            showError(email, "Email is required.");
            isValid = false;
        } else if (!validateEmail(email.value.trim())) {
            showError(email, "Enter a valid email address.");
            isValid = false;
        }

        // Password validation
        if (password.value.trim() === "") {
            showError(password, "Password is required.");
            isValid = false;
        }

        if (!isValid) {
            e.preventDefault();
        }

    });

    function showError(input, message) {
        const error = document.createElement("div");
        error.className = "text-danger validation-error mt-1";
        error.innerText = message;
        input.parentElement.appendChild(error);
    }

    function validateEmail(email) {
        const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return regex.test(email);
    }

});
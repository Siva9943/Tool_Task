console.log("JavaScript loaded");
document.addEventListener("DOMContentLoaded", function () {

    const form = document.getElementById("signup_info");

    form.addEventListener("submit", function (e) {
            console.log("JavaScript loaded676");
        
        document.querySelectorAll(".validation-error").forEach(el => el.remove());

        let isValid = true;

        const fullName = document.getElementById("staticName");
        const email = document.getElementById("staticEmail");
        const password1 = document.getElementById("inputPassword1");
        const password2 = document.getElementById("inputPassword");

        // Full Name
        const fullNameValue = fullName.value.trim();
        const namePattern = /^[A-Za-z ]+$/;
        if (fullNameValue === "") {
            showError(fullName, "Full name is required.");
            isValid = false;
        } else if (!namePattern.test(fullNameValue)) {
            showError(fullName, "Full name can contain only letters and spaces.");
            isValid = false;
        }

        const allowedDomains = ["ineesconsulting.com", "gmail.com"];
        const emailValue = email.value.trim().toLowerCase();
        const domain = emailValue.split("@")[1];

        if (emailValue === "") {
            showError(email, "Email is required.");
            isValid = false;
        } else if (!allowedDomains.includes(domain)) {
            showError(email, "Only @ineesconsulting.com or @gmail.com allowed.");
            isValid = false;
        }

        // Password
        if (password1.value.trim() === "") {
            showError(password1, "Password is required.");
            isValid = false;
        } else if (password1.value.length < 8) {
            showError(password1, "Password must be at least 8 characters.");
            isValid = false;
        }

        // Confirm Password
        if (password2.value.trim() === "") {
            showError(password2, "Confirm password is required.");
            isValid = false;
        } else if (password1.value !== password2.value) {
            showError(password2, "Passwords do not match.");
            isValid = false;
        }

       
        if (!isValid) {
            e.preventDefault();
        }

    });

    function showError(input, message) {
        const error = document.createElement("div");
        error.className = "text-danger mt-1 validation-error";
        error.innerText = message;
        input.parentElement.appendChild(error);
    }

});
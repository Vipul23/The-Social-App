var checksame = function () {
    if (
        document.getElementById("password").value !=
        document.getElementById("password2").value
    ) {
        document.getElementById("message").style.color = "red";
        document.getElementById("message").innerHTML = "Passwords do not match";
        document.getElementById("submit").disabled = true;
    }

};

var validate = function () {
    var pswel = document.getElementById("password");
    var pswel2 = document.getElementById("password2");

    var check = 1;

    if (pswel.value != pswel2.value) {
        document.getElementById("message").style.color = "red";
        document.getElementById("message").innerHTML = "Passwords do not match";
        document.getElementById("submit").disabled = true;
        check = 0;
    }

    // Check if password is between 8 and 16 characters
    if (pswel.value.length < 8 || pswel.value.length > 15) {
        document.getElementById("message").style.color = "red";
        document.getElementById("message").innerHTML = "Passwords must be between 8 and 15 characters<br>";
        document.getElementById("submit").disabled = true;
        check = 0;
    }

    // Check if password contains at least one lowercase letter, uppercase letter, number, and special character
    const regex = /^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[^a-zA-Z0-9])(?!.*\s).*$/;
    if (!regex.test(pswel.value)) {
        document.getElementById("message").style.color = "red";
        document.getElementById("message").innerHTML = "Passwords does not contain at least one lowercase letter,<br> &nbsp&nbsp one uppercase letter, one numeric digit, <br>&nbsp&nbsp and one special character ";
        document.getElementById("submit").disabled = true;
        check = 0
    }

    if (check == 1) {
        document.getElementById("message").innerHTML = "";
        document.getElementById("submit").disabled = false;
    }
};
/*
 * Module containing functions relating to the team hope registration page
 *
 */

function previewImage(event) {
    let reader = new FileReader();
    reader.onload = function () {
        let output = document.getElementById('profile-picture-preview');
        output.src = reader.result;
        output.style.display = 'block';
    }
    reader.readAsDataURL(event.target.files[0]);
}

document.addEventListener("DOMContentLoaded", function () {
    const roleSelect = document.getElementById("id_teamhope_member_role");
    const takeTheCourseDiv = document.getElementById("take_the_course");
    const communicationDiv = document.querySelector("#communication-div");
    const togglePhoneInput = document.querySelector("#id_communication_method_0") ?? null;
    const uoaaTakenCheckbox = document.getElementById("id_uoaa_taken");
    const registerForm = document.querySelector("#team-hope-register-form");
    if (togglePhoneInput !== null) {
        togglePhoneInput.addEventListener("change", (evt) => {
            // Check if the phone number input is displayed
            let phoneInputDiv = document.querySelector("#phone-input-div") ?? null;
            const phoneInputParent = document.querySelector("#id_communication_method");
            if (phoneInputDiv === null) {
                // The phone element does not exist, create it
                phoneInputDiv = createInputElement();
                const phoneCheckBox = phoneInputParent.children[1];
                phoneInputParent.insertBefore(phoneInputDiv, phoneCheckBox);

            } else {
                // Remove the child element
                phoneInputParent.removeChild(phoneInputDiv);
            }

        });
    }


    function createInputElement() {
        const divElement = document.createElement("div");
        divElement.setAttribute("id", "phone-input-div");
        divElement.setAttribute("class", "col-md-4");
        const inputElement = Object.assign(document.createElement("input"), {
            id: "phone-input", className: "form-control  m-3", type: "tel", name: "phone-number"
        });
        // create a help text for the input element
        const helpText = Object.assign(document.createElement("small"), {
            id: "phone-help-text",
            className: "form-text m-3",
            innerText: "Invalid Phone Number.",
            style: "color:red;display:none;"
        });

        divElement.appendChild(inputElement);
        divElement.appendChild(helpText);
        return divElement;
    }

    function toggleTakeTheCourse() {
        takeTheCourseDiv.style.display = "none";
        uoaaTakenCheckbox.required = false;
        if (roleSelect.value === "Volunteer") {
            takeTheCourseDiv.style.display = "block";
            uoaaTakenCheckbox.required = true;
        }

    }

    registerForm.addEventListener("submit", (evt) => {
        evt.preventDefault();
        const phoneInput = document.querySelector("#phone-input") ?? null;
        const phoneRegex = /^\+?\d{9,15}$/;
        const phoneHelpText = document.querySelector("#phone-help-text");
        if (phoneInput) {
            if (!phoneRegex.test(phoneInput.value.trim())) {
                phoneHelpText.style.display = "block";
                phoneInput.focus();
                return false
            }
        }
        registerForm.submit();

    });


    function toggleMethodOfCommunication() {
        communicationDiv.classList.add("d-none");
        if (roleSelect.value === "Participant") {
            communicationDiv.classList.remove("d-none");
        }
    }

    // Set initial state on page load
    toggleTakeTheCourse();
    toggleMethodOfCommunication();

    // Update whenever the selected option changes
    roleSelect.addEventListener("change", toggleMethodOfCommunication);
});
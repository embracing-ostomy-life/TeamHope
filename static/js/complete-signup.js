(() => {
    const akDiv = document.querySelector("#ak-choice");
    const thDiv = document.querySelector("#th-choice");
    const form = document.querySelector("#complete-form");
    let hiddenInput = document.querySelector("#hidden-sub");


    akDiv.addEventListener("click", e => {
        akDiv.style.backgroundColor = "#bfe89f";
        thDiv.style.backgroundColor = "#ffffff";
        hiddenInput.value = "alive_and_kicking";
    });

    thDiv.addEventListener("click", e => {
        thDiv.style.backgroundColor = "#bfe89f";
        akDiv.style.backgroundColor = "#ffffff";
        hiddenInput.value = "team_hope";

    });

    form.addEventListener("submit", e => {
        e.preventDefault();
        if (!hiddenInput.value) {
            return false;
        }

        form.submit();
    });
})();
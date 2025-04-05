document.addEventListener("DOMContentLoaded", function () {
    function updateTime() {
        let now = new Date();
        let formattedTime = now.toLocaleString();
        document.getElementById("current-time").textContent = formattedTime;
    }

    let timeContainer = document.createElement("div");
    timeContainer.id = "current-time";
    timeContainer.style.fontSize = "16px";
    timeContainer.style.fontWeight = "bold";
    timeContainer.style.padding = "10px";
    document.body.prepend(timeContainer);

    updateTime();
    setInterval(updateTime, 1000); // Update every second
});

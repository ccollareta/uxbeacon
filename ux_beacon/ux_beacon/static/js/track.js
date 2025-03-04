document.addEventListener("click", function(event) {
    fetch("http://127.0.0.1:8000/api/heatmap/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            x: event.pageX,
            y: event.pageY,
            timestamp: new Date().toISOString(),
            user_id: new URLSearchParams(window.location.search).get('user_id')
        })
    });
});

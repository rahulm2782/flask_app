
<script>
function startTimer() {
    var timeLeft = 20; // set the timer length in seconds
    var timer = setInterval(function() {
        document.getElementById("timer").innerHTML = timeLeft + " seconds left";
        timeLeft--;
        if (timeLeft < 0) {
            clearInterval(timer);
            document.getElementById("timer").innerHTML = "Time's up!";
        }
    }, 1000); // update the timer every second
}
</script>
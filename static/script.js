document.addEventListener("DOMContentLoaded", function() {
  const text = "TRACK.";
  let index = 0;
  const speed = 200; // milliseconds per character
  const deleteSpeed = 100; // milliseconds per character for delete
  const pauseTime = 1000; // pause before repeating

  function typeWriter() {
    if (index < text.length) {
      document.getElementById("logo").textContent += text.charAt(index);
      index++;
      setTimeout(typeWriter, speed);
    } else {
      // Text is fully typed, pause then delete
      setTimeout(deleteText, pauseTime);
    }
  }

  function deleteText() {
    const element = document.getElementById("logo");
    if (element.textContent.length > 0) {
      element.textContent = element.textContent.slice(0, -1);
      setTimeout(deleteText, deleteSpeed);
    } else {
      // Text is fully deleted, restart typing
      index = 0;
      setTimeout(typeWriter, 500);
    }
  }

  window.onload = typeWriter;
  }); 
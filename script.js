document.querySelectorAll('.download-buttons a').forEach(button => {
    button.addEventListener('click', () => {
        alert('Thank you for downloading!');
    });
});

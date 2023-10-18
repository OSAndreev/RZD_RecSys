let seats = document.querySelectorAll('.seat');
let popupBg = document.querySelector('.info__bg');
let popup__photo = document.querySelector('.info__photo');
let popup__title = document.querySelector('.info__title');
let popup__text = document.querySelector('.info__text');
let tooltip = document.querySelector('.tooltip');

seats.forEach((item) => {
    item.addEventListener('click', function() {
        popup__title.textContent = this.getAttribute('data-title');
        popup__photo.setAttribute('src', this.getAttribute('data-photo'));
        popup__text.textContent = this.getAttribute('data-description'); // Changed to data-description
        popupBg.classList.add('active');
    });

    item.addEventListener('mouseenter', function() {
        tooltip.textContent = item.getAttribute('data-title');
        tooltip.style.display = 'block';
    });

    item.addEventListener('mouseleave', function() {
        tooltip.style.display = 'none'; // Hide tooltip on mouseleave
    });

    item.addEventListener('mousemove', function(e) {
        tooltip.style.top = (e.pageY + 20) + 'px'; // Changed to e.pageY
        tooltip.style.left = (e.pageX + 20) + 'px'; // Changed to e.pageX
    });
});

document.addEventListener('click', (e) => {
    if (e.target === popupBg) {
        popupBg.classList.remove('active');
    }
});

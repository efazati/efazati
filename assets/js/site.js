// The mobile menu. It closes on a tap anywhere outside it, on Escape and on
// following one of its links. The previous menu was a checkbox styled as a
// hamburger: CSS alone cannot see a tap elsewhere on the page, so once open it
// stayed open until you found the hamburger again.
(function () {
    document.documentElement.classList.add('js');
    var nav = document.querySelector('.nav');
    var btn = document.querySelector('.menu-btn');
    if (!nav || !btn) return;

    function setOpen(open) {
        nav.classList.toggle('open', open);
        btn.setAttribute('aria-expanded', open ? 'true' : 'false');
        btn.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    }

    btn.addEventListener('click', function (e) {
        e.stopPropagation();
        setOpen(!nav.classList.contains('open'));
    });

    // pointerdown rather than click: iOS Safari sends no click for a tap on
    // a non-interactive element, which is exactly where people tap to dismiss.
    document.addEventListener('pointerdown', function (e) {
        if (nav.classList.contains('open') && !nav.contains(e.target)) setOpen(false);
    });

    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && nav.classList.contains('open')) { setOpen(false); btn.focus(); }
    });

    nav.querySelectorAll('.nav-links a').forEach(function (a) {
        a.addEventListener('click', function () { setOpen(false); });
    });

    // Rotating to a wide screen leaves no hamburger to close it with.
    window.matchMedia('(min-width: 821px)').addEventListener('change', function (m) {
        if (m.matches) setOpen(false);
    });
})();

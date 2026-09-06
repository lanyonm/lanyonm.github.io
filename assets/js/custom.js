(function () {
  'use strict';

  var header = document.querySelector('header.site-header');
  var heroBg = document.querySelector('.hero-bg, .article-hero-bg');
  var hero = document.querySelector('.hero, .article-hero');

  var hasHero = !!hero;
  if (hasHero && header) {
    header.classList.add('over-hero');
    document.body.classList.add('has-hero');
  }

  var scrolledPast = 40;
  var heroHeight = hero ? hero.offsetHeight : 0;
  var fadeEnd = heroHeight * 0.7;

  function onScroll() {
    var y = window.scrollY || window.pageYOffset;

    if (header) {
      if (y > scrolledPast) {
        header.classList.add('scrolled');
        if (hasHero) header.classList.remove('over-hero');
      } else {
        header.classList.remove('scrolled');
        if (hasHero) header.classList.add('over-hero');
      }
    }

    if (heroBg && fadeEnd > 0) {
      var op = Math.max(0, 1 - y / fadeEnd);
      heroBg.style.opacity = op;
    }
  }

  // Throttled via setTimeout rather than requestAnimationFrame: rAF delivery
  // isn't guaranteed under browser power-saving throttling (e.g. Chrome's
  // Energy Saver mode can suspend rAF callbacks entirely with no error),
  // which can permanently wedge a ticking-flag-guarded rAF scheduler.
  // setTimeout doesn't carry that same risk.
  var scrollThrottled = false;
  window.addEventListener('scroll', function () {
    if (!scrollThrottled) {
      scrollThrottled = true;
      setTimeout(function () {
        scrollThrottled = false;
        onScroll();
      }, 100);
    }
  }, { passive: true });

  // Recompute hero height on resize
  window.addEventListener('resize', function () {
    if (hero) {
      heroHeight = hero.offsetHeight;
      fadeEnd = heroHeight * 0.7;
    }
  });

  // Helper for Congo's checkbox-based menu (called from menu link onclick or close label)
  window.close_menu = function () {
    var ctrl = document.getElementById('menu-controller');
    if (ctrl) ctrl.checked = false;
    var label = document.querySelector('.hamburger-label');
    if (label) label.setAttribute('aria-expanded', 'false');
  };

  // Escape key closes the menu
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      window.close_menu();
    }
  });

  // Mirror the checkbox state into aria-expanded
  var menuController = document.getElementById('menu-controller');
  if (menuController) {
    menuController.addEventListener('change', function () {
      var label = document.querySelector('.hamburger-label');
      if (label) label.setAttribute('aria-expanded', menuController.checked ? 'true' : 'false');
    });
  }

  // Close menu when clicking the overlay backdrop (outside the menu list)
  var overlay = document.getElementById('menu-wrapper');
  if (overlay) {
    overlay.addEventListener('click', function (e) {
      if (e.target === overlay) window.close_menu();
    });
  }

  // ToC active section tracking (flat .toc-list, single active tier)
  var toc = document.querySelector('.toc-list');
  if (toc) {
    var tocLinks = toc.querySelectorAll('a[href^="#"]');
    if (tocLinks.length) {
      var headings = [];
      tocLinks.forEach(function (a) {
        var id = a.getAttribute('href').slice(1);
        var h = id ? document.getElementById(id) : null;
        if (h) headings.push({ li: a.parentElement, target: h });
      });

      function updateToc() {
        var navOffset = 80; // nav-height + small breathing room
        var scrollY = window.scrollY + navOffset;
        var current = null;
        for (var i = 0; i < headings.length; i++) {
          if (headings[i].target.offsetTop <= scrollY) current = headings[i];
        }
        toc.querySelectorAll('li.active').forEach(function (el) {
          el.classList.remove('active');
        });
        if (current) current.li.classList.add('active');
      }
      // See the nav-fade listener above for why setTimeout is used instead
      // of requestAnimationFrame.
      var tocThrottled = false;
      window.addEventListener('scroll', function () {
        if (!tocThrottled) {
          tocThrottled = true;
          setTimeout(function () {
            tocThrottled = false;
            updateToc();
          }, 100);
        }
      }, { passive: true });
      updateToc();
    }
  }
})();
